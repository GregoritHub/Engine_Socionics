"""IE-typed packets.  The facet set is algebra.facets -- derived from the
kernel's strong/bold position characters, not a typed ladder.
Facets are a set.  Nothing continuous is stored."""
from __future__ import annotations
from dataclasses import dataclass
from pyref.core import ELEMENTS
from algebra.facets import FACETS, level

FACET_LEVEL = {f: level(f) for f in FACETS}
ALL = frozenset(FACETS)


@dataclass(frozen=True)
class Packet:
    aspect: str
    facets: frozenset = ALL
    source: str = "world"
    tag: str = ""
    carried: frozenset = frozenset()   # aspects whose content this output carries
    walk: frozenset = frozenset()      # provenance: set of walks, each a tuple of
                                       # hops (holon, position, aspect) the content
                                       # passed through, across holons (V5.2, A38)

    def carries(self) -> frozenset:
        return self.carried | {self.aspect}

    def spans(self) -> frozenset:
        """Holons whose positions appear in any provenance walk."""
        return frozenset(h for w in self.walk for (h, _, _) in w if h != "world")

    def depth(self) -> int:
        return max((len(w) for w in self.walk), default=0)

    def __post_init__(self):
        if self.aspect not in ELEMENTS:
            raise ValueError("invalid_aspect: %s" % self.aspect)
        if not self.facets or not self.facets <= ALL:
            raise ValueError("invalid_facets: %s" % sorted(self.facets))


WALK_CAP = 16          # hops kept per walk (instrument integer; order is exact within it)
WALKS_CAP = 64         # distinct walks kept per charge/packet (instrument integer)


def extend(walks, hop) -> frozenset:
    """Append one hop to every walk; an empty provenance starts a walk."""
    ws = walks or frozenset({()})
    out = frozenset((w + (hop,))[-WALK_CAP:] for w in ws)
    if len(out) > WALKS_CAP:
        out = frozenset(sorted(out, key=lambda w: (-len(w), w))[:WALKS_CAP])
    return out


def packet(aspect, facets=None, source="world", tag="") -> Packet:
    return Packet(aspect, ALL if facets is None else frozenset(facets), source, tag,
                  walk=frozenset({((source, 0, aspect),)}))
