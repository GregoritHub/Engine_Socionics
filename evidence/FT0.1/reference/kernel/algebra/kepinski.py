"""Kępiński's categories in kernel coordinates.

Kępiński (Melancholia; Psychopatologia nerwic) asserts, categorically:
  K1  energy metabolism oscillates between accumulation (anabolic) and
      expenditure (catabolic);
  K2  information metabolism has an affective/subconscious phase that
      orients toward or away from a stimulus;
  K3  that phase PRECEDES the cognitive/conscious phase;
  K4  anabolic precedes catabolic within a cycle.

Model A position space is F2^3 with coordinates (a, v, r).  The map:

  a  accepting=0 / producing=1   <->  anabolic / catabolic      derived
       (typemap.POSITION_POLARITY is already a == 0; checked)
  r  mental=0 / vital=1          <->  cognitive / affective     derived
       (OIG C.3 names the axis conscious/automatic)
  v  valued=0 / unvalued=1       <->  toward / away             proposed_completion
       (reads "valued" as approach; no source states it)

Consequences (checked):
  * K3 and K4 orient two axes: r runs 1 -> 0, a runs 0 -> 1.
    metabolism R3 (vital before mental) and R4 (accepting charges
    producing) were already so oriented.
  * v receives no ordering from Kępiński.  V5: the Archetypal Shadow
    Complex orients it -- integration runs dystonic -> syntonic -- and
    the estafette never crosses it (clock.py), so v is the axis of
    development rather than of oscillation.
  * The sourced Model G chord A6 -> A1 -> A8 is NOT monotone in this
    orientation: A6->A1 runs catabolic->anabolic, A1->A8 runs
    cognitive->affective.  The only sourced energy path is a return
    edge on each axis.  A flow law on the chords must be a cycle, not
    a gradient on the cube.

Status of the whole: this file states polarity and direction.  It
states no quantity.  There is still no energy.
"""
from __future__ import annotations
from pyref.core import POS_COORD, G_CHORDS_A

SIGNATURE_NAMES = {
    "a": ("anabolic", "catabolic"),
    "v": ("toward", "away"),
    "r": ("cognitive_second", "affective_first"),
}
STATUS = {"a": "derived", "r": "derived", "v": "proposed_completion"}

# Orientation Kępiński gives.  None = no ordering supplied.
ORIENTATION = {"a": (0, 1), "r": (1, 0),
               "v": (1, 0)}   # V5: dystonic -> syntonic, the integration direction
                              # (Archetypal Shadow Complex: "converting the Savage
                              # into a figure of light"); NOT from Kepinski
ORIENTATION_SOURCE = {"a": "Kepinski K4", "r": "Kepinski K3",
                      "v": "Archetypal Shadow Complex, integration of the dystonic"}


def signature(p: int) -> dict:
    a, v, r = POS_COORD[p]
    return {"a": SIGNATURE_NAMES["a"][a], "v": SIGNATURE_NAMES["v"][v],
            "r": SIGNATURE_NAMES["r"][r]}


def flips(p: int, q: int) -> dict:
    return {k: x ^ y for k, x, y in zip("avr", POS_COORD[p], POS_COORD[q])}


def monotone(p: int, q: int) -> dict:
    """Per axis: True/False if the step follows/violates Kępiński's
    orientation, None if the axis is not flipped or not oriented."""
    out = {}
    for i, k in enumerate("avr"):
        if POS_COORD[p][i] == POS_COORD[q][i] or ORIENTATION[k] is None:
            out[k] = None
        else:
            out[k] = POS_COORD[p][i] == ORIENTATION[k][0]
    return out


def chord_report() -> list:
    return [{"from": f, "to": t, "flips": flips(f, t), "monotone": monotone(f, t)}
            for f, t in G_CHORDS_A]
