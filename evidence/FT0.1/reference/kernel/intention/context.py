"""Generative intention layer — context assembly (spec 6).

assemble() builds the three-pillar context packet from a live Holon plus
its memory register slice. It reads the kernel only through public API
(observe, pure_projection) and never reaches into children or siblings.

Hard invariant (spec 9, "three pillars required"): a packet is COMPLETE
only when Identity, Development, and Memory are all present. assemble()
always reports what it found; require_complete() is the gate the
generator uses before emitting any intention.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Optional

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyref import holon as H

from holon_tower import schema as tower_schema


class ContextError(Exception):
    def __init__(self, reason: str, detail: str = ""):
        self.reason = reason
        self.detail = detail
        super().__init__(reason if not detail else "%s: %s" % (reason, detail))


def _envelope_summary(env) -> dict:
    return {
        "v": list(env.v),
        "n": list(env.n),
        "k": sorted(env.k),
        "parity": env.p,
        "depth": list(env.depth),
        "r_present": env.r is not None,
    }


def assemble(holon, register, *, world_observation: Optional[Mapping] = None,
             other_holons: Optional[Iterable] = None,
             relevant_residues: Optional[list] = None,
             recent_n: int = 3) -> dict:
    """Assemble the context packet of spec 6 from the three pillars."""
    proj = H.pure_projection(holon)
    obs = H.observe(holon)

    identity = {
        "gamma": holon.gamma,
        "seat": holon.pure_state.seat,
        "obs_summary": _envelope_summary(obs),
        "pure_projection": proj,
    }

    development = None
    cape = holon.pure_state.cape_phase
    if cape is not None:
        tower = tower_schema.validate_any(cape)
        if tower["version"] == tower_schema.VERSION_V2:
            development = {
                "version": tower["version"],
                "altitude": tower["altitude"],
                "retained": tower["retained"],
                "dwelling": tower["dwelling"],
                "native_perspective": tower["native_perspective"],
                "scale": tower["scale"],
            }
        else:
            development = {
                "version": tower["version"],
                "center": tower["center"],
                "active_cells": tower["active_cells"],
                "bloom_stage": tower["bloom_stage"],
                "sealed": tower["sealed"],
            }

    loops = register.loops(holon.id)
    hist = register.residue_histogram(holon.id)
    if relevant_residues is None:
        relevant_residues = sorted(hist, key=lambda r: (-hist[r], r))[:2]
    memory = None
    if loops:
        memory = {
            "active_loops": loops,
            "recently_replayed": register.recently_replayed(holon.id, recent_n),
            "relevant_residues": relevant_residues,
        }

    others = []
    for ref in (other_holons or []):
        # parent-side summaries only: id + envelope, never private state
        others.append({"id": ref.id,
                       "summary": _envelope_summary(ref.summary),
                       "last_seen": ref.last_seen})

    return {
        "holon_id": holon.id,
        "archetype": holon.archetype,
        "identity": identity,
        "development": development,
        "memory": memory,
        "world_observation": dict(world_observation or {}),
        "other_holons": others,
    }


def require_complete(packet: Mapping) -> dict:
    """The three-pillars gate. Raises unless Identity + Development + Memory
    are all present in the packet."""
    missing = []
    if not packet.get("identity"):
        missing.append("identity")
    if not packet.get("development"):
        missing.append("development")
    if not packet.get("memory"):
        missing.append("memory")
    if missing:
        raise ContextError("incomplete_pillars", ",".join(missing))
    return dict(packet)
