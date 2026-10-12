"""Fool's Memory Path — encoding. The four decisions from the Manual:

  1. Decide phases needed        -> choose band
  2. Pick suit by domain         -> suit
  3. Pick rank by edge count     -> rank
  4. Build A-B-C-apex loop constrained by the residue's verb chain

Encoding always produces a Super-Ego-addressed loop (addressability
doctrine); Ego/Identity readings ride along only where the band permits.
"""

from __future__ import annotations

from typing import Mapping, Optional, Sequence

from . import schema
from .schema import LoopError


def choose_band(residue: int, phases_needed: Sequence[str]) -> str:
    """Decision 1: the minimal band whose residue class carries exactly the
    requested phases (an explicit wider band may always be supplied
    instead — e.g. the Manual's '4-18')."""
    need = list(phases_needed)
    if not need or "super_ego" not in need:
        raise LoopError("phases_need_super_ego")
    for p in need:
        if p not in schema.PHASES:
            raise LoopError("invalid_phase", str(p))
    if len(set(need)) != len(need):
        raise LoopError("duplicate_phase", ",".join(sorted(need)))
    wanted = {p for p in need}
    prefix = set(schema.PHASES[:len(wanted)])
    if wanted != prefix:
        raise LoopError("phases_must_be_prefix",
                        "%s is not %s" % (sorted(wanted), sorted(prefix)))
    if residue not in schema.RESIDUES:
        raise LoopError("invalid_residue", str(residue))
    hi = residue
    if "ego" in need:
        hi = residue + 9
    if "identity" in need:
        hi = residue + 18
    return "%d-%d" % (residue, hi)


def encode(*, residue: int, suit: str, edge_count,
           vertices: Mapping, apex: str,
           phase_readings: Mapping,
           phases_needed: Optional[Sequence[str]] = None,
           band: Optional[str] = None,
           created_at: int = 0,
           loop_id: Optional[str] = None) -> dict:
    """Run the four decisions and return a validated Loop.

    Either pass phases_needed (band is derived minimally) or an explicit
    band string. Rank is taken from edge_count (int 1..10 or a court name).
    """
    if (band is None) == (phases_needed is None):
        raise LoopError("band_xor_phases",
                        "give exactly one of band / phases_needed")
    if band is None:
        band = choose_band(residue, phases_needed)
    loop = {
        "id": loop_id or schema.new_id(),
        "version": schema.VERSION,
        "residue": residue,
        "suit": suit,
        "rank": edge_count,
        "band": band,
        "vertices": dict(vertices),
        "apex": apex,
        "phase_readings": dict(phase_readings),
        "created_at": created_at,
        "last_replayed": created_at,
        "strength": 1.0,
        "storage_phase": "super_ego",
    }
    return schema.validate_loop(loop)
