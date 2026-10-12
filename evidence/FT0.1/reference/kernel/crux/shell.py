"""The Shell as a structured object.

Status: source_defined (section 6, 8; Atlas Part 4).

A Shell is a self-maintaining distortion of an otherwise coherent
movement. Its defining property is NOT failure: a Shell can reach the
correct destination and preserve acceptable external form. The distortion
is in the internal path required to maintain the result.

  x = (m, S, iota)          a realization
  (m, empty, 0)             the coherent realization
  (m, S, iota), S != empty  an exotic realization
  pi(m, S, iota) = m        both project to the same formal movement

The Shell does not create a new route; it changes the realized form of an
existing one. Residual intensity iota varies continuously WITHOUT changing
the discrete Shell identity, which is why iota is carried separately from
the sign set rather than folded into it.

The ontology is prior to the list. The five signs are an enumeration that
may be extended, not a definition by cases.
"""

from __future__ import annotations

from typing import Mapping, Optional

from .perspectives import route_name

VERSION = "shell_v1"

# The five diagnostic signs (source 6.1). Signs 1-4 presuppose that the
# movement became active; sign 5 is the case where none did.
PREMATURE_TRANSLATION = "premature_translation"
FORCED_PLACEMENT = "forced_placement"
NEW_DEFENSIVE_STRUCTURE = "new_defensive_structure"
RESIDUAL_FRAGMENTATION = "residual_fragmentation"
FORECLOSURE = "foreclosure"

ACTIVATION_SIGNS = (PREMATURE_TRANSLATION, FORCED_PLACEMENT,
                    NEW_DEFENSIVE_STRUCTURE, RESIDUAL_FRAGMENTATION)
SIGNS = ACTIVATION_SIGNS + (FORECLOSURE,)

# Carrier hypotheses for foreclosure (Atlas 8.5) -- deliberately open.
CARRIERS = ("H_R", "H_I", "H_RI", "open")


class ShellError(Exception):
    def __init__(self, reason: str, detail: str = ""):
        self.reason = reason
        self.detail = detail
        super().__init__(reason if not detail else "%s: %s" % (reason, detail))


def shell(signs=(), *, iota: float = 0.0, carrier: str = "open",
          notes: Optional[Mapping] = None) -> dict:
    """Construct a Shell S. The empty Shell with iota 0 is coherence."""
    sset = frozenset(signs)
    bad = sset - set(SIGNS)
    if bad:
        raise ShellError("unknown_sign", ",".join(sorted(bad)))
    if isinstance(iota, bool) or not isinstance(iota, (int, float)):
        raise ShellError("invalid_iota", str(iota))
    if not 0.0 <= float(iota) <= 1.0:
        raise ShellError("invalid_iota", str(iota))
    if sset and float(iota) == 0.0:
        raise ShellError("shell_requires_intensity",
                         "signs present with iota 0")
    if not sset and float(iota) != 0.0:
        raise ShellError("intensity_without_shell", str(iota))
    # Signs 1-4 presuppose activation; sign 5 is non-activation. A single
    # realization cannot be both.
    if FORECLOSURE in sset and (sset & set(ACTIVATION_SIGNS)):
        raise ShellError("foreclosure_excludes_activation_signs",
                         ",".join(sorted(sset & set(ACTIVATION_SIGNS))))
    if carrier not in CARRIERS:
        raise ShellError("invalid_carrier", str(carrier))
    if carrier != "open" and FORECLOSURE not in sset:
        raise ShellError("carrier_only_for_foreclosure", carrier)
    return {"version": VERSION, "signs": sset, "iota": float(iota),
            "carrier": carrier, "notes": dict(notes or {})}


def coherent_shell() -> dict:
    return shell()


def is_empty(s: Mapping) -> bool:
    return not s["signs"]


def is_foreclosure(s: Mapping) -> bool:
    return FORECLOSURE in s["signs"]


def presupposes_activation(s: Mapping) -> bool:
    return bool(s["signs"] & set(ACTIVATION_SIGNS))


# ---------------------------------------------------------------------------
# Realizations
# ---------------------------------------------------------------------------

def realization(movement: Mapping, s: Optional[Mapping] = None) -> dict:
    """x = (m, S, iota)."""
    s = s if s is not None else coherent_shell()
    if s.get("version") != VERSION:
        raise ShellError("wrong_shell_version", str(s.get("version")))
    return {"version": VERSION, "movement": dict(movement), "shell": s,
            "iota": s["iota"]}


def coherent(movement: Mapping) -> dict:
    return realization(movement, coherent_shell())


def is_coherent(x: Mapping) -> bool:
    return is_empty(x["shell"]) and x["iota"] == 0.0


def is_exotic(x: Mapping) -> bool:
    return not is_coherent(x)


def project(x: Mapping) -> dict:
    """pi(m, S, iota) = m. Coherent and exotic realizations of the same
    movement are indistinguishable after this map -- which is precisely why
    the formal movement is not a sufficient developmental observable."""
    return dict(x["movement"])


def same_formal_movement(x: Mapping, y: Mapping) -> bool:
    return project(x) == project(y)


def describe(x: Mapping) -> str:
    m = x["movement"]
    r = route_name(m["origin"], m["destination"])
    if is_coherent(x):
        return "%s (coherent)" % r
    return "%s (exotic: %s, iota=%.2f)" % (
        r, "+".join(sorted(x["shell"]["signs"])), x["iota"])


# ---------------------------------------------------------------------------
# Developmental direction (source section 8)
# ---------------------------------------------------------------------------

def cleared(x: Mapping, y: Mapping) -> bool:
    """Is y a Shell CLEARANCE relative to x, rather than mere suppression?

    Clearance means the same formal movement realized with a strictly
    smaller sign set and no greater intensity. Dropping intensity while
    keeping every sign is suppression, not clearance.
    """
    if not same_formal_movement(x, y):
        raise ShellError("different_movements")
    sx, sy = x["shell"]["signs"], y["shell"]["signs"]
    return sy < sx and y["iota"] <= x["iota"]


def suppressed(x: Mapping, y: Mapping) -> bool:
    if not same_formal_movement(x, y):
        raise ShellError("different_movements")
    return (y["shell"]["signs"] == x["shell"]["signs"]
            and y["iota"] < x["iota"])


# ---------------------------------------------------------------------------
# S_C: diagnostic appearance (V5).  Source: Archetypal Shadow Complex.
# Shell Geometry 6.2 names three projections of the Shell object --
# S_C (functional/diagnostic), (K,R) (trajectory), iota.  V3 carried the
# five signs as S_C's *form*; this gives its *content* per position.
# ---------------------------------------------------------------------------

def diagnostic_appearance(tim: str, position: int) -> dict:
    """What a Shell attached at `position` of `tim` looks like, and where it
    projects.  See algebra.archetype for the derivation."""
    from algebra.archetype import diagnostic_appearance as _da
    return _da(tim, position)


def realization_at(movement: Mapping, tim: str, position: int,
                   signs=(), *, iota: float = 0.0) -> dict:
    """An exotic realization whose Shell is located at a position; the
    sign set is the movement-side form, S_C the position-side content."""
    x = realization(movement, shell(signs, iota=iota))
    x["S_C"] = diagnostic_appearance(tim, position)
    return x
