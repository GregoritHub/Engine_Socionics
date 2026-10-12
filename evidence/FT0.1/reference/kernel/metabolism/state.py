"""Metabolic state: eight Position records and nothing else that varies.

Every field is an int, str, tuple, or frozenset.  There is one record
type for a position; the state is a tuple of eight of them.  Views such
as retained/residue are computed, not stored twice."""
from __future__ import annotations
from dataclasses import dataclass, replace
from pyref.core import TIMS, ACCESS, element_at
from algebra import Content
from algebra.facets import position_facets


@dataclass(frozen=True)
class Position:
    index: int
    aspect: str
    dim: int
    facets: frozenset                   # what this position can process (derived law)
    valued: bool
    automatic: bool
    accepting: bool
    kept: frozenset = frozenset()       # facets retained (valued) or last processed
    residue: frozenset = frozenset()    # facets dropped by the gate, cumulative
    charge: frozenset = frozenset()     # producing positions only
    carry: frozenset = frozenset()      # aspects the charge carries
    walks: frozenset = frozenset()      # provenance walks of the charge (V5.2)
    processed: int = 0
    unfed: int = 0                      # consecutive ticks without input
    over: int = 0                       # consecutive ticks with overload
    hit: bool = False                   # overloaded this tick

    def fed(self, kept, dropped, retain, pressing=True):
        return replace(self, processed=self.processed + 1, unfed=0,
                       residue=self.residue | dropped,
                       hit=self.hit or (bool(dropped) and pressing),
                       kept=kept if retain else self.kept)


@dataclass(frozen=True)
class State:
    tim: str
    positions: tuple                     # eight Position, index 1..8 at [i-1]
    pending: tuple = ()                  # mental packets awaiting intention
    ticks: int = 0
    log: tuple = ()
    generative: bool = True
    retained: frozenset = frozenset()    # perspectives retained by the tower (H)
    tick_mark: int = 0                   # log index where this tick began
    launched: bool = False               # A6 charge seen last tick -> Ego forced
    seat: int = 1                        # where the estafette relay is (clock.py)
    serpent: int = 0                     # laps remaining of the Serpent's flood (boredom.py)

    def with_organization(self, org) -> "State":
        """Couple to a demand.schema organization: its retained set."""
        return replace(self, retained=frozenset(org["retained"]))

    def at(self, p: int) -> Position:
        return self.positions[p - 1]

    def put(self, pos: Position, entry=None) -> "State":
        ps = list(self.positions)
        ps[pos.index - 1] = pos
        return replace(self, positions=tuple(ps),
                       log=self.log + ((entry,) if entry else ()))

    # ---- views -------------------------------------------------------
    @property
    def kept(self) -> dict:
        return {q.index: q.kept for q in self.positions if q.valued and q.kept}

    @property
    def residue(self) -> dict:
        return {q.index: q.residue for q in self.positions if q.residue}

    @property
    def processed(self) -> dict:
        return {q.index: q.processed for q in self.positions if q.processed}

    @property
    def charge(self) -> dict:
        return {q.index: q.charge for q in self.positions if q.charge}

    def fed_this_tick(self) -> frozenset:
        return frozenset(q.index for q in self.positions if q.unfed == 0 and q.processed)

    def content(self) -> Content:
        """The unified Content: retained aspects.  Facets stay here."""
        return Content(frozenset(q.aspect for q in self.positions
                                 if q.valued and q.kept))


def new_state(tim: str, generative: bool = True) -> State:
    if tim not in TIMS:
        raise ValueError("invalid_tim: %s" % tim)
    ps = tuple(Position(p, element_at(tim, p), ACCESS[p]["dimensionality"],
                        position_facets(p),
                        ACCESS[p]["valued"], ACCESS[p]["frame"] == "vital",
                        ACCESS[p]["mode"] == "accepting")
               for p in range(1, 9))
    from crux.typemap import type_map
    return State(tim=tim, positions=ps, generative=generative,
                 retained=frozenset([type_map(tim)["native_perspective"]]))
