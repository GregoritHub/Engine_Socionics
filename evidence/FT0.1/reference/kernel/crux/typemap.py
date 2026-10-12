"""Crux structural layer — the per-TIM type map, generated not entered.

Status: derived. Every value here is computed from the kernel's
source_defined stacks (pyref.core.DEFINITIVE_STACKS). Nothing in this
module is written per type, so the sixteen type maps cannot drift from
the locked architecture.

Derivations implemented (Atlas Part 3, Part 8.1; source section 15):

  * the strong half of Model A (1,2,7,8) lies in the native club and the
    weak half (3,4,5,6) in the complementary club -- so the strong/weak
    dichotomy IS the native/complementary quadrant dichotomy;
  * the Super-Id pair is the counterphase of the Ego pair, G_T = cp(E_T),
    and -- the other half of the same relation -- the Id pair is the
    counterphase of the Super-Ego pair, so counterphase runs over all four
    position pairs 1-5, 2-6, 3-7, 4-8;
  * the four cost classes -- native (F1,F2), Lateral-E (F1,F6),
    Lateral-A (F2,F5), complementary (F5,F6) -- form a BIJECTION onto the
    four Cross perspectives;
  * the dwelling-cost ladder 7 / 6 / 4 / 3 by dimensionality sum;
  * first-order individuation is always the surface flip, disp = 01.

This module never writes to pyref; it only reads the locked tables.
"""

from __future__ import annotations

from pyref.core import (CLASS, DEFINITIVE_STACKS, TIMS, attitude,
                        dual_candidate)

from .perspectives import CruxError, disp, scale, SURFACE_FLIP

VERSION = "crux_v1"

# Club <-> perspective correspondence (Atlas Part 3).  V5: no longer
# typed here.  Regenerated from the IE cube's internal/external bit by
# algebra.perspective (derived); verify_v5 checks it equals the table the
# Atlas states: NF<->I, ST<->IT, SF<->WE, NT<->ITS.
from algebra.perspective import club_table as _club_table
CLUB_PERSPECTIVE = _club_table()
CLUB_NAME = {("n", "f"): "NF", ("s", "t"): "ST",
             ("s", "f"): "SF", ("n", "t"): "NT"}

# Counterphase involution (source section 15).
COUNTERPHASE = {"ne": "si", "si": "ne", "se": "ni", "ni": "se",
                "fe": "ti", "ti": "fe", "te": "fi", "fi": "te"}

# Model A dimensionality by position -- mirrors le_position_geometry:access/1.
DIMENSIONALITY = {1: 4, 2: 3, 3: 2, 4: 1, 5: 1, 6: 2, 7: 3, 8: 4}

# Polarity by position (source section 15 / Atlas Part 3):
# position 5 accumulates, position 6 expends.
POSITION_POLARITY = {1: "accumulation", 2: "expenditure",
                     3: "accumulation", 4: "expenditure",
                     5: "accumulation", 6: "expenditure",
                     7: "accumulation", 8: "expenditure"}

# Ring split (source_defined, Model A). Positions 1-4 are the mental ring,
# 5-8 the vital ring. Implicit throughout the rest of this module; named
# here because the counterphase derivation below asserts ring crossing.
MENTAL_POSITIONS = (1, 2, 3, 4)
VITAL_POSITIONS = (5, 6, 7, 8)

COST_CLASSES = ("native", "lateral_E", "lateral_A", "complementary")

# Which Model A positions carry each cost class.
CLASS_POSITIONS = {"native": (1, 2), "lateral_E": (1, 6),
                   "lateral_A": (2, 5), "complementary": (5, 6)}


def element_at(tim: str, position: int) -> str:
    if tim not in DEFINITIVE_STACKS:
        raise CruxError("invalid_tim", str(tim))
    if position not in DIMENSIONALITY:
        raise CruxError("invalid_position", str(position))
    return DEFINITIVE_STACKS[tim][position - 1]


def counterphase(element: str) -> str:
    if element not in COUNTERPHASE:
        raise CruxError("invalid_element", str(element))
    return COUNTERPHASE[element]


def macro_axes(elements):
    ns = {CLASS[e] for e in elements if CLASS[e] in ("n", "s")}
    tf = {CLASS[e] for e in elements if CLASS[e] in ("t", "f")}
    return ns, tf


def perspective_of(elements):
    """The Cross perspective a set of elements addresses.

    A perspective requires exactly one {n,s} axis and one {t,f} axis; a
    set that does not span both, or spans one twice, addresses none.
    """
    ns, tf = macro_axes(elements)
    if len(ns) != 1 or len(tf) != 1:
        raise CruxError("does_not_span_a_perspective",
                        "ns=%s tf=%s" % (sorted(ns), sorted(tf)))
    return CLUB_PERSPECTIVE[(ns.pop(), tf.pop())]


