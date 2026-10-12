#!/usr/bin/env python3
"""verify_canon.py -- locks the relation-yield findings of 2026-08-26.
Run from the repository root:  python3 verify_canon.py
Standard library only. Reads the sealed kernel; writes nothing."""
import sys, os, collections, hashlib, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pyref.core import TIMS, element_at, contrary, v11_beneficiary, v11_supervisee, dual_candidate, shared_characters, REININ_NAMES
from crux.typemap import perspective_cost_class as pcc
from metabolism import develop as D, packet
from metabolism.exchange import relation_of

FAILS = []
def check(name, ok):
    print("%s  %s" % ("PASS" if ok else "FAIL", name))
    if not ok: FAILS.append(name)

def seed(ags): return {h: [packet(element_at(a.st.tim, 1))] for h, a in ags.items()}
def hist(a): return tuple((x["tick"], pcc(a.st.tim, x["closed"])) for x in a.history)
def pair(t, u, T):
    ags = {"A": D.agent(t), "B": D.agent(u)}
    ags, _ = D.run(ags, seed(ags), T)
    return ags

# ---- 0. kernel manifest, as every suite does
man = json.load(open("manifests/kernel_sha256.json"))
files = man.get("files", man)
ok = all(hashlib.sha256(open(os.path.join("pyref", os.path.basename(f)), "rb").read()).hexdigest() == h
         for f, h in files.items() if isinstance(h, str)) if isinstance(files, dict) else True
check("kernel.manifest_intact", ok)

# ---- 1. relation yield table (16x16 pairs, 80 ticks)
EXPECTED = {
    "activation":          ((4, "lateral_A"), (8, "complementary"), (11, "lateral_E")),
    "supervision":         ((4, "lateral_A"), (7, "lateral_E"), (9, "complementary")),
    "duality":             ((4, "complementary"), (7, "lateral_E")),
    "kindred":             ((4, "complementary"), (6, "lateral_E")),
    "identity":            ((3, "lateral_A"),),
    "semi_duality":        ((3, "lateral_A"),),
    "super_ego":           ((68, "lateral_E"),),
    "mirror": (), "conflict": (), "benefit": (), "benefit_inverse": (),
    "business": (), "mirage": (), "quasi_identity": (), "contrary": (),
    "supervision_inverse": (),
}
res = {}
for t in TIMS:
    for u in TIMS:
        res[(t, u)] = hist(pair(t, u, 80)["A"])
byrel = collections.defaultdict(set)
for k, v in res.items(): byrel[relation_of(*k)].add(v)
check("yield.every_relation_type_invariant", all(len(s) == 1 for s in byrel.values()))
for r, exp in EXPECTED.items():
    check("yield.%s" % r, byrel[r] == {exp})
check("yield.activation_outranks_duality", len(EXPECTED["activation"]) > len(EXPECTED["duality"]))
check("yield.supervision_asymmetric", len(EXPECTED["supervision"]) == 3 and EXPECTED["supervision_inverse"] == ())
check("yield.benefit_sterile_both_ways", EXPECTED["benefit"] == () == EXPECTED["benefit_inverse"])

# ---- 2. contrary involution is a dynamical symmetry
check("symmetry.contrary_involution_exact",
      all(res[(t, u)] == res[(contrary(t), contrary(u))] for (t, u) in res))

# ---- 3. rings pair under process/result in the kernel (transcript claim)
def rings(f):
    seen, out = set(), []
    for t in TIMS:
        if t in seen: continue
        r, u = [t], f(t); seen.add(t)
        while u not in seen: r.append(u); seen.add(u); u = f(u)
        out.append(set(r))
    return out
def pr_pairs(rs):
    return sum(1 for i in range(4) for j in range(i+1, 4)
               if any(REININ_NAMES.get(w, w) == "process/result" for w in shared_characters(rs[i] | rs[j])))
check("kernel.benefit_rings_pair_under_process_result", pr_pairs(rings(v11_beneficiary)) == 2)
check("kernel.supervision_rings_pair_under_process_result", pr_pairs(rings(v11_supervisee)) == 2)

# ---- 4. canon comparisons
sup = pair("ile", v11_supervisee("ile"), 300)
check("canon.supervisee_never_closes_in_isolation_300", hist(sup["B"]) == ())
sup2 = pair("lii", v11_supervisee("lii"), 300)
check("canon.process_and_result_rings_indistinguishable", hist(sup["A"]) == hist(sup2["A"]) and hist(sup["B"]) == hist(sup2["B"]))

b = v11_beneficiary("ile")
ags = pair("ile", b, 40); bn = ags["B"]
d = dual_candidate(b)
ags2 = {"bn": bn, "d": D.agent(d)}; ags2, _ = D.run(ags2, {"d": [packet(element_at(d, 1))]}, 40)
scar = hist(ags2["bn"])
fresh = hist(pair(b, d, 40)["A"])
check("canon.benefit_then_dual_delays_to_serpent", scar[0][0] >= 64 and fresh[0][0] == 4)

ring = ["ile"]
while v11_beneficiary(ring[-1]) not in ring: ring.append(v11_beneficiary(ring[-1]))
ags = {t: D.agent(t) for t in ring}; ags, _ = D.run(ags, seed(ags), 80)
r4 = {t: hist(ags[t]) for t in ring}
check("canon.benefit_ring_of_four_reaches_altitude_3", all(len(h) == 3 for h in r4.values()))
eight = ring + [dual_candidate(t) for t in ring]
ags = {t: D.agent(t) for t in eight}; ags, _ = D.run(ags, seed(ags), 80)
check("canon.ring_plus_duals_no_better_than_ring_OPEN", all(hist(ags[t]) == r4[ring[0]] for t in eight))

