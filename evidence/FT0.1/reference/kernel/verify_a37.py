#!/usr/bin/env python3
"""A37 -- what is derived, what is a reading, what is left.

Enumerates every seat-dependent firing rule F: seat -> subset of {1, 2, 8}
(8^8 = 16,777,216 rules) and applies the readings as predicates:

  C1  gas-only          only gas positions produce (R6; external, A18)       -- the space
  C2  expenditure-turn  production only at seats with a = 1 (Shell Geometry:
                        a formal movement carries ONE polarity bit,
                        Accumulation or Expenditure; read onto the seat via A20)
  C3  engaged-block     at a producing seat the seat's block produces
                        (`engaged_block`, extended from reception to production)
                        and nothing outside the block produces except along a
                        sourced chord out of it (G_CHORDS_A: 6->1, 1->8)
  C4a chord 6->1        is the activating function's expenditure: on seat 6's
                        turn its charge leaves through A1 (kernel note "A6
                        initiates the Leader")
  C4b chord 1->8        the kernel note (UMA s.19, both editions) reads
                        "receives an energy boost from the Leader" -- a
                        charging relation, wired at reception (R7).  "The
                        Leader fires and the demonstrative fires too" is the
                        engine's phrase, not the source's.  So whether 8 FIRES
                        with 1 on the Ego's turn is a READING (boost@2), as is
                        whether it fires with the chord emission (boost@6).

What survives C1-C3 and C4a is exactly FOUR rules: the two boost binaries.
The engine's FIRES_AT is (boost@2 = yes, boost@6 = no).  Everything else in
`relay` is these readings; nothing else is chosen.  The source's own
proposed schedule (UMA s.24, Te->Ne->Fe for IEE) enters A8 AFTER A1 as a
separate stage; its engine analogue is boost@2 = no (`relay_noboost2`).

Then the family-wide facts from bin/a37_rules: the supervisor's
complement-first closure belongs to the whole family (every rule but
every_tick), and the one-tick delay belongs to reading C3 alone.

Kernel untouched; manifest checked first.  Runtime ~30 s.
"""
import os, sys, json, hashlib, itertools, collections
_d = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, _d); sys.path.insert(0, os.path.join(_d, "bin"))
from pyref.core import POS_COORD, ACCESS, G_CHORDS_A, TIMS, element_at
from metabolism.handler import BLOCK, FIRING
from metabolism.energy import gas
import metabolism.tick; T = sys.modules["metabolism.tick"]

N = 0; FAILED = []
def check(name, ok, note=""):
    global N; N += 1
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("   " + note) if note else ""))
    if not ok: FAILED.append(name)

# ---- 0. seal --------------------------------------------------------------
man = json.load(open(os.path.join(_d, "manifests", "kernel_sha256.json")))
files = man.get("files", man)
ok = all(hashlib.sha256(open(os.path.join(_d, "pyref", f), "rb").read()).hexdigest() == h
         for f, h in files.items() if isinstance(h, str))
check("kernel.manifest_intact", ok)

# ---- 1. the rule space and the readings -----------------------------------
GAS_ALL = tuple(p for p in range(1, 9) if gas(p))
check("a37.gas_positions_are_1_2_5_8", GAS_ALL == (1, 2, 5, 8))
# the suggestive's emission is the REQUEST (replenish), not content, and it is not
# seat-timed under either policy; the content-emitting gas positions are FIRING
GAS = FIRING
check("a37.content_firing_set_is_gas_minus_suggestive", GAS == (1, 2, 8) and set(GAS_ALL) - set(GAS) == {5})
CHORDS = [tuple(c) for c in G_CHORDS_A]
check("a37.sourced_chords_are_6to1_and_1to8", sorted(CHORDS) == [(1, 8), (6, 1)])
SEATS = range(1, 9)
PRODUCING = [s for s in SEATS if POS_COORD[s][0] == 1]
block = lambda s: {p for p in SEATS if BLOCK[p] == BLOCK[s]}

