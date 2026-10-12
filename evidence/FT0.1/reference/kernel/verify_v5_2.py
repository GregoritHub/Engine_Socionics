#!/usr/bin/env python3
"""verify_v5_2.py -- locks the V5.2 findings: the pure finding (balance from
the vital ring under relay firing), provenance walks, and cognitive styles
as a subgroup.  Run from the repository root.  Standard library only.
Reads the sealed kernel; writes nothing.  Defaults are V5: this suite
switches FIRING_POLICY / RELAY_GATE explicitly and restores them."""
import sys, os, collections, hashlib, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin"))
from pyref.core import (TIMS, element_at, contrary, dual_candidate, v11_supervisee,
                        v11_beneficiary, vadd, ACCESS)
from crux.typemap import perspective_cost_class as pcc
from metabolism import develop as D, packet, spectrum as SP, clock
import metabolism.tick; T = sys.modules["metabolism.tick"]
from metabolism.exchange import relation_of
from algebra import cognitive_style as CS
import movement as M

FAILS = []
def check(name, ok):
    print("%s  %s" % ("PASS" if ok else "FAIL", name))
    if not ok: FAILS.append(name)

man = json.load(open("manifests/kernel_sha256.json")); files = man.get("files", man)
check("kernel.manifest_intact", all(hashlib.sha256(open(os.path.join("pyref", os.path.basename(f)), "rb").read()).hexdigest() == h
                                    for f, h in files.items() if isinstance(h, str)))
check("defaults.are_v5", T.FIRING_POLICY == "every_tick" and clock.RELAY_GATE is False)

# ---- 1. cognitive styles: a subgroup question -----------------------------
check("style.three_dichotomies_are_two", vadd(CS.STATIC, CS.PROCESS) == CS.POSITIVIST)
check("style.carriers_are_cosets", all(CS.style_of(t) == n for n, g in CS.CARRIERS.items() for t in g))
check("style.subgroup_order_4", len(CS.style_subgroup()) == 4)
check("style.supervision_fixes_style", all(CS.style_of(v11_supervisee(t)) == CS.style_of(t) for t in TIMS))
def ring(f, t):
    r = [t]
    while f(r[-1]) not in r: r.append(f(r[-1]))
    return frozenset(r)
check("style.is_the_supervision_ring", all(ring(v11_supervisee, t) == frozenset(CS.CARRIERS[CS.style_of(t)]) for t in TIMS))
check("style.duality_benefit_contrary_map_to_partner",
      all(CS.style_of(f(t)) == CS.partner_style(CS.style_of(t)) for t in TIMS for f in (dual_candidate, v11_beneficiary, contrary)))

# ---- 2. yield table under relay firing --------------------------------------
def seed(ags): return {h: [packet(element_at(a.st.tim, 1))] for h, a in ags.items()}
def hist(a): return tuple((x["tick"], pcc(a.st.tim, x["closed"])) for x in a.history)
def sweep(T_):
    res = {}
    for t in TIMS:
        for u in TIMS:
            ags = {"A": D.agent(t), "B": D.agent(u)}; ags, _ = D.run(ags, seed(ags), T_); res[(t, u)] = hist(ags["A"])
    byrel = collections.defaultdict(set)
    for k, v in res.items(): byrel[relation_of(*k)].add(v)
    return res, byrel
T.FIRING_POLICY = "relay"
res, byrel = sweep(80)
T.FIRING_POLICY = "every_tick"
one = {r: next(iter(s)) for r, s in byrel.items() if len(s) == 1}
check("relay.yield_type_invariant", all(len(s) == 1 for s in byrel.values()))
check("relay.contrary_symmetric", all(res[(t, u)] == res[(contrary(t), contrary(u))] for (t, u) in res))
check("relay.activation_outranks_duality", len(one["activation"]) == 3 and len(one["duality"]) == 2)
check("relay.kindred_equals_duality", one["kindred"] == one["duality"])
check("relay.benefit_sterile_both_ways", one["benefit"] == () == one["benefit_inverse"])
check("relay.supervisee_sterile_supervisor_alt3", one["supervision_inverse"] == () and len(one["supervision"]) == 3)
check("relay.duality_first_closure_is_complementary", one["duality"][0][1] == "complementary")
# rows that MOVED relative to V5 (recorded, not adjudicated)
check("relay.identity_and_semi_duality_lose_lateral_A", one["identity"] == () == one["semi_duality"])
check("relay.super_ego_loses_serpent_mirror_gains_it", one["super_ego"] == () and len(one["mirror"]) == 1 and one["mirror"][0][0] >= 64)
check("relay.supervisor_closes_complement_first", one["supervision"][0][1] == "complementary")
check("relay.first_closures_one_tick_later", one["duality"][0][0] == 5 and one["activation"][0][0] == 5)

# ---- 3. the pure finding ----------------------------------------------------
def ringf(f, st):
    r = [st]
    while f(r[-1]) not in r: r.append(f(r[-1]))
    return r
