"""Transfer between psyches.  The relation group is the channel:
landing_position reads rel_map, not the stacks; verify checks the two
agree on all 16x16x8 cases.  Names come from the kernel's anchored
relations, the centre of the dynamical group (super-ego), and the seven
permutations audited in docs/UNRESOLVED_SOURCE_ITEMS.md section 3."""
from __future__ import annotations
from pyref import core
from pyref.core import POS_COORD, COORD_POS, rel_map, apply_relation

AUDITED_PERMS = {
    (2, 1, 4, 3, 6, 5, 8, 7): "mirror",
    (1, 4, 3, 2, 5, 8, 7, 6): "kindred",
    (4, 3, 2, 1, 8, 7, 6, 5): "conflict",
    (5, 8, 7, 6, 1, 4, 3, 2): "semi_duality",
    (8, 7, 6, 5, 4, 3, 2, 1): "quasi_identity",
    (3, 2, 1, 4, 7, 6, 5, 8): "business",
    (7, 6, 5, 8, 3, 2, 1, 4): "mirage",
}


def landing_position(tim_a: str, i: int, tim_b: str) -> int:
    """Position in B of the aspect at position i in A, via rel_map^-1."""
    return COORD_POS[rel_map(tim_a, tim_b).inverse()(POS_COORD[i])]


def landing_perm(tim_a: str, tim_b: str) -> tuple:
    return tuple(landing_position(tim_a, i, tim_b) for i in range(1, 9))


def _anchored():
    act = core.ESTAFETTE.compose(core.ESTAFETTE).key()
    sup = next(g for g in core.group_center(core.dynamical_group())
               if g != core.identity_affine().key())
    return [("duality", lambda a, b: core.dual_candidate(a) == b),
            ("contrary", lambda a, b: core.contrary(a) == b),
            ("benefit", lambda a, b: core.v11_beneficiary(a) == b),
            ("benefit_inverse", lambda a, b: core.v11_beneficiary(b) == a),
            ("supervision", lambda a, b: core.v11_supervisee(a) == b),
            ("supervision_inverse", lambda a, b: core.v11_supervisee(b) == a),
            ("activation", lambda a, b: apply_relation(act, a) == b),
            ("super_ego", lambda a, b: apply_relation(sup, a) == b)]


ANCHORED = _anchored()


def relation_of(tim_a: str, tim_b: str) -> str:
    if tim_a == tim_b:
        return "identity"
    for name, test in ANCHORED:
        if test(tim_a, tim_b):
            return name
    return AUDITED_PERMS.get(landing_perm(tim_a, tim_b),
                             "unnamed:%r" % (rel_map(tim_a, tim_b).key(),))