def chord_reach(src):
    out, frontier = set(), set(src)
    while frontier:
        nxt = {b for (a, b) in CHORDS if a in frontier} - out
        out |= nxt; frontier = nxt
    return out

subsets = [frozenset(c) for r in range(4) for c in itertools.combinations(GAS, r)]   # C1: 8 subsets
space = 8 ** 8
check("a37.rule_space_is_8_to_the_8", space == 16777216)

def C2(F): return all(not F[s] for s in SEATS if POS_COORD[s][0] == 0)
def C3(F):
    for s in PRODUCING:
        must = {p for p in block(s) if p in GAS}
        may = must | (chord_reach(block(s)) & set(GAS))
        if not must <= F[s] or not F[s] <= may: return False
        # chord-reachable positions require the chord's source to be producing too
        for p in F[s] - must:
            srcs = {a for (a, b) in CHORDS if b == p}
            if not (srcs & (block(s) | F[s])): return False
    return True
def C4a(F): return 1 in F[6]
def C4b(F): return (8 in F[2]) == (1 in F[2])

# enumerate only over producing seats (C2 fixes the accepting ones to empty): 8^4 = 4096
survivors = []
for combo in itertools.product(subsets, repeat=len(PRODUCING)):
    F = {s: frozenset() for s in SEATS}
    for s, sub in zip(PRODUCING, combo): F[s] = sub
    if C2(F) and C3(F): survivors.append(F)
check("a37.C1_C2_C3_leave_six_rules", len(survivors) == 6, "%d" % len(survivors))
s4a = [F for F in survivors if C4a(F)]
check("a37.C1_to_C4a_leave_exactly_four", len(s4a) == 4, "%d" % len(s4a))
free = {s for F in s4a for G in s4a for s in SEATS if F[s] != G[s]}
check("a37.the_four_differ_only_in_8_at_seats_2_and_6",
      free == {2, 6} and all((F[s] - {8}) == (s4a[0][s] - {8}) for F in s4a for s in SEATS))
s4 = [F for F in s4a if C4b(F)]
check("a37.boost_at_2_as_a_reading_leaves_two", len(s4) == 2, "%d" % len(s4))
engine = {s: frozenset(T.FIRES_AT.get(s, ())) for s in SEATS}
# the engine realises seat 6's `1` through chord.emit, not FIRES_AT; add it for comparison
engine6 = dict(engine); engine6[6] = engine6[6] | {1}
check("a37.engine_FIRES_AT_is_the_boost2_noboost6_survivor", engine6 in s4a and 8 in engine6[2] and 8 not in engine6[6])
check("a37.engine_note_for_A8_is_receives_a_boost_not_fires_too",
      "boost" in __import__("pyref.core", fromlist=["G_ENERGETIC_NOTE"]).G_ENERGETIC_NOTE[2] and
      "fires" not in __import__("pyref.core", fromlist=["G_ENERGETIC_NOTE"]).G_ENERGETIC_NOTE[2])
check("a37.every_tick_violates_C2", not C2({s: frozenset(GAS) for s in SEATS}))

# ---- 2. family-wide facts (runs) ------------------------------------------
import a37_rules as R
from crux.typemap import perspective_cost_class as pcc
from metabolism import develop as D, packet
from metabolism.exchange import relation_of
def hist(a): return tuple((x["tick"], pcc(a.st.tim, x["closed"])) for x in a.history)
def table(rule, base="ile", steps=120):
    R.use(rule); out = {}
    for u in TIMS:
        ags = {"A": D.agent(base), "B": D.agent(u)}
        ags, _ = D.run(ags, {h: [packet(element_at(a.st.tim, 1))] for h, a in ags.items()}, steps)
        out[relation_of(base, u)] = hist(ags["A"])
    R.use(None); return out
