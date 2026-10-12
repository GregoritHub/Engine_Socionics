"""Holon Tower operations — pure functions on tower_v1 payloads.

All functions are total-or-error and return NEW payloads (no mutation).
Application to a live Holon goes through the kernel's transition() via a
materialized single-rule table (see materialize_rule); this preserves the
trajectory-consistency invariant without touching pyref.

Legality rules implemented here:
  * a cell may be activated only if its vMeme is at most one level above
    the current center (no skipped stages) and not already active;
  * the center advances only when all four quadrants of the current
    center are active (all-quadrant ascent) AND bloom_stage has reached
    at least "Apply"; on advance, bloom resets to "Remember";
  * bloom_stage is monotone non-decreasing within a center;
  * a sealed tower rejects every mutation.
"""

from __future__ import annotations

from . import schema
from .schema import (BLOOM_STAGES, QUADRANTS, VMEMES, TowerError,
                     bloom_index, vmeme_index)

ADVANCE_MIN_BLOOM = "Apply"


def new_tower(center: str = "L1") -> dict:
    """A fresh, legal tower: center cell (I quadrant) active, bloom at start."""
    tower = {
        "version": schema.VERSION,
        "center": center,
        "active_cells": [{"vmeme": center, "quadrant": "I"}],
        "bloom_stage": BLOOM_STAGES[0],
        "sealed": False,
        "sealed_at": None,
    }
    return schema.validate_cape_phase(tower)


def new_shells() -> dict:
    return schema.validate_shells({
        "version": schema.VERSION,
        "active_shells": [],
        "particularity_guard": True,
        "el_roi_active": False,
        "notes": {},
    })


def _guard_unsealed(tower: dict):
    if tower.get("sealed"):
        raise TowerError("tower_sealed")


def is_active(tower: dict, vmeme: str, quadrant: str) -> bool:
    return any(c["vmeme"] == vmeme and c["quadrant"] == quadrant
               for c in tower["active_cells"])


def activate_cell(tower: dict, vmeme: str, quadrant: str) -> dict:
    tower = schema.validate_cape_phase(tower)
    _guard_unsealed(tower)
    if quadrant not in QUADRANTS:
        raise TowerError("invalid_quadrant", str(quadrant))
    vi = vmeme_index(vmeme)
    ci = vmeme_index(tower["center"])
    if vi > ci + 1:
        raise TowerError("skips_level",
                         "%s beyond center %s+1" % (vmeme, tower["center"]))
    if is_active(tower, vmeme, quadrant):
        raise TowerError("cell_already_active", "%s/%s" % (vmeme, quadrant))
    out = dict(tower)
    out["active_cells"] = tower["active_cells"] + [
        {"vmeme": vmeme, "quadrant": quadrant}]
    return schema.validate_cape_phase(out)


def set_bloom(tower: dict, stage: str) -> dict:
    tower = schema.validate_cape_phase(tower)
    _guard_unsealed(tower)
    if bloom_index(stage) < bloom_index(tower["bloom_stage"]):
        raise TowerError("bloom_regression",
                         "%s < %s" % (stage, tower["bloom_stage"]))
    out = dict(tower)
    out["bloom_stage"] = stage
    return schema.validate_cape_phase(out)


def can_advance(tower: dict) -> bool:
    if tower.get("sealed"):
        return False
    if vmeme_index(tower["center"]) >= len(VMEMES) - 1:
        return False
    if bloom_index(tower["bloom_stage"]) < bloom_index(ADVANCE_MIN_BLOOM):
        return False
    return all(is_active(tower, tower["center"], q) for q in QUADRANTS)


def advance_center(tower: dict) -> dict:
    tower = schema.validate_cape_phase(tower)
    _guard_unsealed(tower)
    if not can_advance(tower):
        raise TowerError("advance_illegal", tower["center"])
    nxt = VMEMES[vmeme_index(tower["center"]) + 1]
    out = dict(tower)
    out["center"] = nxt
    out["bloom_stage"] = BLOOM_STAGES[0]
    if not is_active(tower, nxt, "I"):
        out["active_cells"] = tower["active_cells"] + [
            {"vmeme": nxt, "quadrant": "I"}]
    return schema.validate_cape_phase(out)


def activate_shell(shells: dict, name: str) -> dict:
    shells = schema.validate_shells(shells)
    if not isinstance(name, str) or not name:
        raise TowerError("invalid_shell_name", str(name))
    if name in shells["active_shells"]:
        raise TowerError("shell_already_active", name)
    out = dict(shells)
    out["active_shells"] = shells["active_shells"] + [name]
    return schema.validate_shells(out)


# ---------------------------------------------------------------------------
# Kernel application — computed deltas go through transition()
# ---------------------------------------------------------------------------

def state_delta(tower: dict = None, shells: dict = None) -> dict:
    """Build a kernel StateDelta carrying validated tower payloads."""
    delta = {}
    if tower is not None:
        delta["cape_phase"] = schema.validate_cape_phase(tower)
    if shells is not None:
        delta["shells"] = schema.validate_shells(shells)
    if not delta:
        raise TowerError("empty_delta")
    return delta


def materialize_rule(archetype: str, intention: str, event: str,
                     tower: dict = None, shells: dict = None) -> dict:
    """A one-rule table, legal under the kernel's transition(), carrying a
    computed developmental delta. The rule table stays an explicit argument
    (no hidden globals), so trajectory consistency is preserved: the change
    lands only via transition(intention, event)."""
    return {"rules": [{
        "archetype": archetype,
        "intention": intention,
        "event": event,
        "state_delta": state_delta(tower=tower, shells=shells),
    }]}
