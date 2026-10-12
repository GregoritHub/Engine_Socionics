"""The internal clock: the estafette as relay order.

Source: UMA section 10 gives R(a,v,r) = (r, v, 1+a) (kernel ESTAFETTE,
source_defined) and calls the group it generates the dynamical group.
Its orbits on positions are two 4-cycles (derived, checked):

    valued    1 -> 5 -> 6 -> 2 -> 1     leading, suggestive, activating, creative
    unvalued  3 -> 7 -> 8 -> 4 -> 3     role, ignoring, demonstrative, vulnerable

Reading (derived from the name and the kernel's own use: an estafette is
a relay): the seat is the position currently holding the relay, and it
advances by R each tick.  Each step crosses one axis; a and r are each
traversed once forward and once back per lap; v is never crossed.  The
two orbits are the two v-classes.  So the estafette is the oscillation
Kepinski requires, and v is not part of it -- v is crossed only by
development (integration, Archetypal Shadow Complex), which orients it
dystonic -> syntonic.

What the seat does: when the seat is on a mental position, that block
is the engaged intention (the relay is there).  On a vital position the
prior rule applies.  Orbit switching (proposed_completion, A23): under
Super-Ego pressure with no Ego charge the relay drops to the unvalued
orbit at 3; it returns to the valued orbit at 1 once nothing is pending.

`seat` is now read, and written back into the kernel Holon through
commit() as a state_delta, which PureState already accepts.
"""
from __future__ import annotations
from dataclasses import replace
from pyref.core import ESTAFETTE, POS_COORD, COORD_POS, ACCESS
from .state import State
from .handler import BLOCK, position_of_aspect

VALUED_ORBIT = (1, 5, 6, 2)
UNVALUED_ORBIT = (3, 7, 8, 4)

# V5.2 (A23 refined): with RELAY_GATE the relay drops to the Super-Ego under
# pressure only while the complementary perspective is NOT retained.  Once
# it is, Super-Ego pressure is met from the valued lap (Shell Geometry s.18:
# "no longer only external pressure").  Instrument switch; default V5.
RELAY_GATE = False


def advance(p: int) -> int:
    return COORD_POS[ESTAFETTE(POS_COORD[p])]


def orbit(p: int) -> tuple:
    out, q = [], p
    while q not in out:
        out.append(q); q = advance(q)
    return tuple(out)


def pressure(st: State) -> bool:
    pending_se = any(BLOCK[position_of_aspect(st, pk.aspect)] == "super_ego" for pk in st.pending)
    return pending_se and not st.at(2).charge


def step(st: State) -> State:
    """Advance the relay; switch orbit under pressure (A23)."""
    s = st.seat
    gated = RELAY_GATE and _complement_retained(st)
    if ACCESS[s]["valued"] and pressure(st) and not gated:
        s = 3
    elif st.serpent:
        s = advance(s)             # the Serpent holds the relay on the unvalued lap
        st = replace(st, serpent=st.serpent - 1)
    elif not ACCESS[s]["valued"] and not st.pending:
        s = 1
    else:
        s = advance(s)
    return replace(st, seat=s)


def _complement_retained(st: State) -> bool:
    from crux.typemap import type_map
    return type_map(st.tim)["complementary_perspective"] in st.retained


def engaged_block(st: State):
    """The block the relay engages, or None if the seat is vital."""
    return BLOCK[st.seat] if ACCESS[st.seat]["frame"] == "mental" else None
