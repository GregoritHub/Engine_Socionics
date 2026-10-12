"""Holon Tower schema (tower_v1) — Development pillar of Living Engine V2.

The Tower is a 36-cell grid: 9 vMemes (Spiral Dynamics L1..L9) x 4 AQAL
quadrants (I, We, It, Its). Developmental state is carried EXCLUSIVELY in
the kernel's existing opaque optional fields (cape_phase, shells); this
module validates and constructs those payloads. It never imports or
modifies pyref.

Conditional: a data-shape contract, not a finding about development.
"""

from __future__ import annotations

from typing import Any, Mapping

VERSION = "tower_v1"
VERSION_V2 = "tower_v2"

# tower_v1 is retained for compatibility only. It advances on internal
# activity with no demand term, never consults Shell state, and treats its
# nine levels as primitive coordinates -- all three of which the governing
# source forbids. New work should carry a tower_v2 payload built by
# holon_tower.altitude.altitude_phase().

VMEMES = ("L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9")
QUADRANTS = ("I", "We", "It", "Its")
BLOOM_STAGES = ("Remember", "Understand", "Apply", "Analyze",
                "Evaluate", "Create")

GRID_CELLS = tuple((v, q) for v in VMEMES for q in QUADRANTS)  # 36 cells


class TowerError(Exception):
    def __init__(self, reason: str, detail: str = ""):
        self.reason = reason
        self.detail = detail
        super().__init__(reason if not detail else "%s: %s" % (reason, detail))


def vmeme_index(v: str) -> int:
    if v not in VMEMES:
        raise TowerError("invalid_vmeme", str(v))
    return VMEMES.index(v)


def bloom_index(b: str) -> int:
    if b not in BLOOM_STAGES:
        raise TowerError("invalid_bloom_stage", str(b))
    return BLOOM_STAGES.index(b)


def _validate_cell(cell) -> dict:
    if not isinstance(cell, Mapping):
        raise TowerError("invalid_cell", str(cell))
    v = cell.get("vmeme")
    q = cell.get("quadrant")
    if v not in VMEMES:
        raise TowerError("invalid_vmeme", str(v))
    if q not in QUADRANTS:
        raise TowerError("invalid_quadrant", str(q))
    extra = set(cell) - {"vmeme", "quadrant"}
    if extra:
        raise TowerError("unknown_cell_field", ",".join(sorted(extra)))
    return {"vmeme": v, "quadrant": q}


def validate_cape_phase(obj: Any) -> dict:
    """Validate a tower_v1 cape_phase payload. Returns a normalized copy."""
    if not isinstance(obj, Mapping):
        raise TowerError("invalid_cape_phase", "not_a_mapping")
    if obj.get("version") != VERSION:
        raise TowerError("wrong_version", str(obj.get("version")))
    center = obj.get("center")
    if center not in VMEMES:
        raise TowerError("invalid_center", str(center))
    cells_raw = obj.get("active_cells")
    if not isinstance(cells_raw, list):
        raise TowerError("invalid_active_cells")
    cells = [_validate_cell(c) for c in cells_raw]
    seen = set()
    for c in cells:
        key = (c["vmeme"], c["quadrant"])
        if key in seen:
            raise TowerError("duplicate_cell", "%s/%s" % key)
        seen.add(key)
    bloom = obj.get("bloom_stage")
    if bloom not in BLOOM_STAGES:
        raise TowerError("invalid_bloom_stage", str(bloom))
    sealed = obj.get("sealed")
    if not isinstance(sealed, bool):
        raise TowerError("invalid_sealed", str(sealed))
    sealed_at = obj.get("sealed_at")
    if sealed and not isinstance(sealed_at, int):
        raise TowerError("sealed_requires_timestamp")
    if not sealed and sealed_at is not None:
        raise TowerError("unsealed_has_timestamp")
    extra = set(obj) - {"version", "center", "active_cells", "bloom_stage",
                        "sealed", "sealed_at"}
    if extra:
        raise TowerError("unknown_field", ",".join(sorted(extra)))
    return {
        "version": VERSION,
        "center": center,
        "active_cells": cells,
        "bloom_stage": bloom,
        "sealed": sealed,
        "sealed_at": sealed_at,
    }


