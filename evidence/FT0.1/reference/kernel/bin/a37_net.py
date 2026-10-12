#!/usr/bin/env python3
"""A37 research net.  usage: python3 bin/a37_net.py family|grid|balance|analyze [outdir]

  family    yield table (representative pairs) under each rule in a37_rules.RULES,
            default instruments.  Which reading moves which row.
  grid      every_tick vs relay across every instrument/completion flip the repo
            already exposes: A23 gate x patience x window x {A25,A27,chord-gate}
            x delivery {always,gated} x BORED_WINDOW {64,32}.  256 cells x 2.
  balance   the pure-finding table (bin/balance.py machinery) under each rule x gate.
  analyze   read the JSONL and print the robustness classification.

Nothing in the packages is modified; every flip is a monkeypatch in this file
or in a37_rules / completions / relay_gate, restored afterwards.  Kernel untouched.
"""
import os, sys, json, itertools, collections, time
_d = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, _d); sys.path.insert(0, os.path.dirname(_d))
import a37_rules as R
import completions as CP
import relay_gate
from pyref.core import TIMS, element_at, contrary
from crux.typemap import perspective_cost_class as pcc
from metabolism import develop as D, packet, boredom, clock
from metabolism.exchange import relation_of

OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.dirname(_d)), "out")
os.makedirs(OUT, exist_ok=True)
BASES = ("ile", "esi")            # two bases; type-invariance is re-checked per cell on them

def hist(a): return [(x["tick"], pcc(a.st.tim, x["closed"])) for x in a.history]
def seed(ags): return {h: [packet(element_at(a.st.tim, 1))] for h, a in ags.items()}

def run_pair(t, u, steps, patience, window, delivery):
    ags = {"A": D.agent(t, window=window, patience=patience), "B": D.agent(u, window=window, patience=patience)}
    inbox = seed(ags)
    for k in range(1, steps + 1):
        nxt = {h: [] for h in ags}
        for h, a in ags.items():
            a, out, rep = D.step(a, inbox[h]); ags[h] = a
            for pk in out:
                for o in ags:
                    if o == h: continue
                    if delivery == "gated" and any(q.hit for q in ags[o].st.positions): continue
                    nxt[o].append(pk)
        inbox = nxt
    return ags

def yield_table(steps=120, patience=1, window=2, delivery="always", bases=BASES):
    byrel = collections.defaultdict(set)
    for b in bases:
        for u in TIMS:
            byrel[relation_of(b, u)].add(tuple(hist(run_pair(b, u, steps, patience, window, delivery)["A"])))
    return {r: sorted(v) for r, v in byrel.items()}

# ---- BORED_WINDOW flip (default arg of bored() binds at definition time) ------
_orig_bored = boredom.bored
def set_bored(w):
    boredom.BORED_WINDOW = w
    boredom.bored = (lambda tim, walk, t, working, window=None: _orig_bored(tim, walk, t, working, window=w))
def restore_bored():
    boredom.BORED_WINDOW = 64; boredom.bored = _orig_bored

def set_gate(on):
    if on: relay_gate.install()
    else:  clock.step = _orig_clock_step
_orig_clock_step = clock.step

# ------------------------------------------------------------------------------
def family():
    rows = {}
    for rule in R.RULES:
        R.use(rule); t0 = time.time()
        rows[rule] = yield_table()
        print("%-13s %.1fs" % (rule, time.time() - t0), flush=True)
    R.use(None)
    json.dump(rows, open(os.path.join(OUT, "family.json"), "w"), indent=1)
    rels = sorted(rows["every_tick"])
    print("\n%-20s" % "relation" + "".join("%-46s" % r for r in R.RULES))
    for rel in rels:
        print("%-20s" % rel + "".join("%-46s" % (str(rows[r][rel][0]) if len(rows[r][rel]) == 1 else "VARIANT") for r in R.RULES))

def grid():
    """grid [outdir] [start end]: cells start..end-1 appended to grid.jsonl (chunked runs)."""
    path = os.path.join(OUT, "grid.jsonl")
    cells = list(itertools.product((0, 1), (1, 2), (2, 3), (0, 1), (0, 1), (0, 1), ("always", "gated"), (64, 32)))
    lo, hi = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, len(cells))
    f = open(path, "a" if lo else "w")
    print("cells: %d  running %d..%d" % (len(cells), lo, hi), flush=True); t0 = time.time()
    for i, (gate, pat, win, a25, a27, cgate, deliv, bored) in enumerate(cells[lo:hi], lo + 1):
        set_gate(gate); CP.set_cell(a25, a27, cgate); set_bored(bored)
        rec = {"gate": gate, "patience": pat, "window": win, "A25_exposure": a25, "A27_off": a27,
               "chord_open": cgate, "delivery": deliv, "bored": bored}
        for pol in ("every_tick", "relay"):
            R.use(pol)
            rec[pol] = yield_table(steps=120, patience=pat, window=win, delivery=deliv, bases=("ile",))
        rec["cell_index"] = i
        f.write(json.dumps(rec) + "\n"); f.flush()
        if i % 16 == 0: print("  %d/%d  %.0fs" % (i, len(cells), time.time() - t0), flush=True)
    R.use(None); set_gate(0); CP.set_cell(0, 0, 0); restore_bored()
    f.close(); print("wrote", path)

