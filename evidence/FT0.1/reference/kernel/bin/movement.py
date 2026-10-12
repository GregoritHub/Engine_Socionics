#!/usr/bin/env python3
"""Per-holon movement (A36 follow-up).  Nothing in the package is modified;
this is a loop over develop.step with three switchable layers.

  sync      deliveries are resolved at the END of a world step, reading each
            receiver's state once (removes the within-tick step-order read)
  calling   a holon moves only when something calls it: inbox, pending,
            charge, live candidate, serpent, or hunger (accepting position
            unfed >= patience; with `reach`, an idle producing position in
            the reach of a retained perspective).  Otherwise it rests: its
            unfed/idle counters age, nothing else happens.
  polarity  the seat forces the movement's polarity (ACCESS mode of the seat):
            accumulation = receive, do not fire (fresh output is HELD);
            expenditure  = release held + fresh output, do not receive
            (inbox is carried).  Requests are expenditure.
  reach     altitude-widened hunger: producing positions in reach(retained)
            that have not fired for >= patience movements count as deficit.

Gate under sync: a packet is withheld while the receiver holds an
unmetabolised hit, i.e. its last movement was hit and it has not moved since.

V5.2 correction: the seat that forces a movement's polarity (and that the
world feeds) is the seat the relay ADVANCES TO in that movement -- the one
tick() itself works at -- not the seat left behind.  The V5.1 version read
the pre-advance seat, one position behind the engine; the per-seat tables
in NOTE_V5_1's balance addendum were shifted by one position.
"""
import os, sys, collections, itertools
from dataclasses import replace
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pyref.core import element_at, ACCESS
from crux.typemap import perspective_cost_class as pcc
from metabolism import develop as D, packet, energy, clock
from metabolism.tick import REQUEST
from algebra.perspective import reach

FIRING = (1, 2, 8)
_CTX = {"idle": None, "patience": 1, "reach": False}


def _deficit(st, patience):
    base = energy.deficit(st, patience)
    if not _CTX["reach"] or _CTX["idle"] is None:
        return base
    hungry_prod = set()
    for p in st.retained:
        for q in reach(st.tim, p):
            if ACCESS[q]["mode"] == "producing" and q in FIRING and _CTX["idle"].get(q, 0) >= patience:
                hungry_prod.add(q)
    return frozenset(set(base) | hungry_prod)


D.deficit = _deficit          # develop imported the name; energy.signals is untouched


class Mover:
    def __init__(self, tim, seat=1, patience=1):
        self.a = D.agent(tim, patience=patience)
        self.a.st = replace(self.a.st, seat=seat)
        self.tim = tim; self.inbox = []; self.held = []
        self.idle = {q: 0 for q in FIRING}
        self.moves = 0; self.rests = 0
        self.pol = collections.Counter()      # (polarity, effective) -> count
        self.pol_by_alt = collections.defaultdict(collections.Counter)
        self.closed_on_hit = False            # gate flag under sync
        self.seat_by_alt = collections.defaultdict(collections.Counter)
        self.seat_eff = collections.defaultdict(collections.Counter)  # (seat, effective)

    def called(self, patience, use_reach):
        st = self.a.st
        if self.inbox or st.pending or self.a.candidate is not None or st.serpent:
            return True
        if any(q.charge for q in st.positions):
            return True
        _CTX["idle"] = self.idle; _CTX["reach"] = use_reach
        return bool(_deficit(st, patience))

    def rest(self):
        st = self.a.st
        self.a.st = replace(st, positions=tuple(replace(q, unfed=q.unfed + 1) for q in st.positions))
        for q in self.idle: self.idle[q] += 1
        self.rests += 1

    def move(self, polarity_forced, use_reach, patience):
        _CTX["idle"] = self.idle; _CTX["reach"] = use_reach
        seat_mode = ACCESS[clock.step(self.a.st).seat]["mode"]   # the seat this movement is made AT (post-advance)
        pol = seat_mode if polarity_forced else "both"
        take = self.inbox if pol in ("accepting", "both") else []
        if pol in ("accepting", "both"): self.inbox = []
        self.a, out, rep = D.step(self.a, take)
        fired = {q for q in FIRING if any(e[0] == "produced" and e[2] == q for e in self.a.st.log[self.a.st.tick_mark:])}
        for q in self.idle: self.idle[q] = 0 if q in fired else self.idle[q] + 1
        release = []
        if pol == "producing":
            release = self.held + out; self.held = []
        elif pol == "accepting":
            self.held += out
        else:
            release = out
        effective = bool(take) if pol == "accepting" else bool(release) if pol == "producing" else bool(take or release)
        self.pol[(pol, effective)] += 1
        self.seat_by_alt[self.a.altitude][self.a.st.seat] += 1
        self.seat_eff[self.a.altitude][(self.a.st.seat, effective)] += 1
        self.pol_by_alt[self.a.altitude][(pol, effective)] += 1
        self.moves += 1
        self.closed_on_hit = any(q.hit for q in self.a.st.positions)
        return release, rep