def club_of(elements) -> str:
    ns, tf = macro_axes(elements)
    if len(ns) != 1 or len(tf) != 1:
        raise CruxError("does_not_span_a_club")
    return CLUB_NAME[(ns.pop(), tf.pop())]


def cost_class_pair(tim: str, cost_class: str):
    if cost_class not in CLASS_POSITIONS:
        raise CruxError("invalid_cost_class", str(cost_class))
    a, b = CLASS_POSITIONS[cost_class]
    return (element_at(tim, a), element_at(tim, b))


def ring_of(position: int) -> str:
    """`mental` for positions 1-4, `vital` for 5-8."""
    if position in MENTAL_POSITIONS:
        return "mental"
    if position in VITAL_POSITIONS:
        return "vital"
    raise CruxError("invalid_position", str(position))


def is_valued(position: int) -> bool:
    """Valued positions are exactly the Ego and Super-Id blocks.

    Derived rather than tabulated: the valued positions are the union of
    the two cost classes whose pairs are valued, so this cannot drift from
    CLASS_POSITIONS.
    """
    if position not in DIMENSIONALITY:
        raise CruxError("invalid_position", str(position))
    return position in (set(CLASS_POSITIONS["native"])
                        | set(CLASS_POSITIONS["complementary"]))


def dwelling_cost(cost_class: str) -> int:
    """Dimensionality sum of the valued pair carrying this class.

    Higher is cheaper: native 7, Lateral-E 6, Lateral-A 4, complementary 3.
    TIM-invariant, because the positions are fixed.
    """
    a, b = CLASS_POSITIONS[cost_class]
    return DIMENSIONALITY[a] + DIMENSIONALITY[b]


def weakest_of(cost_class: str) -> int:
    a, b = CLASS_POSITIONS[cost_class]
    return min(DIMENSIONALITY[a], DIMENSIONALITY[b])


def type_map(tim: str) -> dict:
    """The complete generated type map for one TIM."""
    out = {"tim": tim, "version": VERSION,
           "stack": list(DEFINITIVE_STACKS[tim]),
           "ego_pair": cost_class_pair(tim, "native"),
           "super_id_pair": cost_class_pair(tim, "complementary"),
           "classes": {}}
    seen = {}
    for cc in COST_CLASSES:
        pair = cost_class_pair(tim, cc)
        p = perspective_of(pair)
        if p in seen:
            raise CruxError("cost_map_not_a_bijection",
                            "%s and %s both address %s" % (seen[p], cc, p))
        seen[p] = cc
        out["classes"][cc] = {
            "pair": pair,
            "club": club_of(pair),
            "perspective": p,
            "dwelling_cost": dwelling_cost(cc),
            "weakest_dimensionality": weakest_of(cc),
        }
    out["native_perspective"] = out["classes"]["native"]["perspective"]
    out["complementary_perspective"] = \
        out["classes"]["complementary"]["perspective"]
    out["scale"] = scale(out["native_perspective"])
    out["first_crossing"] = (out["native_perspective"],
                             out["complementary_perspective"])
    out["return_route"] = (out["complementary_perspective"],
                           out["native_perspective"])
    out["ground_state"] = (out["native_perspective"],
                           out["native_perspective"])
    return out


def perspective_cost_class(tim: str, perspective: str) -> str:
    """Inverse of the bijection: which cost class addresses this perspective."""
    tm = type_map(tim)
    for cc, info in tm["classes"].items():
        if info["perspective"] == perspective:
            return cc
    raise CruxError("unreachable_perspective", perspective)


def cost_of_perspective(tim: str, perspective: str) -> int:
    return dwelling_cost(perspective_cost_class(tim, perspective))


def all_type_maps() -> dict:
    return {t: type_map(t) for t in TIMS}


# ---------------------------------------------------------------------------
# The derivations, as predicates. verify_v3 runs each over all sixteen TIMs.
# ---------------------------------------------------------------------------

def d_strong_half_is_native_club(tim: str) -> bool:
    strong = [element_at(tim, p) for p in (1, 2, 7, 8)]
    weak = [element_at(tim, p) for p in (3, 4, 5, 6)]
    ego = [element_at(tim, 1), element_at(tim, 2)]
    return (perspective_of(strong) == perspective_of(ego)
            and disp(perspective_of(strong), perspective_of(weak))
            == SURFACE_FLIP)


def d_super_id_is_counterphase_of_ego(tim: str) -> bool:
    return (element_at(tim, 5) == counterphase(element_at(tim, 1))
            and element_at(tim, 6) == counterphase(element_at(tim, 2)))


def d_super_id_pair_is_some_tim_ego_pair(tim: str) -> bool:
    """Closure: the complementary pair is SOME TIM's Ego pair.

    The weak half of the claim. It says the Super-Id pair never lands
    outside the sixteen Ego pairs; it does not say which TIM owns it.
    Kept as a separate proposition because it is the part that would still
    hold if the duality anchoring below were wrong.
    """
    want = cost_class_pair(tim, "complementary")
    return any(cost_class_pair(o, "native") == want for o in TIMS)


