"""One content algebra.

V1..V4 accumulated four vocabularies for "content":

  IE aspects        eight elements, F2^3 (q,e,n)         pyref.core
  OIG domains       its / i / we / it, class pairs       pyref.oig
  Crux perspectives I / IT / WE / ITS, two bits          crux.perspectives
  facets            experience / norms / situation / time metabolism.packet

They met at seams.  This package states the maps between them and
proves, from IE_COORD alone, that the two hand-typed tables
(oig.CLASS_PAIR, typemap.CLUB_PERSPECTIVE) are the same object.

  perspective.py   Q = F2^2 as an affine image of the IE 'n' bit;
                   aspects cover lines, rational+irrational pairs
                   cover points; blocks address perspectives
  content.py       the single Content value and its projections
  facets.py        the facet law, unique under Bukalov's P1+P2 and UMA's
                   dimension formula
  kepinski.py      Kępiński's categories as the three position
                   coordinates; two axes oriented, v open; the sourced
                   chord is a return edge
  archetype.py     S_C: the eight archetypes on Model A positions,
                   complexes as (0,1,1) flips (Archetypal Shadow Complex)

Reads pyref/ only.
"""
VERSION = "algebra_v1"

from .perspective import (PERSPECTIVES, DOMAIN_KEY, line_of, point_of,
                          perspective_bits, block_perspective, reach)
from .content import Content, project_domains
from .facets import FACETS, facets_of, position_facets, facets_up_to, level
from .kepinski import signature, monotone, chord_report, ORIENTATION

__all__ = [
    "VERSION",
    "PERSPECTIVES", "DOMAIN_KEY", "line_of", "point_of",
    "perspective_bits", "block_perspective", "reach",
    "Content", "project_domains",
    "FACETS", "facets_of", "position_facets", "facets_up_to", "level",
    "signature", "monotone", "chord_report", "ORIENTATION",
]
