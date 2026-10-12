"""The perturbation protocol -- gamma_0 versus gamma_D.

Status: derived (Atlas Part 8.4). Detection proceeds by perturbation:
compare the baseline trajectory with no relevant demand against the
trajectory under a specified demand. The diagnostic information lives in
the triple (D, gamma_0, gamma_D), not in either trajectory alone.

This module is also where the two projections finally meet. A Crux route
walk is rendered as an OIG content path, so pyref.oig can compute (V, N,
K, R) over the very same object the Crux names -- one process, two
resolutions, as the source requires.

  Atlas Part 8.6 table
  ------------------------------------------------------------
  Healthy rest   gamma_0: A -> A      gamma_D: A -> B -> ...
  Foreclosure    gamma_0: A -> A      gamma_D: A -> A, despite D
"""

from __future__ import annotations

from typing import Iterable, Mapping, Optional, Sequence

from pyref import oig

from crux import perspectives as P
from .schema import (KEY_PERSPECTIVE, PERSPECTIVE_KEY, DemandError,
                     conductive_movements, is_developmental_boundary)

VERSION = "demand_v1"


# ---------------------------------------------------------------------------
# Crux walk <-> OIG content path
# ---------------------------------------------------------------------------

def content_path(walk: Sequence[str], foreign: Optional[Iterable] = None):
    """Render a sequence of perspectives as an OIG content path.

    Each step is the opaque key set OIG reads: the dwelt perspective's
    domain key, plus any foreign content carried along.
    """
    extra = frozenset(foreign or ())
    if extra & set(KEY_PERSPECTIVE):
        raise DemandError("foreign_collides_with_domain_key")
    out = []
    for p in walk:
        if p not in PERSPECTIVE_KEY:
            raise DemandError("invalid_perspective", str(p))
        out.append(frozenset([PERSPECTIVE_KEY[p]]) | extra)
    return out


def walk_of(*perspectives) -> tuple:
    return tuple(perspectives)


def oig_projection(tim: str, walk: Sequence[str],
                   foreign: Optional[Iterable] = None) -> dict:
    """Pi_O over a Crux walk: (V, N, K, R) plus the raw trace."""
    path = content_path(walk, foreign)
    s = oig.summarize_trajectory(tim, path)
    return {"V": s["V"], "N": s["N"], "K": frozenset(s["K"]),
            "R": s["temporal_profile"], "parity": s["parity"],
            "trace": s["trace"]}


def crux_projection(walk: Sequence[str], polarity: str = "accumulation",
                    shell=None) -> dict:
    """Pi_C(X_t) = (o, d, p, S). The pair groupoid forgets the interior of
    the walk; that loss is deliberate and is what OIG restores."""
    if len(walk) < 1:
        raise DemandError("empty_walk")
    o, d = walk[0], walk[-1]
    return {"origin": o, "destination": d, "polarity": polarity,
            "route": P.route_name(o, d), "displacement": P.disp(o, d),
            "shell": shell}


# ---------------------------------------------------------------------------
# The two trajectories
# ---------------------------------------------------------------------------

def baseline_trajectory(org: Mapping, steps: int = 2) -> tuple:
    """gamma_0 -- no relevant demand. The system runs its native self-route.

    Free, indefinite, and not pathological.
    """
    if steps < 1:
        raise DemandError("invalid_steps", str(steps))
    return tuple([org["dwelling"]] * (steps + 1))


def demanded_trajectory(org: Mapping, dem: Mapping, steps: int = 2) -> tuple:
    """gamma_D -- the trajectory the organization actually produces under D.

    If the demand is met conductively the system departs. If the demand
    lands on a developmental boundary the organization is preserved
    instead, and gamma_D is indistinguishable from gamma_0.
    """
    cands = conductive_movements(org, dem)
    if not cands:
        return baseline_trajectory(org, steps)
    dest = cands[0]["destination"]
    walk = [org["dwelling"], dest]
    while len(walk) < steps + 1:
        walk.append(dest)
    return tuple(walk)


def departed(gamma_0: Sequence[str], gamma_D: Sequence[str]) -> bool:
    return tuple(gamma_0) != tuple(gamma_D)


# ---------------------------------------------------------------------------
# Demand-Blindness (Atlas Part 8.3)
# ---------------------------------------------------------------------------

def demand_blind_pair(org: Mapping, dem: Mapping, steps: int = 2) -> dict:
    """Construct the witness: rest and foreclosure under identical Pi_O.

    Returns both projections plus whether OIG can separate them. When the
    demand is a boundary the answer must be False -- that is the
    proposition, and no additional OIG coordinate repairs it, because the
    missing information is not in the trajectory at all.
    """
    g0 = baseline_trajectory(org, steps)
    gD = demanded_trajectory(org, dem, steps)
    p0 = oig_projection(org["tim"], g0)
    pD = oig_projection(org["tim"], gD)
    separable = (p0["V"], p0["N"], p0["K"], p0["R"]) != \
                (pD["V"], pD["N"], pD["K"], pD["R"])
    return {"gamma_0": g0, "gamma_D": gD,
            "pi_O_baseline": p0, "pi_O_demanded": pD,
            "boundary": is_developmental_boundary(org, dem),
            "oig_can_separate": separable}
