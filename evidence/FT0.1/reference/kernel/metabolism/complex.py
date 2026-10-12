"""Complex activation: where metabolism meets the Shell.

"An emotion is an affect resulting from the activation of a complex"
(Archetypal Shadow Complex, Clarification).  The metabolism already
computes overload per position -- input the facet law could not
process.  A complex is ACTIVATED at p when overload at p persists for
`window` consecutive ticks (persistence is the Shell Geometry 6.1
requirement: signs must persist through the test; one bad tick is not
a Shell).  The activation's diagnostic appearance is S_C at p; its
projection lands on the complex partner, cast onto Self or Other by
the directive bit.

Status: the threshold `window` is an integer instrument value; the
rule "persistent overload activates the complex" is proposed_completion.
No intensity is computed: iota stays where Shell Geometry put it.
"""
from __future__ import annotations
from algebra.archetype import diagnostic_appearance
from .state import State


def overload_streak(st: State, p: int) -> int:
    """Consecutive ticks (including the current one) with overload at p."""
    q = st.at(p)
    return q.over + (1 if q.hit else 0)


def activated(st: State, window: int = 2) -> list:
    out = []
    for q in st.positions:
        k = overload_streak(st, q.index)
        if k >= window:
            out.append(dict(diagnostic_appearance(st.tim, q.index), streak=k))
    return out
