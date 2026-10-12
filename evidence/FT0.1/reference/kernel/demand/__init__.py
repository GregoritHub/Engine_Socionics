"""Demand — the term neither projection contains.

V2 had no word for what a system was *required* to do. Without it, rest
and foreclosure are the same object: both look like a holon sitting on its
native self-route, and no amount of trajectory detail separates them.
Demand is what makes the difference observable.

  schema.py    the Demand object, the Organization (retained capacity),
               and the conductivity test C(H, D)
  protocol.py  the gamma_0 / gamma_D perturbation pair, and the bridge
               that renders a Crux walk as an OIG content path so both
               projections finally describe the same object
  detector.py  the four states — rest, conductive, Shell-mediated,
               foreclosed — read off that perturbation pair
"""

from .detector import (
    CONDUCTIVE, FORECLOSED, REST, SHELL_MEDIATED, STATES,
    detect, integration_improved, maintenance_signature, recurrence_returns,
)
from .protocol import (
    baseline_trajectory, content_path, crux_projection, demand_blind_pair,
    demanded_trajectory, departed, oig_projection,
)
from .schema import (
    PERSPECTIVE_KEY, VERSION, DemandError,
    altitude, conductive_movements, demand, ground_state,
    is_developmental_boundary, is_ground_state, meets_conductively, order,
    organization, validate_demand,
)

__all__ = [
    "VERSION", "DemandError", "PERSPECTIVE_KEY",
    # schema
    "demand", "validate_demand", "organization", "ground_state",
    "is_ground_state", "altitude", "order", "conductive_movements",
    "meets_conductively", "is_developmental_boundary",
    # protocol
    "content_path", "oig_projection", "crux_projection",
    "baseline_trajectory", "demanded_trajectory", "departed",
    "demand_blind_pair",
    # detector
    "REST", "CONDUCTIVE", "SHELL_MEDIATED", "FORECLOSED", "STATES",
    "detect", "maintenance_signature", "recurrence_returns",
    "integration_improved",
]