def balance():
    import balance as B, movement as M
    res = []
    for rule in R.RULES:
        for gate in (0, 1):
            set_gate(gate); R.use(rule); t0 = time.time()
            agg = collections.defaultdict(collections.Counter); seat = collections.defaultdict(collections.Counter)
            reached = collections.Counter(); held_total = 0
            for name, g in B.GROUPS.items():
                runs = M.ensemble(g, steps=200, n_seats=8, all_orders=False, policy="always", world="seat",
                                  sync=True, calling=True, polarity=True, use_reach=True)
                for r in runs:
                    for h in g:
                        m = r[h]; reached[m.a.altitude] += 1
                        for alt, c in m.pol_by_alt.items():
                            for k, n in c.items(): agg[alt][k] += n
                        for alt, c in m.seat_by_alt.items():
                            for k, n in c.items(): seat[alt][k] += n
            row = {"rule": rule, "gate": gate, "final_altitudes": dict(sorted(reached.items())), "alts": {}}
            for alt in sorted(agg):
                c = agg[alt]; ae = c[("accepting", True)]; ee = c[("producing", True)]
                ai = c[("accepting", False)]; ei = c[("producing", False)]; tot = ae + ee + ai + ei
                ss = seat[alt]; tt = max(1, sum(ss.values()))
                row["alts"][alt] = {"moves": tot, "balance": round(abs(ae - ee) / max(1, ae + ee), 3),
                                    "idle": round((ai + ei) / max(1, tot), 3),
                                    "valued_share": round(sum(ss[q] for q in (1, 5, 6, 2)) / tt, 3),
                                    "seat_share": {q: round(ss[q] / tt, 3) for q in sorted(ss)}}
            res.append(row)
            a3 = row["alts"].get(3, {}); a2 = row["alts"].get(2, {})
            print("%-13s gate=%d  alt3 bal %.3f idle %.3f valued %.3f | alt2 bal %.3f idle %.3f | reached %s  (%.0fs)" % (
                rule, gate, a3.get("balance", -1), a3.get("idle", -1), a3.get("valued_share", -1),
                a2.get("balance", -1), a2.get("idle", -1), row["final_altitudes"], time.time() - t0), flush=True)
    R.use(None); set_gate(0)
    json.dump(res, open(os.path.join(OUT, "balance.json"), "w"), indent=1)

def analyze():
    recs = [json.loads(l) for l in open(os.path.join(OUT, "grid.jsonl"))]
    rels = sorted(recs[0]["every_tick"])
    print("cells:", len(recs))
    inv = {pol: sum(all(len(r[pol][rel]) == 1 for rel in rels) for r in recs) for pol in ("every_tick", "relay")}
    print("cells with one sequence per relation:", inv, "(grid runs a single base; see invariance_spotcheck.json)")
    def first(h): return h[0][1] if h else "sterile"
    def shape(h): return tuple(c for _, c in h)
    print("\n%-20s %-10s %-10s %-10s  %s" % ("relation", "seq!=", "first!=", "sterile!=", "note"))
    summary = {}
    for rel in rels:
        seq = firstc = ster = 0; pat = collections.Counter()
        for r in recs:
            e = r["every_tick"][rel][0]; l = r["relay"][rel][0]
            seq += shape(e) != shape(l); firstc += first(e) != first(l); ster += (bool(e) != bool(l))
            pat[(first(e), first(l))] += 1
        summary[rel] = {"seq": seq, "first": firstc, "sterile": ster, "patterns": dict((str(k), v) for k, v in pat.items())}
        top = ", ".join("%s->%s x%d" % (k[0], k[1], v) for k, v in pat.most_common(3))
        print("%-20s %4d/%-5d %4d/%-5d %4d/%-5d  %s" % (rel, seq, len(recs), firstc, len(recs), ster, len(recs), top))
    # the named discriminators, per cell
    sup_relay_comp_first = sum(first(r["relay"]["supervision"][0]) == "complementary" for r in recs)
    sup_et_lat_first = sum(first(r["every_tick"]["supervision"][0]).startswith("lateral") for r in recs)
    sup_relay_lat_last = sum((r["relay"]["supervision"][0] and r["relay"]["supervision"][0][-1][1] == "lateral_A") for r in recs)
    semi_et_closes = sum(bool(r["every_tick"]["semi_duality"][0]) for r in recs)
    semi_relay_sterile = sum(not r["relay"]["semi_duality"][0] for r in recs)
    print("\nsupervisor complement-first under relay: %d/%d ; lateral-first under every_tick: %d/%d ; relay lateral_A last: %d/%d"
          % (sup_relay_comp_first, len(recs), sup_et_lat_first, len(recs), sup_relay_lat_last, len(recs)))
    print("semi-dual closes under every_tick: %d/%d ; sterile under relay: %d/%d" % (semi_et_closes, len(recs), semi_relay_sterile, len(recs)))
    # which flips break which discriminator
    print("\ncells where the supervisor discriminator FAILS (relay not complement-first or every_tick not lateral-first):")
    bad = [r for r in recs if not (first(r["relay"]["supervision"][0]) == "complementary" and first(r["every_tick"]["supervision"][0]).startswith("lateral"))]
    keys = ["gate", "patience", "window", "A25_exposure", "A27_off", "chord_open", "delivery", "bored"]
    for k in keys:
        c = collections.Counter(r[k] for r in bad); tot = collections.Counter(r[k] for r in recs)
        print("  %-13s %s" % (k, {v: "%d/%d" % (c[v], tot[v]) for v in sorted(tot)}))
    print("\ncells where the semi-dual discriminator FAILS:")
    bad2 = [r for r in recs if not (bool(r["every_tick"]["semi_duality"][0]) and not r["relay"]["semi_duality"][0])]
    for k in keys:
        c = collections.Counter(r[k] for r in bad2); tot = collections.Counter(r[k] for r in recs)
        print("  %-13s %s" % (k, {v: "%d/%d" % (c[v], tot[v]) for v in sorted(tot)}))
    json.dump(summary, open(os.path.join(OUT, "grid_summary.json"), "w"), indent=1)



