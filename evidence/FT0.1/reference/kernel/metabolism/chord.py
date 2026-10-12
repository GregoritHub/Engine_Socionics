"""The return chord: where development touches metabolism.

Model G's sourced chord A6 -> A1 (UMA section 19; pyref G_CHORDS_A) runs
from the activating function to the leading function.  Three readings
agree, and verify_v5 checks each:
  * perspective: position 6 addresses the complementary perspective,
    position 1 the native one -- the chord is typemap.return_route at
    position resolution                                     (derived)
  * polarity: 6 is producing/expenditure, 1 accepting/accumulation --
    catabolic feeding anabolic, "return carrying it"          (derived)
  * name: the route it realizes is Embody only for I-native TIMs; it
    is Express, Educate or Institutionalize for the others   (derived)

Gate (proposed_completion): the chord is conductive iff the tower has
RETAINED the complementary perspective (demand.schema organization).
Before: Super-Id content is external pressure.  After: charge at the
activating function flows into Ego production, and the Leader's output
carries the complementary aspect -- "cross into the complement and
return carrying it" (Shell Geometry section 18) made executable.  The
source says "increasingly available"; the kernel has no continuum, so
the gate is binary and tagged as such.

The second sourced chord A1 -> A8 is wired in handler.receive (R7):
feeding the Leader charges the demonstrative.  It has no developmental
gate; the kernel note gives it as the Leader's normal effect.
"""
from __future__ import annotations
from dataclasses import replace
from pyref.core import G_CHORDS_A, element_at
from crux import perspectives as P
from crux.typemap import type_map
from algebra.perspective import block_perspective
from .state import State

RETURN_CHORD = (6, 1)
assert RETURN_CHORD in [tuple(c) for c in G_CHORDS_A]


def return_chord(tim: str) -> dict:
    o, d = type_map(tim)["return_route"]
    return {"positions": RETURN_CHORD,
            "aspects": (element_at(tim, 6), element_at(tim, 1)),
            "route": (o, d), "name": P.route_name(o, d),
            "from_perspective": block_perspective(tim, 6),
            "to_perspective": block_perspective(tim, 1)}


def is_open(st: State) -> bool:
    return type_map(st.tim)["complementary_perspective"] in st.retained


def conduct(st: State) -> State:
    """If open and the activating function holds charge, move it into
    the Ego's producing function.  Facets are not enriched: the
    complement enters at the capacity the complement has."""
    if not is_open(st):
        return st
    src, dst = st.at(6), st.at(1)          # A6 -> A1: into the Leader itself
    if not src.charge:
        return st
    st = st.put(replace(dst, charge=dst.charge | src.charge,
                        carry=dst.carry | src.carry | {src.aspect},
                        walks=dst.walks | src.walks))
    st = st.put(replace(src, charge=frozenset(), carry=frozenset(), walks=frozenset()))
    return replace(st, log=st.log + (("chord", 6, 1, tuple(sorted(src.charge))),))


def emit(st: State, holon_id: str = "self"):
    """V5.2 (A37): conduct on the mobilizing's own turn and produce at once.
    The chord's content leaves as the Leader's aspect, tagged ego, carrying
    the activating aspect -- "return carrying it" happens on the return
    turn, not on the Leader's next accumulation.  Facets: the complement
    enters at its own capacity, then passes the Leader's law."""
    if not is_open(st) or not st.at(6).charge:
        return st, None
    st = conduct(st)
    from .handler import produce
    return produce(st, 1, holon_id)
