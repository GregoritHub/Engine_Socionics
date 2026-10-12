"""le_dynamic mirror — multiscale model state and the UNFITTED dynamic model.

SPEC sections 17, 21, 46-48.  Central boundary (SPEC section 2):
structural topology is specified; numerical dynamics are not.  Until
parameters are estimated from real observations, every numerical query
returns 'unknown' or structural information only — never fake probabilities.
"""

from .core import ELEMENTS, TIMS, routing_neighbors, routing_distance
from .features import extract

SUBTYPES = ["unknown", "dominant", "creative", "normalizing", "harmonizing"]


def new_model_state(tim, subtype="unknown"):
    if tim not in TIMS:
        raise ValueError("not a lawful TIM: %r" % (tim,))
    if subtype not in SUBTYPES:
        raise ValueError("not a lawful subtype value: %r" % (subtype,))
    return {
        "tim": tim,                       # locked experimental assignment
        "subtype": subtype,               # optional in first study
        "profile": "unknown",             # estimated field over 8 IEs
        "current_state": "unknown",       # hard IE, distribution, or unknown
        "reserve": "unknown",             # latent; no physical units
        "model_version": "v2.0",
        "parameter_version": "unfitted",
    }


class UnfittedReserveModel:
    """Default le_reserve_model behaviour: returns unknown (SPEC section 46)."""

    name = "unfitted_reserve"

    def init(self, _model_state):
        return "unknown"

    def predict(self, _model_state, _context, _control):
        return "unknown"

    def update(self, _model_state, _context, _control, _observation):
        return "unknown"


class UnfittedProfileModel:
    """Default le_profile_model behaviour (SPEC section 47)."""

    name = "unfitted_profile"

    def init(self, _model_state):
        return {ie: {"estimate": "unknown",
                     "uncertainty": "unknown",
                     "parameter_version": "unfitted"} for ie in ELEMENTS}


class TransitionModel:
    """P(z' | z, tau, p, r, e, u; theta) — structural_only until theta is
    estimated (SPEC section 21).  Never returns fabricated probabilities."""

    def __init__(self, mode="structural_only", theta=None):
        if mode not in ("structural_only", "fitted"):
            raise ValueError(mode)
        if mode == "fitted" and theta is None:
            raise ValueError("fitted mode requires estimated parameters")
        self.mode = mode
        self.theta = theta

    def permissible_routes(self, tim, z, target):
        return {
            "mode": self.mode,
            "primitive_neighbors": routing_neighbors(tim, z),
            "routing_distance": routing_distance(tim, z, target),
            "hypotheses": [
                "H1 TIM-dependent routing: cost depends on TIM-specific "
                "routing geometry beyond generic IE identity",
                "H2 intermediate-state facilitation: a privileged "
                "intermediate can reduce target-entry cost",
            ],
            "numerical_probabilities": ("unavailable_unfitted"
                                        if self.mode == "structural_only"
                                        else "fitted"),
        }

    def features(self, tim, z, target, intermediates=None, practice=None):
        return extract(tim, z, target, intermediates=intermediates,
                       practice=practice,
                       parameter_version=("unfitted" if self.mode ==
                                          "structural_only" else "fitted"))

    def probability(self, *_args, **_kw):
        if self.mode == "structural_only":
            raise RuntimeError(
                "transition model is structural_only: no numerical kernel "
                "has been estimated from observations (SPEC sections 2, 21)")
        raise NotImplementedError("fitted kernel evaluation is part of the "
                                  "post-calibration phase (Phase 6)")
