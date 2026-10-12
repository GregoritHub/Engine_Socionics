"""Demand — the term the projections do not contain.

Status: source_defined shape, derived semantics. Source section 6.1 and
Atlas Part 8: the four self-routes are not pathological, and foreclosure
is only diagnosable relative to a demand that calls for departure. The
demand clause is mandatory, so demand must be an object the engine can
carry, not a description in a comment.

A Demand states what the system was required to do:

  requires_destination   the perspective(s) the demand calls for. A set
                         with more than one member is a demand that several
                         distinct movements could satisfy -- which is how
                         developmental BRANCHING arises.
  requires_polarity      optional constraint on the movement's polarity
  intensity              load, in [0, 1]; the "increased demand" of the
                         conductivity test
  window                 how many steps the prevention must persist before
                         foreclosure may be declared

An Organization is the other half of the pair: the capacities a holon has
actually RETAINED (net, not merely visited). The ground state retains only
its native perspective, which is why there is no gradient out of it.
"""

from __future__ import annotations

from typing import Mapping, Optional

from crux import perspectives as P
from crux import typemap as TM

VERSION = "demand_v1"

# Content keys that OIG reads as domain (pyref.oig.DOMAINS).
PERSPECTIVE_KEY = {"I": "i", "IT": "it", "WE": "we", "ITS": "its"}
KEY_PERSPECTIVE = {v: k for k, v in PERSPECTIVE_KEY.items()}


class DemandError(Exception):
    def __init__(self, reason: str, detail: str = ""):
        self.reason = reason
        self.detail = detail
        super().__init__(reason if not detail else "%s: %s" % (reason, detail))


def demand(demand_id: str, requires_destination, *,
           requires_polarity: Optional[str] = None,
           intensity: float = 1.0, window: int = 2) -> dict:
    if not isinstance(demand_id, str) or not demand_id:
        raise DemandError("invalid_demand_id")
    if isinstance(requires_destination, str):
        dests = frozenset([requires_destination])
    else:
        dests = frozenset(requires_destination)
    if not dests:
        raise DemandError("empty_destination_set")
    bad = dests - set(P.CODE)
    if bad:
        raise DemandError("invalid_destination", ",".join(sorted(bad)))
    if requires_polarity is not None and requires_polarity not in P.POLARITIES:
        raise DemandError("invalid_polarity", str(requires_polarity))
    if isinstance(intensity, bool) or not isinstance(intensity, (int, float)):
        raise DemandError("invalid_intensity", str(intensity))
    if not 0.0 <= float(intensity) <= 1.0:
        raise DemandError("invalid_intensity", str(intensity))
    if not isinstance(window, int) or isinstance(window, bool) or window < 1:
        raise DemandError("invalid_window", str(window))
    return {"version": VERSION, "id": demand_id,
            "requires_destination": dests,
            "requires_polarity": requires_polarity,
            "intensity": float(intensity), "window": window}


def validate_demand(obj) -> dict:
    if not isinstance(obj, Mapping):
        raise DemandError("invalid_demand", "not_a_mapping")
    if obj.get("version") != VERSION:
        raise DemandError("wrong_version", str(obj.get("version")))
    extra = set(obj) - {"version", "id", "requires_destination",
                        "requires_polarity", "intensity", "window"}
    if extra:
        raise DemandError("unknown_field", ",".join(sorted(extra)))
    return demand(obj["id"], obj["requires_destination"],
                  requires_polarity=obj.get("requires_polarity"),
                  intensity=obj.get("intensity", 1.0),
                  window=obj.get("window", 2))


# ---------------------------------------------------------------------------
# Organization: retained capacity, not visited capacity
# ---------------------------------------------------------------------------

def organization(tim: str, *, retained=None, dwelling: Optional[str] = None,
                 closures: int = 0) -> dict:
    """A coherent organization H. `retained` is the set of perspectives the
    system can address conductively; the ground state retains only native."""
    tm = TM.type_map(tim)
    native = tm["native_perspective"]
    ret = frozenset(retained) if retained is not None else frozenset([native])
    if native not in ret:
        raise DemandError("native_not_retained",
                          "%s missing from %s" % (native, sorted(ret)))
    bad = ret - set(P.CODE)
    if bad:
        raise DemandError("invalid_perspective", ",".join(sorted(bad)))
    dw = dwelling if dwelling is not None else native
    if dw not in ret:
        raise DemandError("dwelling_not_retained", str(dw))
    if not isinstance(closures, int) or isinstance(closures, bool) \
            or closures < 0:
        raise DemandError("invalid_closures", str(closures))
    return {"version": VERSION, "tim": tim, "retained": ret, "dwelling": dw,
            "closures": closures}


def ground_state(tim: str) -> dict:
    """The unique trajectory that runs indefinitely at minimum cost."""
    return organization(tim)


def is_ground_state(org: Mapping) -> bool:
    tm = TM.type_map(org["tim"])
    return (org["retained"] == frozenset([tm["native_perspective"]])
            and org["dwelling"] == tm["native_perspective"])


def altitude(org: Mapping) -> int:
    """h(H) = recursive depth of completed coherent closure.

    Counted, never assigned. There is no ladder of names to index into.
    """
    return org["closures"]


def order(a: Mapping, b: Mapping) -> Optional[int]:
    """Partial order on organizations by retained capacity. Returns -1 if
    a < b, 1 if a > b, 0 if equal, None if incomparable."""
    ra, rb = a["retained"], b["retained"]
    if ra == rb:
        return 0
    if ra < rb:
        return -1
    if rb < ra:
        return 1
    return None


# ---------------------------------------------------------------------------
# The conductivity test: C(H, D)
# ---------------------------------------------------------------------------

def conductive_movements(org: Mapping, dem: Optional[Mapping] = None) -> tuple:
    """C(H, D) -- the movements that remain conductive under demand D.

    A movement is conductive for H when its destination is a RETAINED
    capacity. Reaching a perspective the organization has only visited is
    not conductivity; that is what the Shell is for.

    With no demand, C is the movements available from the current dwelling.
    """
    out = []
    for dest in sorted(org["retained"]):
        for pol in P.POLARITIES:
            m = P.movement(org["dwelling"], dest, pol)
            if dem is not None:
                if m["destination"] not in dem["requires_destination"]:
                    continue
                if dem["requires_polarity"] is not None \
                        and m["polarity"] != dem["requires_polarity"]:
                    continue
            out.append(m)
    return tuple(out)


def meets_conductively(org: Mapping, dem: Mapping) -> bool:
    return len(conductive_movements(org, dem)) > 0


def is_developmental_boundary(org: Mapping, dem: Mapping) -> bool:
    """C(H_k, D) = empty. Not "hard", not "failed once" -- unsolvable by
    the complete current organization."""
    return not meets_conductively(org, dem)