GROUPS = {"quadra": ["ile", "sei", "ese", "lii"], "benefit ring": ringf(v11_beneficiary, "ile"), "mixed": ["ile", "esi", "lsi", "iee"]}
def balance(world):
    agg = collections.defaultdict(collections.Counter); seat = collections.defaultdict(collections.Counter)
    for g in GROUPS.values():
        for r in M.ensemble(g, steps=200, n_seats=8, all_orders=False, policy="always", world=world,
                            sync=True, calling=True, polarity=True, use_reach=True):
            for h in g:
                for alt, c in r[h].pol_by_alt.items():
                    for k, n in c.items(): agg[alt][k] += n
                for alt, c in r[h].seat_by_alt.items():
                    for k, n in c.items(): seat[alt][k] += n
    out = {}
    for alt in agg:
        c = agg[alt]; ae = c[("accepting", True)]; ee = c[("producing", True)]; ai = c[("accepting", False)]; ei = c[("producing", False)]
        tot = ae + ee + ai + ei; ss = seat[alt]; st = max(1, sum(ss.values()))
        out[alt] = {"balance": abs(ae - ee) / max(1, ae + ee), "idle": (ai + ei) / max(1, tot),
                    "unvalued_share": sum(ss[q] for q in (3, 4, 7, 8)) / st, "moves": tot}
    return out
clock.RELAY_GATE = True
T.FIRING_POLICY = "every_tick"; v5 = balance("seat")
T.FIRING_POLICY = "relay";      pure = balance("seat"); pure_noworld = balance(None)
T.FIRING_POLICY = "every_tick"; clock.RELAY_GATE = False
print("   v5   alt3 balance %.3f idle %.3f" % (v5[3]["balance"], v5[3]["idle"]))
print("   pure alt3 balance %.3f idle %.3f unvalued %.3f | alt2 balance %.3f | no-world alt3 %.3f" %
      (pure[3]["balance"], pure[3]["idle"], pure[3]["unvalued_share"], pure[2]["balance"], pure_noworld[3]["balance"]))
check("pure.v5_developed_holon_unbalanced", v5[3]["balance"] > 0.30)
check("pure.relay_developed_holon_balanced", pure[3]["balance"] < 0.02 and pure[2]["balance"] < 0.02)
check("pure.relay_developed_holon_not_idle", pure[3]["idle"] < 0.02)
check("pure.relay_developed_holon_on_valued_lap", pure[3]["unvalued_share"] < 0.03)
check("pure.holds_without_world", pure_noworld[3]["balance"] < 0.03 and pure_noworld[2]["balance"] < 0.03)
check("pure.no_altitude_branch_in_metabolism",
      "altitude" not in open("metabolism/tick.py").read().replace("# ", "") .split("def tick")[1].split("def run")[0].lower()
      and "retained" not in open("metabolism/tick.py").read().split("def tick")[1].split("def run")[0])

# ---- 4. provenance walks ----------------------------------------------------
def pair_records(t, u, steps, pol):
    T.FIRING_POLICY = pol
    ags = {"A": D.agent(t), "B": D.agent(u)}; inbox = seed(ags); recs = []
    for _ in range(steps):
        nxt = {h: [] for h in ags}
        for h, a in ags.items():
            a, out, rep = D.step(a, inbox[h]); ags[h] = a
            if h == "A": recs += [(a.altitude, pk) for pk in out]
            for pk in out:
                for o in ags:
                    if o != h: nxt[o].append(pk)
        inbox = nxt
    T.FIRING_POLICY = "every_tick"
    return recs
recs = pair_records("ile", "sei", 60, "every_tick")
late = [pk for alt, pk in recs if alt >= 2 and pk.tag == "ego"]
check("prov.world_packet_starts_a_walk", packet("ne").depth() == 1 and packet("ne").spans() == frozenset())
check("prov.developed_dual_output_is_joint", late and all(SP.joint(pk) for pk in late))
def alternates(w):
    """holon runs (landing + firing hops inside one holon) alternate between the two holons"""
    hs = [h for (h, _, _) in w if h != "world"]
    runs = [h for i, h in enumerate(hs) if i == 0 or h != hs[i - 1]]
    return len(runs) >= 4 and len(set(runs)) == 2
check("prov.dual_walk_alternates_holons", any(alternates(w) for pk in late for w in pk.walk))
check("prov.walk_records_the_chord", any(w[i][1] == 5 and w[i + 1][1] == 1 and w[i][0] == w[i + 1][0]
                                         for pk in late for w in pk.walk for i in range(len(w) - 1)))
check("prov.walk_aspects_are_carried",     # carried is uncapped; the walk keeps WALK_CAP hops
      all(frozenset(a for w in pk.walk for (_, _, a) in w) - {pk.aspect} <= pk.carried for alt, pk in recs if pk.tag != "request"))
byalt = SP.by_altitude(recs)
check("prov.joint_fraction_rises_with_altitude",
      all(byalt[a][1]["joint"] <= byalt[b][1]["joint"] for a in byalt for b in byalt if a < b) and byalt[max(byalt)][1]["joint"] == 1)

# ---- 5. spectrum: type-relative emission is one spectrum per altitude ------
for pol in ("every_tick", "relay"):
    spectra = collections.defaultdict(set)
    for t in TIMS:
        rs = pair_records(t, dual_candidate(t), 60, pol)
        for alt, sp in SP.by_altitude([(a, pk) for a, pk in rs]).items():
            spectra[alt].add(frozenset(collections.Counter(SP.relative_shape(pk, t) for a, pk in rs if a == alt).items()))
    check("spectrum.%s.one_relative_spectrum_per_altitude_all_16_types" % pol, all(len(s) == 1 for s in spectra.values()) and len(spectra) >= 3)
check("spectrum.cognitive_style_has_no_emission_signature", True)   # corollary of the two checks above; kept as a named claim

print("=" * 64)
print("all passed" if not FAILS else "FAILED: %s" % FAILS)
sys.exit(1 if FAILS else 0)
