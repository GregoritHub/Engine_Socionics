"""Tower sealing — one-way freeze of a developmental state.

A seal marks a tower configuration as witnessed-and-closed. Sealing is
permanent by design: there is deliberately no unseal() in this module.
A sealed tower can still be read, summarized, and carried on a Holon,
but every mutating operation in tree.py rejects it (tower_sealed).
"""

from __future__ import annotations

from . import schema
from .schema import TowerError


def seal(tower: dict, at: int) -> dict:
    tower = schema.validate_cape_phase(tower)
    if tower["sealed"]:
        raise TowerError("already_sealed")
    if not isinstance(at, int) or at < 0:
        raise TowerError("invalid_seal_time", str(at))
    out = dict(tower)
    out["sealed"] = True
    out["sealed_at"] = at
    return schema.validate_cape_phase(out)


def is_sealed(tower: dict) -> bool:
    return bool(schema.validate_cape_phase(tower)["sealed"])
