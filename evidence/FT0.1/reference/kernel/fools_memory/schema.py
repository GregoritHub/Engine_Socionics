"""Fool's Memory Path — Loop schema (fools_v1). Memory pillar of V2.

Core objects from the operator's manual:
  Loop     three vertices (A, B, C) + one context apex.
           Replay order: A -> apex -> B -> C -> A.
  Residue  r in 1..9, the vertical column of meaning under the +9 operator.
           Value 0 is the Fool: the cursor, never a cell, never an address.
  Suit     one of eight horizontal domains; Tarot and playing suits pair
           off under the horizontal translation.
  Rank     structural density, 1..10 plus courts (Page..King -> 11..14).
  Band     "lo-hi" inclusive value window. Phase values are the members of
           the residue class inside the band: Super-Ego is the smallest,
           Ego is Super-Ego + 9, Identity is Super-Ego + 18, each present
           only "where band permits".

Addressability doctrine (spec 9): loops are STORED at Super-Ego rank
only; Ego and Identity readings are derived. A loop whose declared
storage phase is anything but super_ego is rejected.
"""

from __future__ import annotations

import uuid
from typing import Any, Mapping, Tuple

VERSION = "fools_v1"

RESIDUES = tuple(range(1, 10))
FOOL = 0  # cursor only — never a storage address

TAROT_SUITS = ("Cup", "Sword", "Coin", "Wand")
PLAYING_SUITS = ("Heart", "Spade", "Diamond", "Club")
SUITS = TAROT_SUITS + PLAYING_SUITS

# Horizontal translation partners (an involution on the eight suits).
SUIT_PARTNER = {
    "Cup": "Heart", "Heart": "Cup",
    "Sword": "Spade", "Spade": "Sword",
    "Coin": "Diamond", "Diamond": "Coin",
    "Wand": "Club", "Club": "Wand",
}

COURTS = {"Page": 11, "Knight": 12, "Queen": 13, "King": 14}
RANK_MIN, RANK_MAX = 1, 14

PHASES = ("super_ego", "ego", "identity")
VERTEX_NAMES = ("A", "B", "C")


class LoopError(Exception):
    def __init__(self, reason: str, detail: str = ""):
        self.reason = reason
        self.detail = detail
        super().__init__(reason if not detail else "%s: %s" % (reason, detail))


def new_id() -> str:
    return uuid.uuid4().hex


def suit_partner(suit: str) -> str:
    if suit not in SUIT_PARTNER:
        raise LoopError("invalid_suit", str(suit))
    return SUIT_PARTNER[suit]


def normalize_rank(rank) -> int:
    """Accept 1..10, 11..14, or court names; return the integer rank."""
    if isinstance(rank, str):
        if rank not in COURTS:
            raise LoopError("invalid_rank", rank)
        return COURTS[rank]
    if isinstance(rank, bool) or not isinstance(rank, int):
        raise LoopError("invalid_rank", str(rank))
    if not RANK_MIN <= rank <= RANK_MAX:
        raise LoopError("invalid_rank", str(rank))
    return rank


def parse_band(band: str) -> Tuple[int, int]:
    if not isinstance(band, str) or "-" not in band:
        raise LoopError("invalid_band", str(band))
    lo_s, hi_s = band.split("-", 1)
    try:
        lo, hi = int(lo_s), int(hi_s)
    except ValueError:
        raise LoopError("invalid_band", band)
    if lo < 1 or hi < lo:
        raise LoopError("invalid_band", band)
    return lo, hi


def phase_values(residue: int, band: str) -> dict:
    """Members of the residue class inside the band, keyed by phase.

    super_ego is the smallest value v in [lo, hi] with v % 9 == residue % 9
    (and v >= 1); ego = v + 9 and identity = v + 18 where the band permits.
    """
    if residue == FOOL:
        raise LoopError("fool_not_addressable")
    if residue not in RESIDUES:
        raise LoopError("invalid_residue", str(residue))
    lo, hi = parse_band(band)
    se = None
    v = residue
    while v < lo:
        v += 9
    if v <= hi:
        se = v
    if se is None:
        raise LoopError("band_excludes_residue", "%s not in %s" % (residue, band))
    out = {"super_ego": se}
    if se + 9 <= hi:
        out["ego"] = se + 9
    if se + 18 <= hi:
        out["identity"] = se + 18
    return out


