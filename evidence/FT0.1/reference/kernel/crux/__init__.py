"""Crux structural layer — the four perspectives and what each TIM does
with them.

Everything in this package is either stated by the governing source or
generated from the kernel's locked Model A stacks. Nothing is entered per
type, so the sixteen type maps cannot drift from the architecture.

  perspectives.py  Q = {I, IT, WE, ITS} as two bits, the sixteen routes,
                   the pair groupoid, formal movements  (source_defined)
  typemap.py       the per-TIM map: cost classes, clubs, dwelling costs,
                   first crossing, return route          (derived)
  shell.py         x = (m, S, iota) — realizations, the five signs,
                   clearance vs suppression              (source_defined)

Read-only with respect to `pyref`: this package imports the locked tables
and never writes to them.
"""

from .perspectives import (
    CODE, PERSPECTIVES, ROUTE_NAME, CruxError,
    all_movements, code, compose, disp, inverse, is_self_route,
    is_surface_flip, movement, route_name, routes, scale, surface_partner,
)
from .typemap import (
    COST_CLASSES, DERIVATIONS,
    all_type_maps, club_of, cost_of_perspective, counterphase, dwelling_cost,
    element_at, is_valued, perspective_cost_class, perspective_of,
    ring_of, type_map,
)

VERSION = "crux_v1"

__all__ = [
    "VERSION",
    # perspectives
    "PERSPECTIVES", "CODE", "ROUTE_NAME", "CruxError",
    "code", "disp", "route_name", "is_self_route", "is_surface_flip",
    "scale", "surface_partner", "routes", "inverse", "compose",
    "movement", "all_movements",
    # typemap
    "COST_CLASSES", "DERIVATIONS",
    "type_map", "all_type_maps", "element_at", "counterphase",
    "perspective_of", "club_of", "dwelling_cost", "cost_of_perspective",
    "perspective_cost_class", "ring_of", "is_valued",
]
