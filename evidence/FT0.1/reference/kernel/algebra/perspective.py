"""Perspectives derived from the IE cube.

Theorem (proved in verify_v5 by exhaustion):

  Let n(e) be the 'internal' coordinate of aspect e in UMA section 3
  (IE_COORD[e][2]: 1 on Ni, Ne, Fi, Fe).  For an irrational aspect r and
  a rational aspect j,

      collective(r, j) = n(r) XOR n(j)
      interior(r, j)   = 1 XOR n(j)

  reproduces crux.perspectives.CODE exactly, and the two hand-typed
  tables oig.CLASS_PAIR and typemap.CLUB_PERSPECTIVE are both images of
  this one affine map.  The Crux square is therefore a change of basis
  on the kernel's internal/external dichotomy, not a fourth primitive.

Consequences (all checked):
  * one aspect fixes one coordinate and leaves the other free: an
    aspect covers a LINE of two perspectives -- this is oig.CLASS_PAIR;
  * a rational+irrational pair fixes a POINT -- this is CLUB_PERSPECTIVE;
  * every Model A block is such a pair (stacks alternate rationality),
    so every block addresses a perspective: Ego and Id the native one,
    Super-Ego and Super-Id its surface partner, and the two lateral
    pairs the remaining two -- typemap's four cost classes;
  * OIG reach(tim, d) = positions whose aspect's line contains d.

Status: derived.  The only source_defined input is IE_COORD.
"""
from __future__ import annotations
from pyref.core import (IE_COORD, ELEMENTS, CLASS, rationality, element_at,
                        vadd, POS_COORD, COORD_POS)

PERSPECTIVES = ("I", "IT", "WE", "ITS")
BITS = {"I": (0, 0), "IT": (0, 1), "WE": (1, 0), "ITS": (1, 1)}
BY_BITS = {v: k for k, v in BITS.items()}
DOMAIN_KEY = {"I": "i", "IT": "it", "WE": "we", "ITS": "its"}
KEY_PERSPECTIVE = {v: k for k, v in DOMAIN_KEY.items()}


def n_bit(e: str) -> int:
    return IE_COORD[e][2]


def perspective_bits(irrational: str, rational: str) -> tuple:
    """(collective, interior) from the n-bits of an irrational/rational pair."""
    if rationality(irrational) != "irrational" or rationality(rational) != "rational":
        raise ValueError("need one irrational and one rational aspect")
    return (n_bit(irrational) ^ n_bit(rational), 1 ^ n_bit(rational))


def point_of(a: str, b: str) -> str:
    """The perspective addressed by a rational+irrational pair (either order)."""
    if rationality(a) == "irrational":
        return BY_BITS[perspective_bits(a, b)]
    return BY_BITS[perspective_bits(b, a)]


def line_of(e: str) -> frozenset:
    """The two perspectives an aspect can address, paired with any partner."""
    partners = [p for p in ELEMENTS if rationality(p) != rationality(e)]
    return frozenset(point_of(e, p) for p in partners)


def block_partner(p: int) -> int:
    return COORD_POS[vadd(POS_COORD[p], (1, 0, 0))]


def block_perspective(tim: str, p: int) -> str:
    """Perspective addressed by the block containing position p."""
    return point_of(element_at(tim, p), element_at(tim, block_partner(p)))


def reach(tim: str, perspective: str) -> frozenset:
    """Positions whose aspect's line contains the perspective.  Must equal
    oig.reach(tim, DOMAIN_KEY[perspective]); checked."""
    return frozenset(p for p in range(1, 9)
                     if perspective in line_of(element_at(tim, p)))


def class_pair_table() -> dict:
    """Regenerate oig.CLASS_PAIR from the algebra."""
    out = {}
    for c in ("n", "s", "t", "f"):
        e = next(x for x in ELEMENTS if CLASS[x] == c)
        out[c] = {DOMAIN_KEY[P] for P in line_of(e)}
    return out


def club_table() -> dict:
    """Regenerate typemap.CLUB_PERSPECTIVE from the algebra."""
    out = {}
    for x in ("n", "s"):
        for y in ("t", "f"):
            ex = next(e for e in ELEMENTS if CLASS[e] == x)
            ey = next(e for e in ELEMENTS if CLASS[e] == y)
            out[(x, y)] = point_of(ex, ey)
    return out
