"""D_Shell = (D, Pi_C, Pi_O) -- the joint detector.

Status: derived (source 6.1, 19; Atlas Part 8.4).

Demand states what the system was required to do. The Crux states which
movement was selected and whether it was conductive. OIG states what
happened to observable content. No one leg suffices:

  * Pi_O alone cannot recover D (Demand-Blindness), so it cannot separate
    rest from foreclosure.
  * Pi_C alone cannot separate a direct realization from a compensatory
    one, because the pair groupoid forgets the interior of the walk.
  * D alone says nothing about what actually happened.

The classifier returns one of four states. Note that REST is a first-class
outcome, not a default: the source is explicit that the native self-route
is free and non-pathological, and that misclassifying it is the specific
error the demand clause exists to prevent.
"""

from __future__ import annotations

from typing import Mapping, Optional, Sequence

from crux import shell as SH

from .protocol import (baseline_trajectory, crux_projection, demanded_trajectory,
                       departed, oig_projection)
from .schema import DemandError, is_developmental_boundary

VERSION = "demand_v1"

REST = "rest"
CONDUCTIVE = "conductive_realization"
SHELL_MEDIATED = "shell_mediated_realization"
FORECLOSED = "foreclosure"

STATES = (REST, CONDUCTIVE, SHELL_MEDIATED, FORECLOSED)


def maintenance_signature(pi_o: Mapping) -> bool:
    """The A -> B -> A geometry: activity occurred, nothing was retained.

    At the relevant quotient V=1, N=0, K=1 -- cumulative visibility without
    net endpoint difference.
    """
    return bool(pi_o["K"]) and pi_o["N"] == ("none", "none")


def recurrence_returns(pi_o: Mapping) -> int:
    """How many quotients show a moment returning to an earlier class.

    R preserves recurrence that endpoint summaries lose. Recurrence is not
    by itself pathological -- rhythm, practice and rehearsal are recurrent
    -- so this is reported, never decisive on its own.
    """
    n = 0
    for _, partition in pi_o["R"].items():
        if any(len(block) > 1 for block in partition):
            n += 1
    return n


def detect(org: Mapping, *, dem: Optional[Mapping] = None,
           observed_walk: Optional[Sequence[str]] = None,
           observed_shell: Optional[Mapping] = None,
           steps: int = 2) -> dict:
    """Run the joint detector.

    `observed_walk` lets a caller supply what the system actually did; when
    omitted the protocol's own gamma_0 / gamma_D are used, which is the
    pure-perturbation case.
    """
    tim = org["tim"]
    g0 = baseline_trajectory(org, steps)
    gD = tuple(observed_walk) if observed_walk is not None \
        else (demanded_trajectory(org, dem, steps) if dem is not None else g0)

    pi_o_0 = oig_projection(tim, g0)
    pi_o_D = oig_projection(tim, gD)
    sh = observed_shell if observed_shell is not None else SH.coherent_shell()
    pi_c = crux_projection(gD, shell=sh)

    moved = departed(g0, gD)

    if dem is None:
        state = REST
        why = "no relevant demand; native self-route continues"
    elif not moved:
        # Non-initiation under demand. Foreclosure is only declarable when
        # the prevention persists through the conductivity test.
        if len(gD) - 1 >= dem["window"] and is_developmental_boundary(org, dem):
            state = FORECLOSED
            why = ("demand calls for %s; movement did not become active and "
                   "the current organization was preserved"
                   % "|".join(sorted(dem["requires_destination"])))
        else:
            state = REST
            why = "no departure, but prevention has not persisted through the test"
    elif SH.is_empty(sh) and not maintenance_signature(pi_o_D):
        state = CONDUCTIVE
        why = "demand met without persistent distortion"
    else:
        state = SHELL_MEDIATED
        why = "demand met, but distortion or cancellation persists"

    return {
        "version": VERSION,
        "state": state,
        "why": why,
        "demand": dict(dem) if dem is not None else None,
        "pi_C": pi_c,
        "pi_O": {"V": pi_o_D["V"], "N": pi_o_D["N"],
                 "K": sorted(pi_o_D["K"]), "parity": pi_o_D["parity"]},
        "gamma_0": g0,
        "gamma_D": gD,
        "departed": moved,
        "maintenance_signature": maintenance_signature(pi_o_D),
        "recurrence_returns": recurrence_returns(pi_o_D),
        "oig_alone_separates_from_baseline": (
            (pi_o_0["V"], pi_o_0["N"], pi_o_0["K"], pi_o_0["R"])
            != (pi_o_D["V"], pi_o_D["N"], pi_o_D["K"], pi_o_D["R"])),
    }


def integration_improved(before: Mapping, after: Mapping) -> bool:
    """After genuine integration the SAME demand should require less
    trajectory complexity, less persistent cancellation, and retain more.

    Both arguments are detector reports for the same demand.
    """
    if before["demand"] is None or after["demand"] is None:
        raise DemandError("integration_requires_demand")
    if before["demand"]["id"] != after["demand"]["id"]:
        raise DemandError("different_demands")
    shorter = len(after["gamma_D"]) <= len(before["gamma_D"])
    less_k = len(after["pi_O"]["K"]) <= len(before["pi_O"]["K"])
    retained = after["pi_O"]["N"] != ("none", "none")
    return shorter and less_k and retained
