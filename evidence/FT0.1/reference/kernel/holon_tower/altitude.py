"""Generated altitude -- the developmental law, replacing the fixed ladder.

Status: source_defined law, derived implementation (source sections 10-14;
Atlas Part 7).

  h(H) = recursive depth of completed coherent closure

Altitude is COUNTED, never assigned. There is no ladder of names to index
into, and this module deliberately exposes no successor function on tiers.
The source is explicit about the failure modes:

    Difficulty alone is not altitude pressure.
    One failed route is not altitude pressure.
    High activity is not altitude.

Altitude increases only when the COMPLETE currently available organization
cannot meet a generated demand without persistent Shell distortion. The
selection rule is a search, not an increment:

    C(H_k, D) != empty  ->  horizontal adaptation
    C(H_k, D) == empty  ->  developmental boundary
    H_(k+1) = min { H' > H_k : C(H', D) != empty }

and the character of the new altitude is read off AFTER the organization is
generated:

    C_new = C(H_(k+1), D) - C(H_k, D)
    chi   = Profile(C_new)

Where several equally minimal solutions exist, development BRANCHES, and
this module returns all of them rather than breaking the tie. Preserving
the branch is a requirement of the source, not an implementation detail.

The predecessor payload `tower_v1` (nine vMemes x four quadrants, advancing
on all-quadrant activity plus bloom) is retained in schema.py for
compatibility only. It contradicts this law on three counts: it advances
with no demand term, it never consults Shell state, and its tiers are
primitive coordinates rather than emergent summaries.
"""

from __future__ import annotations

from typing import Mapping, Optional, Sequence

from crux import perspectives as P
from crux import shell as SH
from crux import typemap as TM
from demand import schema as DS

VERSION = "tower_v2"


class AltitudeError(Exception):
    def __init__(self, reason: str, detail: str = ""):
        self.reason = reason
        self.detail = detail
        super().__init__(reason if not detail else "%s: %s" % (reason, detail))


# ---------------------------------------------------------------------------
# Horizontal adaptation versus developmental boundary (source section 12)
# ---------------------------------------------------------------------------

def classify_demand(org: Mapping, dem: Mapping) -> str:
    """`horizontal_adaptation` or `developmental_boundary`.

    The current holon may change route, polarity, timing or strategy
    without any increase in altitude. That is the common case and it is
    not development.
    """
    return ("developmental_boundary"
            if DS.is_developmental_boundary(org, dem)
            else "horizontal_adaptation")


# ---------------------------------------------------------------------------
# The altitude-selection rule (source section 12)
# ---------------------------------------------------------------------------

def extension_cost(org: Mapping, added: str) -> int:
    """What it costs this TIM to retain `added` as a conductive capacity.

    Read off the dwelling-cost ladder, so it is generated from the stack
    rather than assigned: native 7, Lateral-E 6, Lateral-A 4,
    complementary 3. Higher is cheaper.
    """
    return TM.cost_of_perspective(org["tim"], added)


def candidate_extensions(org: Mapping) -> tuple:
    """Every organization strictly one capacity above this one."""
    out = []
    for p in P.PERSPECTIVES:
        if p in org["retained"]:
            continue
        out.append(DS.organization(org["tim"],
                                   retained=set(org["retained"]) | {p},
                                   dwelling=org["dwelling"],
                                   closures=org["closures"]))
    return tuple(out)


def minimal_extensions(org: Mapping, dem: Mapping) -> tuple:
    """H_(k+1) = min { H' > H_k : C(H', D) != empty }.

    Returns ALL minimal solutions. A tuple of length > 1 is a branch point
    and must be preserved as such; length 0 means no single-capacity
    extension solves the demand.
    """
    if not DS.is_developmental_boundary(org, dem):
        raise AltitudeError("not_a_boundary",
                            "current organization already meets D")
    solving = [h for h in candidate_extensions(org)
               if DS.meets_conductively(h, dem)]
    if not solving:
        return ()
    best = max(extension_cost(org, sorted(h["retained"] - org["retained"])[0])
               for h in solving)
    return tuple(h for h in solving
                 if extension_cost(
                     org, sorted(h["retained"] - org["retained"])[0]) == best)


def branches(org: Mapping, dem: Mapping) -> int:
    return len(minimal_extensions(org, dem))


# ---------------------------------------------------------------------------
# Developmental character (source section 13)
# ---------------------------------------------------------------------------

def new_conductive_movements(org_k: Mapping, org_k1: Mapping,
                             dem: Optional[Mapping] = None) -> tuple:
    """C_new = C(H_(k+1), D) - C(H_k, D)."""
    old = {P.movement_bits(m) for m in DS.conductive_movements(org_k, dem)}
    return tuple(m for m in DS.conductive_movements(org_k1, dem)
                 if P.movement_bits(m) not in old)