def validate_shells(obj: Any) -> dict:
    """Validate a tower_v1 shells payload. particularity_guard must be True.

    Hard invariant (spec 9): developmental operations must never erase
    distinction. The guard flag is the carrier of that promise; a payload
    that switches it off is rejected outright.
    """
    if not isinstance(obj, Mapping):
        raise TowerError("invalid_shells", "not_a_mapping")
    if obj.get("version") != VERSION:
        raise TowerError("wrong_version", str(obj.get("version")))
    shells = obj.get("active_shells")
    if not isinstance(shells, list) or not all(
            isinstance(s, str) and s for s in shells):
        raise TowerError("invalid_active_shells")
    if len(set(shells)) != len(shells):
        raise TowerError("duplicate_shell")
    if obj.get("particularity_guard") is not True:
        raise TowerError("particularity_guard_disabled")
    if not isinstance(obj.get("el_roi_active"), bool):
        raise TowerError("invalid_el_roi_active")
    notes = obj.get("notes")
    if not isinstance(notes, Mapping):
        raise TowerError("invalid_notes")
    extra = set(obj) - {"version", "active_shells", "particularity_guard",
                        "el_roi_active", "notes"}
    if extra:
        raise TowerError("unknown_field", ",".join(sorted(extra)))
    return {
        "version": VERSION,
        "active_shells": list(shells),
        "particularity_guard": True,
        "el_roi_active": bool(obj["el_roi_active"]),
        "notes": {str(k): v for k, v in notes.items()},
    }


# ---------------------------------------------------------------------------
# tower_v2 -- generated altitude (see holon_tower/altitude.py for the law)
# ---------------------------------------------------------------------------

def validate_altitude_phase(obj) -> dict:
    """Validate a tower_v2 cape_phase payload. Returns a normalized copy."""
    if not isinstance(obj, Mapping):
        raise TowerError("invalid_cape_phase", "not_a_mapping")
    if obj.get("version") != VERSION_V2:
        raise TowerError("wrong_version", str(obj.get("version")))
    from crux.perspectives import PERSPECTIVES
    retained = obj.get("retained")
    if not isinstance(retained, (list, tuple)) or not retained:
        raise TowerError("invalid_retained")
    bad = set(retained) - set(PERSPECTIVES)
    if bad:
        raise TowerError("invalid_perspective", ",".join(sorted(bad)))
    if len(set(retained)) != len(retained):
        raise TowerError("duplicate_perspective")
    native = obj.get("native_perspective")
    if native not in PERSPECTIVES:
        raise TowerError("invalid_native_perspective", str(native))
    if native not in retained:
        raise TowerError("native_not_retained", str(native))
    dwelling = obj.get("dwelling")
    if dwelling not in retained:
        raise TowerError("dwelling_not_retained", str(dwelling))
    alt = obj.get("altitude")
    if isinstance(alt, bool) or not isinstance(alt, int) or alt < 0:
        raise TowerError("invalid_altitude", str(alt))
    if obj.get("scale") not in ("individual", "collective"):
        raise TowerError("invalid_scale", str(obj.get("scale")))
    history = obj.get("history", [])
    if not isinstance(history, list):
        raise TowerError("invalid_history")
    extra = set(obj) - {"version", "tim", "retained", "dwelling", "altitude",
                        "native_perspective", "scale", "history"}
    if extra:
        raise TowerError("unknown_field", ",".join(sorted(extra)))
    return {
        "version": VERSION_V2,
        "tim": obj.get("tim"),
        "retained": sorted(retained),
        "dwelling": dwelling,
        "altitude": alt,
        "native_perspective": native,
        "scale": obj["scale"],
        "history": [dict(h) for h in history],
    }


def validate_any(obj) -> dict:
    """Dispatch on payload version. Callers that must accept either
    generation of the Development pillar use this."""
    if not isinstance(obj, Mapping):
        raise TowerError("invalid_cape_phase", "not_a_mapping")
    v = obj.get("version")
    if v == VERSION:
        return validate_cape_phase(obj)
    if v == VERSION_V2:
        return validate_altitude_phase(obj)
    raise TowerError("wrong_version", str(v))