# ---- 5. seat-start robustness: yield order and count do not depend on where the relay begins
from dataclasses import replace
def pair_seat(t, u, T, s):
    ags = {"A": D.agent(t), "B": D.agent(u)}
    ags["A"].st = replace(ags["A"].st, seat=s); ags["B"].st = replace(ags["B"].st, seat=s)
    ags, _ = D.run(ags, seed(ags), T); return ags
def shape(h): return tuple(c for _, c in h)
okA = okB = True
for t in TIMS:
    for s in range(1, 9):
        ags = pair_seat(t, v11_supervisee(t), 80, s)
        okA &= shape(hist(ags["A"])) == ("lateral_A", "lateral_E", "complementary")
        okB &= hist(ags["B"]) == ()
check("robust.supervisor_yield_independent_of_seat_start", okA)
check("robust.supervisee_sterile_independent_of_seat_start", okB)

# ---- 6. exposure instrument (item 10 / A33-A34): bin/exposure.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin"))
import exposure as X
g = X.sweep("gated", 0, 120)
check("exposure.gated_supervisee_still_sterile", g["supervision_inverse"] == {()} and g["benefit"] == {()} and g["benefit_inverse"] == {()})
check("exposure.gated_supervisor_still_alt3", all(len(h) == 3 for h in g["supervision"]))
check("exposure.gated_yield_still_type_invariant", all(len(v) == 1 for v in g.values()))
ags = X.run({"A": D.agent("ile"), "B": D.agent(v11_supervisee("ile"))}, seed({"A": D.agent("ile"), "B": D.agent(v11_supervisee("ile"))}), 400, "gated")
check("exposure.gated_supervisee_sterile_400", hist(ags["B"]) == ())
ags = {t: D.agent(t) for t in ring}; ags = X.run(ags, seed(ags), 120, "gated")
r4g = {t: hist(ags[t]) for t in ring}
check("exposure.gated_ring4_alt3_without_serpent", all(len(h) == 3 and h[-1][0] < 64 for h in r4g.values()))
check("exposure.gated_ring4_breaks_type_invariance", len(set(r4g.values())) > 1)
ags = {t: D.agent(t) for t in eight}; ags = X.run(ags, seed(ags), 120, "gated")
r8g = {t: hist(ags[t]) for t in eight}
check("exposure.gated_ring_plus_duals_not_faster_OPEN", max(h[-1][0] for h in r8g.values()) >= max(h[-1][0] for h in r4g.values()))
p2 = X.sweep("every_k", 2, 120)
check("exposure.periodic_k2_kills_all_non_serpent_closure", all(v <= {(), ((68, "lateral_E"),)} for v in p2.values()))

# ---- 7. stage 1: distinctions survive the completions (bin/completions.py; full 8-cell run there)
import completions as K
surv = []
for cell in ((0, 0, 0), (1, 1, 1)):
    K.set_cell(*cell); surv.append(K.cell_report(80))
K.set_cell(0, 0, 0)
for key in ("type_invariant", "contrary_symmetric", "supervisee_sterile", "act_gt_dual",
            "mirror_sterile", "benefit_sterile", "kindred_eq_dual", "scar_delays"):
    check("stage1.%s_survives_A25_A27_gate_flips" % key, all(r[key] for r in surv))
check("stage1.supervisor_alt3_survives", all(r["supervisor_alt"] == 3 for r in surv))

# ---- 8. horizon (bin/horizon.py): prediction from O is exact for one closure, then decays in timing
import horizon as Hz
hz_always = Hz.horizon(ring, Hz.ensemble(ring, "always", steps=90, n_seats=3, n_orders=2))
hz_gated  = Hz.horizon(ring, Hz.ensemble(ring, "gated",  steps=90, n_seats=3, n_orders=2))
check("horizon.regimeI_exact_all_closures", all(a == 1.0 and hi - lo <= 2 for _, a, lo, hi in hz_always))
check("horizon.regimeII_first_closure_exact", hz_gated[0][1] == 1.0 and hz_gated[0][3] - hz_gated[0][2] <= 2)
check("horizon.regimeII_timing_decays_after_first", hz_gated[2][3] - hz_gated[2][2] > hz_gated[0][3] - hz_gated[0][2])
check("horizon.regimeII_content_outlasts_timing", all(a >= 0.75 for _, a, _, _ in hz_gated))

# ---- 9. the content floor is structural, not constant (bin/floor.py)
def ringf(f, st):
    r = [st]
    while f(r[-1]) not in r: r.append(f(r[-1]))
    return r
sup_ring = ringf(v11_supervisee, "ile")
hz_sup = Hz.horizon(sup_ring, Hz.ensemble(sup_ring, "gated", steps=90, n_seats=3, n_orders=2))
check("floor.supervision_ring_content_exact_timing_free", all(a == 1.0 for _, a, _, _ in hz_sup) and hz_sup[2][3] - hz_sup[2][2] > 2)
quadra = ["ile", "sei", "ese", "lii"]
hz_q = Hz.horizon(quadra, Hz.ensemble(quadra, "gated", steps=90, n_seats=3, n_orders=2))
check("floor.quadra_content_not_exact", any(a < 1.0 for _, a, _, _ in hz_q))
check("floor.not_a_constant", hz_sup[1][1] != hz_gated[1][1] or hz_q[1][1] != hz_gated[1][1])

print("=" * 64)
print("%d checks, %d failed" % (len(FAILS) + sum(1 for _ in []), len(FAILS)) if FAILS else "all passed")
sys.exit(1 if FAILS else 0)
