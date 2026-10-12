"""Generative intention layer — three pillars resolved to one intention.

`context.py` assembles a context packet from Identity, Development
(tower_v1 or tower_v2, dispatched on payload version) and Memory;
`generate.py` scores candidate intentions against that packet and returns
the winner with its reasons attached.
"""

from . import context, generate

__all__ = ["context", "generate"]