def d_super_id_pair_is_the_dual_ego_pair(tim: str) -> bool:
    """Atlas Part 1 / I1, stated [S]: the Super-Id pair is the Ego pair of
    the DUAL. The strong half, and the reason individuation has the precise
    form of internal dualization without type change.

    The check is not circular. Two independent routes to the same pairing
    are compared:

      this side   Model A positions (5,6) via the counterphase involution
      kernel side `pyref.core.dual_candidate` -- the relation group's
                  torsor element rel(ile, sei), anchored on one README
                  instance and applied to every TIM

    Nothing in the relation-group route consults the Super-Id block, so
    agreement across all sixteen is a real coincidence of two derivations
    rather than a restatement. Three conditions are asserted together:
    the owner exists and is UNIQUE, the owner is the kernel's dual, and
    duality is fixed-point-free (no TIM is its own dual).
    """
    want = cost_class_pair(tim, "complementary")
    owners = [o for o in TIMS if cost_class_pair(o, "native") == want]
    if len(owners) != 1:
        return False
    return owners[0] == dual_candidate(tim) and dual_candidate(tim) != tim


def d_cost_classes_partition_perspectives(tim: str) -> bool:
    tm = type_map(tim)  # raises cost_map_not_a_bijection if it fails
    return len({c["perspective"] for c in tm["classes"].values()}) == 4


def d_dwelling_ladder_7_6_4_3(tim: str) -> bool:
    return tuple(dwelling_cost(c) for c in
                 ("native", "lateral_E", "lateral_A", "complementary")) \
        == (7, 6, 4, 3)


def d_laterals_at_displacement_10_and_11(tim: str) -> bool:
    tm = type_map(tim)
    nat = tm["native_perspective"]
    got = {disp(nat, tm["classes"]["lateral_E"]["perspective"]),
           disp(nat, tm["classes"]["lateral_A"]["perspective"])}
    return got == {0b10, 0b11}


def d_first_crossing_is_surface_flip(tim: str) -> bool:
    tm = type_map(tim)
    return disp(*tm["first_crossing"]) == SURFACE_FLIP


def d_id_is_counterphase_of_super_ego(tim: str) -> bool:
    """The counterphase relation runs over FOUR position pairs, not two.

    Generative Semantics of Information Metabolism v1.1 section 28 states
    the counterphase relation as positions 1-5, 2-6, **3-7 and 4-8**, with
    the pairs Ne-Si, Se-Ni, Fe-Ti, Te-Fi throughout. The kernel and the
    Atlas only ever assert the first half -- G_T = cp(E_T), checked above
    as `super_id_is_counterphase_of_ego`. This is the other half: the Id
    block is the counterphase of the Super-Ego block.

    The full section 28 property is asserted, not just the element
    identity, because the identity alone could be a numerical coincidence
    of the stack convention. A counterphase pair must

      * be counterphase partners under the involution;
      * SHARE valuation -- 3, 4, 7, 8 are all unvalued, as 1, 2, 5, 6 are
        all valued;
      * CROSS the ring -- 3, 4 mental against 7, 8 vital;
      * CROSS attitude -- the involution is extro <-> intro throughout.

    Section 28 also requires crossing the static/dynamic class. That is not
    asserted here: the static set {Ne, Se, Fi, Ti} is a further
    source_defined constant this module does not currently carry, and
    importing one to strengthen a check would put a source fact behind a
    derivation. It is left to whoever adds the static/dynamic layer.
    """
    for mental_pos, vital_pos in ((3, 7), (4, 8)):
        a = element_at(tim, mental_pos)
        b = element_at(tim, vital_pos)
        if b != counterphase(a):
            return False
        if is_valued(mental_pos) or is_valued(vital_pos):
            return False
        if ring_of(mental_pos) == ring_of(vital_pos):
            return False
        if attitude(a) == attitude(b):
            return False
    return True


DERIVATIONS = {
    "strong_half_is_native_club": d_strong_half_is_native_club,
    "super_id_is_counterphase_of_ego": d_super_id_is_counterphase_of_ego,
    "super_id_pair_is_some_tim_ego_pair": d_super_id_pair_is_some_tim_ego_pair,
    "super_id_pair_is_the_dual_ego_pair": d_super_id_pair_is_the_dual_ego_pair,
    "id_is_counterphase_of_super_ego": d_id_is_counterphase_of_super_ego,
    "cost_classes_partition_perspectives": d_cost_classes_partition_perspectives,
    "dwelling_ladder_7_6_4_3": d_dwelling_ladder_7_6_4_3,
    "laterals_at_displacement_10_and_11": d_laterals_at_displacement_10_and_11,
    "first_crossing_is_surface_flip": d_first_crossing_is_surface_flip,
}