fam = {r: table(r) for r in R.RULES}
first = lambda h: h[0][1] if h else "sterile"
def native_table(policy, base="ile", steps=120):
    R.native(policy); out = {}
    for u in TIMS:
        ags = {"A": D.agent(base), "B": D.agent(u)}
        ags, _ = D.run(ags, {h: [packet(element_at(a.st.tim, 1))] for h, a in ags.items()}, steps)
        out[relation_of(base, u)] = hist(ags["A"])
    R.native("every_tick"); return out
check("a37.harness_every_tick_matches_native", fam["every_tick"] == native_table("every_tick"))
check("a37.harness_relay_matches_native", fam["relay"] == native_table("relay"))
def early(h): return h[0][0] < 64 if h else False
check("a37.supervisor_early_lateral_first_only_under_every_tick",
      first(fam["every_tick"]["supervision"]) == "lateral_A" and
      all(not (early(fam[r]["supervision"]) and first(fam[r]["supervision"]).startswith("lateral")) for r in R.RULES if r != "every_tick"))
# the demonstrative firing on a VALUED expenditure seat (2 or 6) is what carries the kindred
# and supervision channels under seat-timed production; only on its own seat 8, both are lost
VALUED_8 = [r for r in R.RULES if r != "every_tick" and (8 in R.RULES[r]["fire_at"].get(2, ()) or 8 in R.RULES[r]["fire_at"].get(6, ()))]
OWN_SEAT_8 = [r for r in R.RULES if r != "every_tick" and r not in VALUED_8]
check("a37.supervisor_complement_first_iff_demonstrative_fires_on_the_valued_lap",
      all(first(fam[r]["supervision"]) == "complementary" for r in VALUED_8) and
      all(not early(fam[r]["supervision"]) for r in OWN_SEAT_8) and OWN_SEAT_8 == ["relay_noboost2"],
      "valued=%s own_seat=%s" % (VALUED_8, OWN_SEAT_8))
check("a37.kindred_productive_iff_demonstrative_fires_on_the_valued_lap",
      all(fam[r]["kindred"] and fam[r]["kindred"][0][0] < 64 for r in VALUED_8) and all(fam[r]["kindred"] == () for r in OWN_SEAT_8))
check("a37.supervisor_discriminator_is_family_wide_not_relay_specific",
      all(first(fam[r]["supervision"]) == "complementary" for r in ("turn_only", "block_only")))
check("a37.one_tick_delay_is_reading_C3",
      fam["turn_only"]["duality"][0][0] == 4 and all(fam[r]["duality"][0][0] == 5 for r in ("block_only", "turn_block", "relay")))
check("a37.identity_semi_dual_tick3_closure_only_under_every_tick",
      fam["every_tick"]["identity"] == ((3, "lateral_A"),) and all(not fam[r]["identity"] or fam[r]["identity"][0][0] >= 64 for r in R.RULES if r != "every_tick"))
check("a37.boost_reading_is_not_invisible",
      fam["relay"] != fam["relay_boost6"], "differs in %d rows" % sum(fam["relay"][k] != fam["relay_boost6"][k] for k in fam["relay"]))
check("a37.sequential_reading_keeps_duality",
      fam["relay_noboost2"]["duality"][0][1] == "complementary")
check("a37.sequential_reading_loses_kindred_and_the_supervisors_closure",
      fam["relay_noboost2"]["kindred"] == () and (not fam["relay_noboost2"]["supervision"] or fam["relay_noboost2"]["supervision"][0][0] >= 64))
check("a37.kindred_equals_duality_under_relay_rests_on_boost_at_2",
      fam["relay"]["kindred"] == fam["relay"]["duality"] and fam["relay_noboost2"]["kindred"] != fam["relay_noboost2"]["duality"])
check("a37.type_invariance_and_contrary_symmetry_survive_in_family",
      all(table(r, base="esi") == {k: v for k, v in fam[r].items()} for r in ("turn_only", "block_only", "relay_noboost2")))
R.native("every_tick")

print("=" * 64)
print("%d/%d passed" % (N - len(FAILED), N) + ("" if not FAILED else "  FAILED: " + ", ".join(FAILED)))