def lock():
    """Emit the C28-style prediction table from the grid: per instrument setting
    (patience, window, delivery), per policy, per relation -> ordinal closure-class
    sequence, with a completion-independence flag (constant over the 32 cells of
    gate x A25 x A27 x chord-gate x BORED_WINDOW).  Hashed; ticks are dropped
    (they are not clock time), only ORDER is locked."""
    import hashlib
    recs = [json.loads(l) for l in open(os.path.join(OUT, "grid.jsonl"))]
    rels = sorted(recs[0]["every_tick"])
    shape = lambda h: [c for _, c in h]
    table = {"kind": "a37_prediction_table", "engine": "HolonicLivingEngine 5.2 canon",
             "locks": "ordinal closure-class sequence of holon A in pair(A, B), Regime I seed (leading aspect, tick 1), 120 ticks",
             "instruments_locked": ["patience", "window", "delivery"],
             "completion_flips_marginalised": ["A23 gate", "A25 exposure", "A27 off", "chord gate open", "BORED_WINDOW 64/32"],
             "settings": {}}
    for pat in (1, 2):
        for win in (2, 3):
            for dl in ("always", "gated"):
                key = "patience=%d,window=%d,delivery=%s" % (pat, win, dl)
                cs = [r for r in recs if r["patience"] == pat and r["window"] == win and r["delivery"] == dl]
                ent = {}
                for pol in ("every_tick", "relay"):
                    ent[pol] = {}
                    for rel in rels:
                        shapes = collections.Counter(tuple(shape(r[pol][rel][0])) for r in cs)
                        ent[pol][rel] = {"sequence": list(shapes.most_common(1)[0][0]),
                                         "completion_independent": len(shapes) == 1,
                                         "variants": [list(k) for k in shapes] if len(shapes) > 1 else None}
                table["settings"][key] = ent
    body = json.dumps(table, sort_keys=True, separators=(",", ":"))
    h = hashlib.sha256(body.encode()).hexdigest()
    table["sha256_of_body"] = h
    json.dump(table, open(os.path.join(OUT, "a37_prediction_table.json"), "w"), indent=1, sort_keys=True)
    print("a37_prediction_table.json  sha256(body) =", h)
    # decision matrix on the two decisive rows
    print("\njoint first-closure outcome (activation, supervision) -> consistent (policy, setting):")
    out = collections.defaultdict(list)
    for key, ent in table["settings"].items():
        for pol in ("every_tick", "relay"):
            a = ent[pol]["activation"]["sequence"]; s = ent[pol]["supervision"]["sequence"]
            out[(a[0] if a else "sterile", s[0] if s else "sterile")].append("%s @ %s" % (pol, key))
    for k, v in sorted(out.items()):
        pols = {x.split(" @ ")[0] for x in v}
        print("  %-30s -> %s%s" % (k, "; ".join(v), "   [DECISIVE: %s]" % pols.pop() if len(pols) == 1 else "   [AMBIGUOUS]"))
    return h


if __name__ == "__main__":
    {"family": family, "grid": grid, "balance": balance, "analyze": analyze, "lock": lock}[sys.argv[1]]()