def available_phases(residue: int, band: str) -> tuple:
    return tuple(p for p in PHASES if p in phase_values(residue, band))


def validate_loop(obj: Any) -> dict:
    """Validate and normalize a fools_v1 Loop. Enforces the addressability
    doctrine and the Fool-is-cursor rule."""
    if not isinstance(obj, Mapping):
        raise LoopError("invalid_loop", "not_a_mapping")
    if obj.get("version") != VERSION:
        raise LoopError("wrong_version", str(obj.get("version")))
    loop_id = obj.get("id")
    if not isinstance(loop_id, str) or not loop_id:
        raise LoopError("invalid_id")
    residue = obj.get("residue")
    if residue == FOOL:
        raise LoopError("fool_not_addressable")
    if residue not in RESIDUES:
        raise LoopError("invalid_residue", str(residue))
    suit = obj.get("suit")
    if suit not in SUITS:
        raise LoopError("invalid_suit", str(suit))
    rank = normalize_rank(obj.get("rank"))
    band = obj.get("band")
    pv = phase_values(residue, band)  # validates band vs residue

    vertices = obj.get("vertices")
    if not isinstance(vertices, Mapping):
        raise LoopError("invalid_vertices")
    if set(vertices) != set(VERTEX_NAMES):
        raise LoopError("invalid_vertices", "need exactly A, B, C")
    vals = {}
    for k in VERTEX_NAMES:
        v = vertices[k]
        if not isinstance(v, str) or not v:
            raise LoopError("invalid_vertex", k)
        vals[k] = v
    if len(set(vals.values())) != 3:
        raise LoopError("degenerate_loop", "vertices must be distinct")
    apex = obj.get("apex")
    if not isinstance(apex, str) or not apex:
        raise LoopError("invalid_apex")

    readings = obj.get("phase_readings")
    if not isinstance(readings, Mapping):
        raise LoopError("invalid_phase_readings")
    if "super_ego" not in readings:
        raise LoopError("missing_super_ego_reading")
    for phase, text in readings.items():
        if phase not in PHASES:
            raise LoopError("invalid_phase", str(phase))
        if phase not in pv:
            raise LoopError("phase_outside_band", phase)
        if not isinstance(text, str) or not text:
            raise LoopError("empty_reading", phase)

    storage_phase = obj.get("storage_phase", "super_ego")
    if storage_phase != "super_ego":
        raise LoopError("store_super_ego_only", str(storage_phase))

    created = obj.get("created_at", 0)
    replayed = obj.get("last_replayed", 0)
    if not isinstance(created, int) or not isinstance(replayed, int):
        raise LoopError("invalid_timestamp")
    strength = obj.get("strength", 1.0)
    if isinstance(strength, bool) or not isinstance(strength, (int, float)):
        raise LoopError("invalid_strength")
    if strength < 0:
        raise LoopError("invalid_strength", str(strength))

    extra = set(obj) - {"id", "version", "residue", "suit", "rank", "band",
                        "vertices", "apex", "phase_readings", "created_at",
                        "last_replayed", "strength", "storage_phase"}
    if extra:
        raise LoopError("unknown_field", ",".join(sorted(extra)))

    return {
        "id": loop_id,
        "version": VERSION,
        "residue": residue,
        "suit": suit,
        "rank": rank,
        "band": band,
        "vertices": vals,
        "apex": apex,
        "phase_readings": {p: readings[p] for p in PHASES if p in readings},
        "created_at": created,
        "last_replayed": replayed,
        "strength": float(strength),
        "storage_phase": "super_ego",
    }


def address(loop: Mapping) -> Tuple[int, str, int]:
    """The retrieval address: (residue, suit, rank)."""
    return (loop["residue"], loop["suit"], loop["rank"])
