"""Gulenko's four cognitive styles as a subgroup question (V5.2, A39).

Source (external_secondary): V. Gulenko, "Forms of Thinking", Socionics,
Mentology and Personality Psychology 4 (2002); wikisocion translation.
The source defines the styles by three Reinin dichotomies and lists
their carriers:

    causal_determinist       process  positivist  static    ILE LSI SEE EII
    dialectical_algorithmic  process  negativist  dynamic   SEI EIE ILI LSE
    holographic_panoramic    result   negativist  static    SLE LII IEE ESI
    vortical_synergetic      result   positivist  dynamic   ESE IEI LIE SLI

Derived here, checked in verify_v5_2 against the kernel's characters:

  1. The three dichotomies are two.  In the character group,
         static/dynamic + process/result = positivist/negativist,
     so the third is the product of the first two; three dichotomies
     give four classes, not eight, and that is why there are four styles.
  2. Each style is a coset of the annihilator of span{static, process}
     -- an order-4 subgroup of the TIM space.  Style is a coordinate pair
     on the F2 algebra, not a new content vocabulary.
  3. The style subgroup is the supervision ring: v11_supervisee maps each
     style to itself, and its orbit is the whole style.  Gulenko's remark
     that supervision rings carry a form of thinking through society is,
     at kernel level, an identity: a cognitive style IS a supervision ring.
  4. Duality and benefit map a style to its partner style (CD<->DA,
     HP<->VS); contrary fixes... see verify for the exact images.

The verbal poles ("positivist", "static", "process") follow A6: names
attach to characters, polarity of the pole is not asserted.  The
carrier lists are what is checked.
"""
from __future__ import annotations
from pyref.core import (TIMS, REININ_NAMES, character, shared_characters, span,
                        annihilator, vadd, v11_supervisee, dual_candidate,
                        v11_beneficiary, contrary, jungian_coord)

CHAR = {v: k for k, v in REININ_NAMES.items()}
STATIC = CHAR["static/dynamic"]
PROCESS = CHAR["process/result"]
POSITIVIST = CHAR["positivist/negativist"]

CARRIERS = {                       # source_defined (Gulenko 2002)
    "causal_determinist": ("ile", "lsi", "see", "eii"),
    "dialectical_algorithmic": ("sei", "eie", "ili", "lse"),
    "holographic_panoramic": ("sle", "lii", "iee", "esi"),
    "vortical_synergetic": ("ese", "iei", "lie", "sli"),
}
SOURCE = {"carriers": "external_secondary:Gulenko 2002 'Forms of Thinking' (wikisocion)",
          "coset_law": "derived", "supervision_identity": "derived"}


def coordinates(tim: str) -> tuple:
    """(process/result, static/dynamic) character values -- the style's coordinates."""
    return (character(PROCESS, tim), character(STATIC, tim))


def style_subgroup() -> list:
    """Annihilator of span{static, process}: the subgroup whose cosets are the styles."""
    return sorted(annihilator(span([STATIC, PROCESS], 4), 4))


_BY_COORD = {coordinates(g[0]): name for name, g in CARRIERS.items()}


def style_of(tim: str) -> str:
    return _BY_COORD[coordinates(tim)]


def partner_style(name: str) -> str:
    return style_of(dual_candidate(CARRIERS[name][0]))
