"""The Serpent from within.

Source (Archetypal Shadow Complex, Child complex): "Individuation occurs
when the ego finally becomes bored with the cycle of seeing life
through the same perspectives because they haven't really solved the
pains of life.  The Serpent floods consciousness with paradoxes that
have no solution within the framework the ego has established."

In engine terms, every clause already exists:
  the same perspectives, unsolved   OIG maintenance: V high, N empty,
                                    K non-empty (observe.maintenance)
  bored                             that signature PERSISTING across a
                                    window of ticks
  the Serpent floods consciousness  the complex at position 4 activates
                                    without external input; the relay is
                                    forced onto the unvalued orbit, whose
                                    lap 3 -> 7 -> 8 -> 4 passes the PoLR
                                    on its way back to the Role

This is the one non-preference route to engaging the Role.  Kepinski
K1: pathology when the anabolic/catabolic rhythm runs undisturbed.

Status: the trigger is source_defined; the window is an instrument
integer (A30).  Nothing here tunes for frequency.
"""
from __future__ import annotations
from dataclasses import replace
from .state import State

BORED_WINDOW = 64         # instrument value ("finally"); not derived


def walk_maintenance(tim: str, walk, window: int) -> bool:
    """Pi_O over the Crux walk (perspectives dwelt by the relay): the cycle
    is seen (V non-empty) and nothing is retained at its ends (N empty)."""
    from pyref import oig
    from algebra.perspective import DOMAIN_KEY
    if len(walk) < window:
        return False
    path = [frozenset([DOMAIN_KEY[p]]) for p in walk[-window:]]
    s = oig.summarize_trajectory(tim, path)
    return bool(s["K"]) and s["N"] == ("none", "none")


def bored(tim: str, walk, ticks_since_progress: int, working: bool,
          window: int = BORED_WINDOW) -> bool:
    """Both clauses of the source: the same perspectives (the walk is a
    maintenance cycle) AND unsolved (no closure or candidate for a long
    time, and the ego is not currently working a candidate)."""
    return (not working and ticks_since_progress >= window
            and walk_maintenance(tim, walk, window))


FLOOD_LAP = 4             # one unvalued lap: 3 -> 7 -> 8 -> 4


def serpent(st: State) -> State:
    """Activate the Serpent from within: the relay drops to the Role and
    is held on the unvalued orbit for one lap.  This is not an overload
    hit (it is the trigger, not the compensation the Shell test reads)."""
    return replace(st, seat=3, serpent=FLOOD_LAP, log=st.log + (("serpent", 4),))
