"""Fool's Memory Path — persistence. The PREFERRED option from spec 5.3:
a dedicated memory register held as a parallel map keyed by Holon id.

The kernel is never touched and Holon.content stays clean for OIG; the
register lives beside the Holon tree, exactly like the parent-side
ChildRef map lives beside children.

Particularity guarantees (spec 9):
  * put() only appends; it never overwrites or deletes an existing loop;
  * duplicate loop ids are rejected;
  * there is no bulk-erase operation; forget() removes exactly one loop
    by id and returns it, so nothing vanishes silently;
  * every read hands back a DEEP copy. Returning the stored dicts made the
    guarantee true at the door and false at the window: a caller could
    rewrite vertices, strength, even residue, without passing through
    validate_loop. put() was already safe against caller aliasing; the read
    path was not.
"""

from __future__ import annotations

import copy
import json
import os
from typing import List

from . import schema
from .schema import LoopError

REGISTER_VERSION = "fools_register_v1"


class MemoryRegister:
    def __init__(self):
        self._loops = {}  # holon_id -> list of loop dicts (append-only)

    # -- write ------------------------------------------------------------

    def put(self, holon_id: str, loop) -> dict:
        if not isinstance(holon_id, str) or not holon_id:
            raise LoopError("invalid_holon_id")
        lp = schema.validate_loop(loop)
        bucket = self._loops.setdefault(holon_id, [])
        if any(x["id"] == lp["id"] for x in bucket):
            raise LoopError("duplicate_loop_id", lp["id"])
        bucket.append(lp)
        return lp

    def mark_replayed(self, holon_id: str, loop_id: str, at: int,
                      boost: float = 0.25) -> dict:
        for i, lp in enumerate(self._loops.get(holon_id, [])):
            if lp["id"] == loop_id:
                upd = dict(lp)
                upd["last_replayed"] = int(at)
                upd["strength"] = lp["strength"] + boost
                upd = schema.validate_loop(upd)
                self._loops[holon_id][i] = upd
                return upd
        raise LoopError("unknown_loop", loop_id)

    def forget(self, holon_id: str, loop_id: str) -> dict:
        """Remove exactly one loop, explicitly, and hand it back."""
        bucket = self._loops.get(holon_id, [])
        for i, lp in enumerate(bucket):
            if lp["id"] == loop_id:
                return self._loops[holon_id].pop(i)
        raise LoopError("unknown_loop", loop_id)

    # -- read -------------------------------------------------------------

    def loops(self, holon_id: str) -> List[dict]:
        """Deep copy: stored distinction is not mutable through a read."""
        return [copy.deepcopy(lp) for lp in self._loops.get(holon_id, [])]

    def recently_replayed(self, holon_id: str, n: int = 3) -> List[dict]:
        lps = sorted(self.loops(holon_id),
                     key=lambda lp: (-lp["last_replayed"], lp["id"]))
        return lps[:n]

    def residue_histogram(self, holon_id: str) -> dict:
        hist = {}
        for lp in self.loops(holon_id):
            hist[lp["residue"]] = hist.get(lp["residue"], 0) + 1
        return hist

    # -- persistence ------------------------------------------------------

    def save(self, path: str):
        doc = {"version": REGISTER_VERSION,
               "registers": {h: lps for h, lps in sorted(self._loops.items())}}
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=1, sort_keys=True)
        os.replace(tmp, path)

    @classmethod
    def load(cls, path: str) -> "MemoryRegister":
        with open(path, "r", encoding="utf-8") as f:
            doc = json.load(f)
        if doc.get("version") != REGISTER_VERSION:
            raise LoopError("wrong_register_version",
                            str(doc.get("version")))
        reg = cls()
        for holon_id, lps in (doc.get("registers") or {}).items():
            for lp in lps:
                reg.put(holon_id, lp)
        return reg
