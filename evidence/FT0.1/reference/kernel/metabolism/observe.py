"""Pi_O over the metabolism: one process, two projections.

Shell Geometry section 5: the Crux identifies the transformation, OIG
identifies how it was realized.  The metabolism's per-tick Content
projects to OIG domain keys (algebra.content); a sequence of states is
therefore an OIG content path and pyref.oig computes (V, N, K, R) over
it with nothing added.  The Shell signatures the source states:

    maintenance   K != empty and N = empty     (section 7: A -> B -> A)
    foreclosure   no departure under demand    (section 7: pure A under D)

The per-sign map for the four activation signs is not stated by the
source and is not asserted here (UNRESOLVED 9).
"""
from __future__ import annotations
from pyref import oig


def content_path(states) -> list:
    return [frozenset(s.content().domains()) for s in states]


def projection(states) -> dict:
    sts = list(states)
    s = oig.summarize_trajectory(sts[0].tim, content_path(sts))
    return {"V": s["V"], "N": s["N"], "K": frozenset(s["K"]), "parity": s["parity"],
            "R": s["temporal_profile"], "trace": s["trace"]}


def maintenance(states) -> bool:
    p = projection(states)
    return bool(p["K"]) and p["N"] == ("none", "none")


def foreclosure(states, demand_present: bool) -> bool:
    return demand_present and len(set(content_path(states))) == 1
