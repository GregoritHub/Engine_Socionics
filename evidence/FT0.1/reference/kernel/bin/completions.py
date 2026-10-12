#!/usr/bin/env python3
"""Stage 1: which distinctions survive every plausible completion?
Flips three proposed_completion rules by monkeypatch (packages untouched):
  A25  streak counts TICKS (reset on gap)   | counts EXPOSURES (no reset)
  A27  clearance at 3/4 required            | not required
  gate return chord gated on retention      | always open
Runs the 16x16 yield sweep and the benefit-scar test under all 8 cells."""
import os, sys, collections, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pyref.core import TIMS, element_at, contrary, v11_beneficiary, dual_candidate
from crux.typemap import perspective_cost_class as pcc
from metabolism import develop as D, chord as C, packet
from metabolism.exchange import relation_of
from demand import schema as DS
from algebra.perspective import point_of, block_perspective
from pyref.core import rationality
from crux import perspectives as P

_orig = dict(demands=D.demands_from, activated=D.activated, is_open=C.is_open)

def demands_exposure(a):
    st, fed = a.st, a.st.fed_this_tick()
    hot = set(D.deficit(st, a.patience)) | set(D.overload(st))
    streak = dict(a.streak)
    for p in hot: streak[p] = streak.get(p, 0) + 1     # never resets
    a.streak = streak
    out = []
    if st.serpent:
        gap = set(P.PERSPECTIVES) - a.org["retained"]
        if gap: out.append(DS.demand("serpent", gap, window=1))
    for p, n in streak.items():
        if n < a.window or p not in hot: continue
        ap = st.at(p).aspect
        pairs = {point_of(ap, st.at(q).aspect) for q in fed if q != p
                 and rationality(st.at(q).aspect) != rationality(ap)}
        out.append(DS.demand("sig_%d" % p, pairs or {block_perspective(st.tim, p)}, window=a.window))
    return out

def set_cell(a25_exposure, a27_off, gate_open):
    D.demands_from = demands_exposure if a25_exposure else _orig["demands"]
    D.activated = (lambda st, w=2: []) if a27_off else _orig["activated"]
    C.is_open = (lambda st: True) if gate_open else _orig["is_open"]

def hist(a): return tuple((x["tick"], pcc(a.st.tim, x["closed"])) for x in a.history)
def seed(ags): return {h: [packet(element_at(a.st.tim, 1))] for h, a in ags.items()}
def pair(t, u, T):
    ags = {"A": D.agent(t), "B": D.agent(u)}; ags, _ = D.run(ags, seed(ags), T); return ags

def shape(h): return tuple(c for _, c in h)

def cell_report(T=80):
    byrel = collections.defaultdict(set); res = {}
    for t in TIMS:
        for u in TIMS:
            res[(t, u)] = hist(pair(t, u, T)["A"]); byrel[relation_of(t, u)].add(res[(t, u)])
    b = v11_beneficiary("ile"); d = dual_candidate(b)
    ags = pair("ile", b, 40); ags2 = {"bn": ags["B"], "d": D.agent(d)}
    ags2, _ = D.run(ags2, {"d": [packet(element_at(d, 1))]}, 40)
    scar = hist(ags2["bn"]); fresh = hist(pair(b, d, 40)["A"])
    return {
        "type_invariant": all(len(v) == 1 for v in byrel.values()),
        "contrary_symmetric": all(res[(t, u)] == res[(contrary(t), contrary(u))] for (t, u) in res),
        "supervisee_sterile": byrel["supervision_inverse"] == {()},
        "supervisor_alt": max(len(h) for h in byrel["supervision"]),
        "activation_alt": max(len(h) for h in byrel["activation"]),
        "duality_alt": max(len(h) for h in byrel["duality"]),
        "act_gt_dual": max(len(h) for h in byrel["activation"]) > max(len(h) for h in byrel["duality"]),
        "mirror_sterile": byrel["mirror"] == {()},
        "benefit_sterile": byrel["benefit"] == {()} and byrel["benefit_inverse"] == {()},
        "kindred_eq_dual": {shape(h) for h in byrel["kindred"]} == {shape(h) for h in byrel["duality"]},
        "scar_delays": (scar[0][0] if scar else 999) > (fresh[0][0] if fresh else 999),
        "n_sterile": sum(1 for r, v in byrel.items() if v == {()}),
    }

if __name__ == "__main__":
    rows = []
    for a25, a27, gate in itertools.product((0, 1), (0, 1), (0, 1)):
        set_cell(a25, a27, gate)
        r = cell_report(); r["cell"] = "A25=%s A27=%s gate=%s" % ("exp" if a25 else "tick", "off" if a27 else "on", "open" if gate else "gated")
        rows.append(r); print(r["cell"], {k: v for k, v in r.items() if k != "cell"}, flush=True)
    set_cell(0, 0, 0)
    keys = [k for k in rows[0] if k != "cell"]
    print("\nSURVIVES ALL 8 CELLS:")
    for k in keys:
        vals = {r[k] for r in rows}
        print("  %-20s %s" % (k, "yes: %s" % vals.pop() if len(vals) == 1 else "NO  %s" % sorted(map(str, vals))))
