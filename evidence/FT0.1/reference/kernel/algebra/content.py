"""The single Content value.

A Content is a set of retained aspects plus opaque foreign keys.  Every
other vocabulary is a projection of it:

  domains(c)      = union of line_of(a) for retained aspects a
                    -> the OIG domain key set the kernel reads
  perspectives(c) = the same set, in Crux letters
  kernel_delta(c) = a content delta for pyref.holon.transition

Nothing here is a fourth store; it is the one object the others are
views of.  Facets are not part of Content: they are what a POSITION did
to an aspect on the way in, and belong to the metabolic state.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pyref.core import ELEMENTS
from .perspective import line_of, DOMAIN_KEY


@dataclass(frozen=True)
class Content:
    aspects: frozenset = field(default_factory=frozenset)
    foreign: frozenset = field(default_factory=frozenset)

    def __post_init__(self):
        bad = set(self.aspects) - set(ELEMENTS)
        if bad:
            raise ValueError("not aspects: %s" % sorted(bad))

    def perspectives(self) -> frozenset:
        out = frozenset()
        for a in self.aspects:
            out |= line_of(a)
        return out

    def domains(self) -> frozenset:
        return frozenset(DOMAIN_KEY[P] for P in self.perspectives())

    def kernel_delta(self) -> dict:
        """Domain keys present -> the aspects that put them there."""
        dom = {}
        for a in sorted(self.aspects):
            for P in line_of(a):
                dom.setdefault(DOMAIN_KEY[P], []).append(a)
        return {"replace_domain": {k: ",".join(v) for k, v in dom.items()},
                "replace_foreign": {k: "present" for k in sorted(self.foreign)}}


def project_domains(aspects) -> frozenset:
    return Content(frozenset(aspects)).domains()
