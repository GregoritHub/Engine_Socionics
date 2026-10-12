"""The facet law, derived.

Premises:
  P1  dimensionality is the NUMBER of parameters a function processes
      (Bukalov; source_defined)
  P2  the parameters nest: time ⊂ situation ⊂ norms ⊂ experience
      (Bukalov; source_defined)
  P3  dim(p) = 1 + 2·strong(p) + bold(p)   (UMA §2; pyref.core, derived)

Theorem (verify_v5 enumerates all 16^4 assignments of the four facets
to boolean functions of (strong, bold)): exactly 96 satisfy P1+P3 and
exactly ONE also satisfies P2:

    experience  always
    norms       strong OR bold
    situation   strong
    time        strong AND bold

So the ladder is not a primitive: 'situation' IS the strong/weak
position dichotomy, 'time' is the 4D pair {1,8}, and 'norms' is exactly
what the 1D pair {4,5} lacks.  Status: derived, conditional on P1, P2.
"""
from __future__ import annotations
from pyref.core import pos_strong, pos_bold

FACETS = ("experience", "norms", "situation", "time")
LAW = {
    "experience": lambda S, B: True,
    "norms":      lambda S, B: S or B,
    "situation":  lambda S, B: S,
    "time":       lambda S, B: S and B,
}


def facets_of(S: bool, B: bool) -> frozenset:
    return frozenset(f for f in FACETS if LAW[f](S, B))


def position_facets(p: int) -> frozenset:
    return facets_of(pos_strong(p), bool(pos_bold(p)))


def facets_up_to(d: int) -> frozenset:
    """The chain view, for callers that only know a dimension.  Equal to
    position_facets on every position (checked)."""
    return frozenset(FACETS[:d])


def level(f: str) -> int:
    return FACETS.index(f) + 1
