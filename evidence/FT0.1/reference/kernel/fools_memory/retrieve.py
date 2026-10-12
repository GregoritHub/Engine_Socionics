"""Fool's Memory Path — retrieval.

  Locate by residue + suit + rank.
  Replay the loop (A -> apex -> B -> C -> A) until the missing vertex snaps.
  Run the vertical check (+9 operator).
  Run the horizontal check (suit translation).

The Fool (value 0) is the cursor walking these functions; it never
appears as an address, so no function here accepts residue 0.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Optional

from . import schema
from .schema import LoopError

REPLAY_ORDER = ("A", "apex", "B", "C", "A")


def locate(loops: Iterable[Mapping], residue: Optional[int] = None,
           suit: Optional[str] = None, rank=None) -> list:
    """Filter loops by any subset of the (residue, suit, rank) address."""
    if residue == schema.FOOL:
        raise LoopError("fool_not_addressable")
    want_rank = schema.normalize_rank(rank) if rank is not None else None
    out = []
    for lp in loops:
        if residue is not None and lp["residue"] != residue:
            continue
        if suit is not None and lp["suit"] != suit:
            continue
        if want_rank is not None and lp["rank"] != want_rank:
            continue
        out.append(lp)
    return out


def replay(loop: Mapping) -> list:
    """The walk: A -> apex -> B -> C -> A, as (station, value) pairs."""
    lp = schema.validate_loop(loop)
    seq = []
    for station in REPLAY_ORDER:
        value = lp["apex"] if station == "apex" else lp["vertices"][station]
        seq.append((station, value))
    return seq


def snap_missing(loops: Iterable[Mapping], residue: int, suit: str, rank,
                 known: Mapping) -> dict:
    """Given two known vertices at an address, replay stored loops at that
    address until the missing vertex snaps into place.

    known: e.g. {"A": "obligation", "C": "penalty"}. Returns
    {"loop_id", "missing", "value"}. Errors if nothing matches or the
    match is ambiguous.
    """
    if not isinstance(known, Mapping) or len(known) != 2:
        raise LoopError("need_two_known_vertices")
    names = set(known)
    if not names <= set(schema.VERTEX_NAMES):
        raise LoopError("invalid_vertices", ",".join(sorted(names)))
    missing = (set(schema.VERTEX_NAMES) - names).pop()
    hits = []
    for lp in locate(loops, residue, suit, rank):
        if all(lp["vertices"][k] == v for k, v in known.items()):
            hits.append(lp)
    if not hits:
        raise LoopError("no_snap", "no loop matches the known vertices")
    values = {lp["vertices"][missing] for lp in hits}
    if len(values) > 1:
        raise LoopError("ambiguous_snap", ",".join(sorted(values)))
    lp = hits[0]
    return {"loop_id": lp["id"], "missing": missing,
            "value": lp["vertices"][missing]}


def vertical_check(loop: Mapping) -> dict:
    """The +9 operator: verify the phase ladder of the loop's residue class
    inside its band, and pair each available phase value with its reading
    (Ego and Identity are derived positions; only Super-Ego is stored).
    """
    lp = schema.validate_loop(loop)
    pv = schema.phase_values(lp["residue"], lp["band"])
    se = pv["super_ego"]
    if se % 9 != lp["residue"] % 9:
        raise LoopError("residue_mismatch")  # unreachable by construction
    ladder = {}
    for phase, value in pv.items():
        if value % 9 != lp["residue"] % 9:
            raise LoopError("broken_ladder", phase)
        ladder[phase] = {
            "value": value,
            "reading": lp["phase_readings"].get(phase),
            "derived": phase != "super_ego",
        }
    return {"residue": lp["residue"], "band": lp["band"], "ladder": ladder}


def horizontal_check(loop: Mapping,
                     loops: Optional[Iterable[Mapping]] = None) -> dict:
    """Suit translation: the partner-domain address of this loop, and (when
    a register slice is supplied) any loops already stored there."""
    lp = schema.validate_loop(loop)
    partner = schema.suit_partner(lp["suit"])
    addr = (lp["residue"], partner, lp["rank"])
    translated = []
    if loops is not None:
        translated = locate(loops, *addr)
    return {"partner_suit": partner, "address": addr,
            "translated_loops": [t["id"] for t in translated]}
