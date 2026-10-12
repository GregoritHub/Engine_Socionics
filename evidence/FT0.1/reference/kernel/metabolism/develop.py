"""The development generator (Shell Geometry section 11) driven by the
metabolism.

    H_k -> movement -> W_(t+1) -> demand -> conductivity test
    C(H_k, D) empty -> minimal higher closure -> H_(k+1)

Demand from signals (A25, proposed_completion of "persistent consequences
generate demand"): a sustained signal at position p (deficit or overload
for >= window ticks) demands the perspectives addressed by p together
with any position fed this tick of the opposite rationality
(algebra.point_of).  A block addresses native or complementary; cross-
block pairs address the laterals.  Nothing here names a perspective by
hand.

Conductivity test: demand.schema.  Boundary -> tower minimal_extensions
gives the candidate H'.  The candidate is provisional until the tower's
own closure law (holon_tower.altitude.closure_admissible) is met from
metabolic observables:

  retained    kept content at every position addressing the crossed
              perspective, for >= window consecutive ticks
  returned    the estafette walk contains complement -> native
  cleared     no complex activated at the Shell's compensation carriers,
              Role and Vulnerable (section 16.1), for >= window ticks (A27)

Then altitude.close() seals it.  Altitude is counted, never assigned.

Developed hunger (section 18/19, "no longer only external pressure";
Archetypal: "the dual is not needed in the ways the God projects"): a
holon that has RETAINED the complementary perspective and holds kept
content at the suggestive does not emit a request -- it draws on what it
carries.  Infants request every tick.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from pyref.core import rationality
from crux import perspectives as P, shell as SH
from crux.typemap import type_map
from demand import schema as DS
from holon_tower import altitude as ALT
from algebra.perspective import point_of, block_perspective, reach
from .state import State, new_state
from .energy import deficit, overload
from .complex import activated
from .tick import tick as _tick, REQUEST
from . import boredom


@dataclass
class Agent:
    st: State
    org: dict
    window: int = 2
    patience: int = 1
    streak: dict = field(default_factory=dict)      # position -> sustained signal ticks
    walk: tuple = ()                                # perspective addressed by the seat, per tick
    candidate: Optional[dict] = None                # provisional H'
    crossed: Optional[str] = None
    hold: int = 0                                   # ticks retention has held
    clear: int = 0                                  # ticks since last complex at the crossed positions
    history: list = field(default_factory=list)
    serpent_ticks: list = field(default_factory=list)
    last_progress: int = 0                          # tick of last closure or candidate

    @property
    def altitude(self):
        return self.org["closures"]


def agent(tim: str, *, window=2, patience=1, generative=True) -> Agent:
    st = new_state(tim, generative)
    org = DS.ground_state(tim)
    return Agent(st=st.with_organization(org), org=org, window=window, patience=patience)


def demands_from(a: Agent) -> list:
    """Sustained signals -> demand objects."""
    st, fed = a.st, a.st.fed_this_tick()
    hot = set(deficit(st, a.patience)) | set(overload(st))
    streak = {p: (a.streak.get(p, 0) + 1) for p in hot}
    a.streak = streak
    out = []
    if st.serpent:
        # "paradoxes that have no solution within the framework the ego has
        # established": the Serpent's demand is exactly the gap, and pure.
        gap = set(P.PERSPECTIVES) - a.org["retained"]
        if gap:
            out.append(DS.demand("serpent", gap, window=1))
    for p, n in streak.items():
        if n < a.window:
            continue
        ap = st.at(p).aspect
        pairs = {point_of(ap, st.at(q).aspect) for q in fed if q != p
                 and rationality(st.at(q).aspect) != rationality(ap)}
        # the ACTIVE pair addresses the point; only a lone signal falls
        # back to its own block's perspective
        dests = pairs or {block_perspective(st.tim, p)}
        out.append(DS.demand("sig_%d" % p, dests, window=a.window))
    return out


def positions_of(tim: str, perspective: str):
    return reach(tim, perspective)


def step(a: Agent, inbox) -> tuple:
    """One developmental tick.  Returns (agent, outbox, report)."""
    # a candidate never closed is a visit, not retention (section 8): it lapses
    if a.candidate is not None and a.st.ticks - a.last_progress >= boredom.BORED_WINDOW:
        a.candidate = a.crossed = None
        a.last_progress = a.st.ticks
    unsolved = bool(set(P.PERSPECTIVES) - a.org["retained"])
    if unsolved and boredom.bored(a.st.tim, a.walk, a.st.ticks - a.last_progress, a.candidate is not None):
        a.st = boredom.serpent(a.st)
        a.serpent_ticks.append(a.st.ticks + 1)
    st, out, rep = _tick(a.st, inbox, holon_id=a.st.tim, patience=a.patience)
    if a.serpent_ticks and a.serpent_ticks[-1] == st.ticks:
        rep["serpent"] = True
    # developed hunger: retained complement + kept suggestive -> no request
    comp = type_map(st.tim)["complementary_perspective"]
    if comp in a.org["retained"] and st.at(5).kept:
        out = [p for p in out if p.tag != REQUEST]
        rep["hungry"] = False
    a.st = st
    a.walk = (a.walk + (block_perspective(st.tim, st.seat),))[-boredom.BORED_WINDOW:]
    rep["altitude"] = a.altitude
    rep["retained"] = sorted(a.org["retained"])
    # ---- demand -> conductivity -> candidate
    for dem in demands_from(a):
        if not DS.is_developmental_boundary(a.org, dem):
            rep.setdefault("adapted", []).append(sorted(dem["requires_destination"]))
            continue
        exts = ALT.minimal_extensions(a.org, dem)
        if exts and a.candidate is None:
            a.candidate = exts[0]
            a.crossed = sorted(a.candidate["retained"] - a.org["retained"])[0]
            a.hold = a.clear = 0
            a.last_progress = st.ticks
            rep["boundary"] = a.crossed
    # ---- closure test on the candidate
    if a.candidate is not None:
        pos = positions_of(st.tim, a.crossed)
        held = all(st.at(p).kept for p in pos if st.at(p).valued) and any(st.at(p).kept for p in pos)
        a.hold = a.hold + 1 if held else 0
        hot = {c["position"] for c in activated(st, a.window)}
        a.clear = 0 if hot & {3, 4} else a.clear + 1
        rep["closing"] = {"crossed": a.crossed, "hold": a.hold, "clear": a.clear}
        if a.hold >= a.window and a.clear >= a.window:
            trial = DS.organization(st.tim, retained=a.candidate["retained"],
                                    dwelling=a.org["dwelling"], closures=a.org["closures"])
            ok, why = ALT.closure_admissible(trial, crossed=a.crossed, walk=a.walk,
                                             shell_before=SH.coherent_shell(),
                                             shell_after=SH.coherent_shell())
            if ok:
                a.org = ALT.close(trial, crossed=a.crossed, walk=a.walk,
                                  shell_before=SH.coherent_shell(), shell_after=SH.coherent_shell())
                a.st = a.st.with_organization(a.org)
                rep["closed"] = a.crossed
                a.last_progress = st.ticks
                a.history.append({"tick": st.ticks, "closed": a.crossed, "altitude": a.altitude})
                a.candidate = a.crossed = None
            else:
                rep["closure_refused"] = why
    return a, out, rep


def run(agents: dict, world_inbox: dict, steps: int, *, deliver=None):
    inbox = {h: list(world_inbox.get(h, [])) for h in agents}
    history = []
    for _ in range(steps):
        nxt = {h: [] for h in agents}
        for h, a in agents.items():
            a, out, rep = step(a, inbox[h])
            agents[h] = a
            history.append(dict(rep, holon=h))
            for pk in out:
                for t in (deliver(h, pk) if deliver else [o for o in agents if o != h]):
                    nxt[t].append(pk)
        inbox = nxt
    return agents, history