def character(org_k: Mapping, org_k1: Mapping,
              dem: Optional[Mapping] = None) -> dict:
    """chi_(k+1) = Profile(C_new).

    Source section 13 names eight measures for this profile: origin,
    destination, displacement, polarity, club, residual family, route
    composition, and recurrence structure. Six are implemented here:

      destination, displacement, polarity   as named
      club                                  as named, from the type map
      route                                 route composition, one hop
      cost_class                            not in the source's list, but
                                            in bijection with club WITHIN a
                                            single TIM (typemap.py) though
                                            not across TIMs: cost class is
                                            TIM-relative, club is absolute.
                                            Both are reported, because a
                                            profile over several TIMs needs
                                            each and neither recovers the
                                            other
      origin                                NOT profiled: every movement in
                                            C_new leaves the same dwelling,
                                            so the distribution is constant
      residual family                       not implemented
      recurrence structure                  not implemented; it is a
                                            trajectory property and C_new
                                            is a set of movements, so it
                                            needs a trajectory argument
                                            this function does not take

    `dominant` is reported only when one structural profile actually
    dominates; otherwise it is None and the caller must not invent one.
    """
    c_new = new_conductive_movements(org_k, org_k1, dem)
    if not c_new:
        return {"c_new": (), "dominant": None, "profile": {}}
    prof = {"destination": {}, "displacement": {}, "polarity": {},
            "route": {}, "club": {}, "cost_class": {}}
    for m in c_new:
        d = m["destination"]
        prof["destination"][d] = prof["destination"].get(d, 0) + 1
        k = format(P.disp(m["origin"], d), "02b")
        prof["displacement"][k] = prof["displacement"].get(k, 0) + 1
        prof["polarity"][m["polarity"]] = \
            prof["polarity"].get(m["polarity"], 0) + 1
        r = P.route_name(m["origin"], d)
        prof["route"][r] = prof["route"].get(r, 0) + 1
        cc = TM.perspective_cost_class(org_k1["tim"], d)
        prof["cost_class"][cc] = prof["cost_class"].get(cc, 0) + 1
        club = TM.club_of(TM.cost_class_pair(org_k1["tim"], cc))
        prof["club"][club] = prof["club"].get(club, 0) + 1
    dests = prof["destination"]
    top = max(dests.values())
    winners = [d for d, n in dests.items() if n == top]
    dominant = winners[0] if len(winners) == 1 else None
    return {"c_new": c_new, "dominant": dominant, "profile": prof}


# ---------------------------------------------------------------------------
# Coherent closure (source sections 9, 18; Atlas Part 5 "Embodiment")
# ---------------------------------------------------------------------------

def return_route(tim: str):
    """The route that carries the crossed capacity home: complementary ->
    native. Generated from the type map, never tabulated.

    Atlas Part 5 states this as a fixed pair per scale -- IT -> I (Embody)
    for individual-scale types, ITS -> WE (Educate) for collective. That
    holds for exactly the eight TIMs whose NATIVE perspective is interior
    (second bit 0: I, WE). The other eight are exterior-native and return
    the other way:

        interior-native   EIE EII IEE IEI   IT  -> I    Embody
                          ESE ESI SEE SEI   ITS -> WE   Educate
        exterior-native   LSE LSI SLE SLI   I   -> IT   Express
                          ILE ILI LIE LII   WE  -> ITS  Institutionalize

    The structural rule (inverse of the first crossing) covers all sixteen;
    the Atlas's named pairs are a restriction of it, not a definition. See
    NOTE_V3.md, "One correction to the Atlas", and the verify_v3 check
    `crux.atlas_return_route_claim_holds_only_for_interior_native`.
    """
    return TM.type_map(tim)["return_route"]


def closure_admissible(org: Mapping, *, crossed: str,
                       walk: Sequence[str],
                       shell_before: Mapping,
                       shell_after: Mapping) -> tuple:
    """Does this trajectory constitute a completed coherent closure?

    Reaching the complementary surface is NOT integration. Three conditions
    must all hold, and each is a separate failure the source names:

      1. the crossed capacity is retained (not merely visited);
      2. the return route was actually traversed -- cross into the
         complement AND return carrying it;
      3. the Shell was CLEARED, not suppressed. Motion across an exotic
         surface is not development.
    """
    reasons = []
    if crossed not in org["retained"]:
        reasons.append("capacity_visited_not_retained")
    src, dst = return_route(org["tim"])
    walk = tuple(walk)
    traversed = any(walk[i] == src and walk[i + 1] == dst
                    for i in range(len(walk) - 1))
    if not traversed:
        reasons.append("return_route_not_traversed")
    if not SH.is_empty(shell_after):
        if SH.cleared(SH.realization({"origin": src, "destination": dst,
                                      "polarity": "accumulation"},
                                     shell_before),
                      SH.realization({"origin": src, "destination": dst,
                                      "polarity": "accumulation"},
                                     shell_after)):
            reasons.append("shell_reduced_but_not_cleared")
        else:
            reasons.append("shell_persists")
    return (not reasons, tuple(reasons))


def close(org: Mapping, *, crossed: str, walk: Sequence[str],
          shell_before: Mapping, shell_after: Mapping) -> dict:
    """Seal one holon and increment altitude. Sealing is one-way: the lower
    holon does not disappear, it becomes a constituent of the higher one."""
    ok, reasons = closure_admissible(org, crossed=crossed, walk=walk,
                                     shell_before=shell_before,
                                     shell_after=shell_after)
    if not ok:
        raise AltitudeError("closure_inadmissible", ",".join(reasons))
    return DS.organization(org["tim"], retained=org["retained"],
                           dwelling=org["dwelling"],
                           closures=org["closures"] + 1)


# ---------------------------------------------------------------------------
# tower_v2 payload -- what rides in the kernel's opaque cape_phase field
# ---------------------------------------------------------------------------

def altitude_phase(org: Mapping, *, history: Sequence = ()) -> dict:
    tm = TM.type_map(org["tim"])
    return {
        "version": VERSION,
        "tim": org["tim"],
        "retained": sorted(org["retained"]),
        "dwelling": org["dwelling"],
        "altitude": org["closures"],
        "native_perspective": tm["native_perspective"],
        "scale": tm["scale"],
        "history": [dict(h) for h in history],
    }
