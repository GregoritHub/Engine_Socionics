"""Information metabolism, executing.

  packet.py    IE-typed packets with dimensional facets
  state.py     the metabolic state: eight position records, one charge
  handler.py   the five rules, applied to one packet
  exchange.py  transfer between psyches over the relation group
  energy.py    gas/brake law, deficit/overload signals, the four
               sourced effects
  clock.py     the estafette as relay order; seat read and written
  observe.py   Pi_O over a metabolism trajectory
  boredom.py   sustained maintenance activates the Serpent from within
  complex.py   persistent overload activates the complex -> S_C
  chord.py     the return chord A6->A1, gated by tower retention
  tick.py      the generative loop and the kernel commit

Reads pyref/ and algebra/.  Writes into neither.
"""
VERSION = "metabolism_v2"

from algebra.facets import facets_up_to
from .packet import FACETS, FACET_LEVEL, Packet, packet
from .state import State, Position, new_state
from .handler import receive, produce, block_name, is_automatic
from .exchange import landing_position, relation_of, landing_perm
from .chord import return_chord, is_open as chord_open, conduct
from .tick import tick, run, intention_for, commit, REQUEST

__all__ = [
    "VERSION",
    "FACETS", "FACET_LEVEL", "Packet", "packet", "facets_up_to",
    "State", "Position", "new_state",
    "receive", "produce", "block_name", "is_automatic",
    "landing_position", "relation_of", "landing_perm",
    "return_chord", "chord_open", "conduct",
    "tick", "run", "intention_for", "commit", "REQUEST",
]
