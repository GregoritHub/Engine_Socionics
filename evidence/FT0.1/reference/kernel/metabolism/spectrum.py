"""Emission spectrum and provenance (V5.2, A38).

A packet is (aspect, facets, source, tag, carried, walk).  Its SHAPE is
the tuple (aspect, |facets|, carried, tag); its PROVENANCE is the set of
walks -- sequences of (holon, position, aspect) hops the content passed
through, across holons.  The spectrum of a holon at an altitude is the
distribution of shapes it emits there.  Nothing here is a quantity of
the theory: counts are counts of packets, the joint fraction is an exact
Fraction of them, and the walk is exact within WALK_CAP hops.

  shape(pk)              the morphed primitive, without history
  spectrum(packets)      Counter of shapes
  provenance(packets)    depth, span (holons crossed), joint fraction
  joint(pk)              True iff the walk crosses >= 2 holons: content
                         produced jointly and owned by neither
"""
from __future__ import annotations
import collections
from fractions import Fraction
from .packet import Packet


def shape(pk: Packet) -> tuple:
    return (pk.aspect, len(pk.facets), tuple(sorted(pk.carried)), pk.tag)


def joint(pk: Packet) -> bool:
    return len(pk.spans()) >= 2


def spectrum(packets) -> collections.Counter:
    return collections.Counter(shape(pk) for pk in packets)


def provenance(packets) -> dict:
    ps = list(packets)
    if not ps:
        return {"n": 0, "depth": (0, 0), "span": (0, 0), "joint": Fraction(0)}
    depths = [pk.depth() for pk in ps]
    spans = [len(pk.spans()) for pk in ps]
    return {"n": len(ps), "depth": (min(depths), max(depths)),
            "span": (min(spans), max(spans)),
            "joint": Fraction(sum(joint(pk) for pk in ps), len(ps))}


def by_altitude(records):
    """records: iterable of (altitude, packet).  -> {alt: (spectrum, provenance)}"""
    buckets = collections.defaultdict(list)
    for alt, pk in records:
        buckets[alt].append(pk)
    return {a: (spectrum(v), provenance(v)) for a, v in sorted(buckets.items())}


def relative_shape(pk: Packet, tim: str) -> tuple:
    """Shape in the emitter's own coordinates: positions instead of aspects,
    so spectra of different types are comparable."""
    from pyref.core import position_of
    return (position_of(tim, pk.aspect), len(pk.facets),
            tuple(sorted(position_of(tim, a) for a in pk.carried)), pk.tag)