def run(group, seats, order, steps, *, policy="gated", sync=True, calling=True,
        polarity=True, use_reach=True, patience=1, world=None):
    """world: None (seed only), "seat" (each step a full-facet world packet on the
    aspect at the mover's seat, if that position is accepting), "leading" (on the
    leading aspect every step).  World packets are not gated."""
    movers = {t: Mover(t, s, patience) for t, s in zip(group, seats)}
    for m in movers.values(): m.inbox = [packet(element_at(m.tim, 1))]
    for t in range(1, steps + 1):
        nxt = {h: [] for h in movers}
        if world:
            for m in movers.values():
                if t == 1: continue
                if world == "leading":
                    m.inbox.append(packet(element_at(m.tim, 1)))
                elif world == "seat":
                    q = clock.step(m.a.st).seat
                    if ACCESS[q]["mode"] == "accepting":
                        m.inbox.append(packet(m.a.st.at(q).aspect))
        for h in order:
            m = movers[h]
            if calling and not m.called(patience, use_reach):
                m.rest(); continue
            rel, rep = m.move(polarity, use_reach, patience)
            for pk in rel:
                for o in movers:
                    if o == h: continue
                    if policy == "gated":
                        if sync:
                            nxt[o].append((h, pk)); continue   # resolve at end of step
                        if any(q.hit for q in movers[o].a.st.positions): continue
                    nxt[o].append((h, pk))
        for o, lst in nxt.items():
            for h, pk in lst:
                if policy == "gated" and sync and movers[o].closed_on_hit: continue
                movers[o].inbox.append(pk)
    _CTX["idle"] = None; _CTX["reach"] = False      # leave develop.deficit as energy.deficit for other callers
    return movers


def closures(m):
    return [(x["tick"], pcc(m.tim, x["closed"])) for x in m.a.history]


def ensemble(group, steps=90, n_seats=8, all_orders=True, **kw):
    n = len(group)
    seats = [tuple(((i * 3 + j * 5 + 1) % 8) + 1 for j in range(n)) for i in range(n_seats)]
    orders = list(itertools.permutations(range(n)))
    if not all_orders: orders = orders[::max(1, len(orders) // 2)]
    out = []
    for s in seats:
        for od in orders:
            mv = run(group, s, [group[i] for i in od], steps, **kw)
            out.append(mv)
    return out


def score(group, runs, kmax=3):
    rows = []
    for k in range(kmax):
        agree, ticks, reached = [], [], 0
        for h in group:
            c = collections.Counter(closures(r[h])[k][1] for r in runs if len(closures(r[h])) > k)
            if c: agree.append(c.most_common(1)[0][1] / sum(c.values())); reached += 1
            ticks += [closures(r[h])[k][0] for r in runs if len(closures(r[h])) > k]
        rows.append((k + 1, (sum(agree) / len(agree)) if agree else None, min(agree) if agree else None,
                     (min(ticks), max(ticks)) if ticks else None, reached))
    return rows
