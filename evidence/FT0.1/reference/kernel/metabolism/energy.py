"""Energy signals -- both directions, every position, no quantities.

Sources
  * kernel G_ENERGETIC_NOTE (UMA sections 13/19, source_defined):
      A6  initiates the Leader              (chord A6 -> A1)
      A8  receives an energy boost           (chord A1 -> A8)
      A5  replenishes reserves
      A4  inhibition and energy loss; high resistance to workload
  * Gulenko, "Energy model G in Humanitarian socionics", socioniks.net
    article 113 -- EXTERNAL to the governing documents; admitted here
    as `external_source` and to be added to source_manifest or struck:
      four energy levels by vertical block, as gas/brake pairs
        maximum (+-)  optimum (++)  minimum (-+)  pessimum (--)
  * Kepinski K1: anabolic / catabolic oscillation -- so every position
    has a deficit direction and an overload direction.

Derived (checked exhaustively): with the kernel's G_TO_A permutation,
Gulenko's levels are a function of the position coordinates:

    gas   = 1 XOR v XOR a*r
    brake = v XOR r XOR a*r

On the mental ring valued <-> gas, unvalued <-> brake.  On the vital
ring gas = brake = the kernel's contact bit.

Signals (categorical, per tick):
  deficit(p)   accepting position unfed >= patience   -- anabolic side
  overload(p)  input this tick exceeded the facet law  -- catabolic side

Effects, one per sourced note, all proposed_completion as to mechanism:
  launch    charge at A6 forces Ego engagement next tick (trigger only;
            CONTENT transfer stays gated by retention in chord.py)
  boost     A1 -> A8: the demonstrative "receives an energy boost from
            the Leader" (kernel note, UMA s.19) -- a charging relation,
            wired at reception (R7).  That 8 also FIRES with the Leader
            is this build's reading (A37/C4b, docs/A37_RESEARCH_NET.md);
            both are gas positions; the chord is why 8 is charged when
            1 is fed -- implemented as R4's self-charge on gas + the
            firing set in handler
  replenish deficit at A5 emits the request (was `hunger`)
  brake     overload at A4 inhibits Ego production this tick
"""
from __future__ import annotations
from pyref.core import POS_COORD, G_TO_A, G_ENERGETIC_NOTE
from .state import State

STATUS = {"levels": "external_source:socioniks.net/article/113",
          "effects": "proposed_completion", "formula": "derived"}

LEVEL_BY_G = {1: "maximum", 5: "maximum", 2: "optimum", 6: "optimum",
              3: "minimum", 7: "minimum", 4: "pessimum", 8: "pessimum"}
GAS = {"maximum": 1, "optimum": 1, "minimum": 0, "pessimum": 0}
BRAKE = {"maximum": 0, "optimum": 1, "minimum": 1, "pessimum": 0}
A_TO_G = {a: g for g, a in G_TO_A.items()}


def level(p: int) -> str:
    return LEVEL_BY_G[A_TO_G[p]]


def gas(p: int) -> int:
    a, v, r = POS_COORD[p]
    return 1 ^ v ^ (a & r)


def brake(p: int) -> int:
    a, v, r = POS_COORD[p]
    return v ^ r ^ (a & r)


def note(p: int) -> str:
    return G_ENERGETIC_NOTE.get(A_TO_G[p], "none_sourced")


# ---- signals ---------------------------------------------------------

def deficit(st: State, patience: int) -> frozenset:
    return frozenset(q.index for q in st.positions
                     if q.accepting and q.unfed >= patience)


def overload(st: State) -> frozenset:
    """Positions whose input this tick carried facets they cannot process."""
    return frozenset(q.index for q in st.positions if q.hit)


def signals(st: State, patience: int) -> dict:
    d, o = deficit(st, patience), overload(st)
    return {"deficit": sorted(d), "overload": sorted(o),
            "launch": bool(st.at(6).charge), "brake": 4 in o,
            "replenish": 5 in d}


# ---- effects ---------------------------------------------------------

def braked(st: State) -> bool:
    return 4 in overload(st)
