"""Crux structural layer — the four perspectives and the route matrix.

Status: source_defined. Every object here is stated directly by
Unified Shell Geometry and Developmental Dynamics v1.1 sections 2-3 and
the Individuation Atlas v1.3 Part 5. Nothing is derived here; derivation
lives in typemap.py.

  Q = {I, IT, WE, ITS}, coded I=00 IT=01 WE=10 ITS=11.
  First bit: individual / collective.  Second bit: interior / exterior.
  disp(o -> d) = o XOR d.
  The sixteen routes form the pair groupoid on Q.
"""

from __future__ import annotations

VERSION = "crux_v1"

PERSPECTIVES = ("I", "IT", "WE", "ITS")

CODE = {"I": 0b00, "IT": 0b01, "WE": 0b10, "ITS": 0b11}
BY_CODE = {v: k for k, v in CODE.items()}

# Displacement classes. 00 is the identity/self-route, 01 the surface flip.
SURFACE_FLIP = 0b01
IDENTITY_DISP = 0b00

ROUTE_NAME = {
    ("I", "I"): "Contemplate",
    ("I", "IT"): "Express",
    ("I", "WE"): "Share",
    ("I", "ITS"): "Theorize",
    ("IT", "I"): "Embody",
    ("IT", "IT"): "Act",
    ("IT", "WE"): "Coordinate",
    ("IT", "ITS"): "Organize",
    ("WE", "I"): "Identify",
    ("WE", "IT"): "Mobilize",
    ("WE", "WE"): "Commune",
    ("WE", "ITS"): "Institutionalize",
    ("ITS", "I"): "Understand",
    ("ITS", "IT"): "Apply",
    ("ITS", "WE"): "Educate",
    ("ITS", "ITS"): "Integrate",
}

# Polarity of a formal movement (source section 2): one further bit.
POLARITIES = ("accumulation", "expenditure")


class CruxError(Exception):
    def __init__(self, reason: str, detail: str = ""):
        self.reason = reason
        self.detail = detail
        super().__init__(reason if not detail else "%s: %s" % (reason, detail))


def _check(p: str) -> str:
    if p not in CODE:
        raise CruxError("invalid_perspective", str(p))
    return p


def code(p: str) -> int:
    return CODE[_check(p)]


def disp(o: str, d: str) -> int:
    return code(o) ^ code(d)


def route_name(o: str, d: str) -> str:
    return ROUTE_NAME[(_check(o), _check(d))]


def is_self_route(o: str, d: str) -> bool:
    return disp(o, d) == IDENTITY_DISP


def is_surface_flip(o: str, d: str) -> bool:
    return disp(o, d) == SURFACE_FLIP


def is_collective(p: str) -> bool:
    """First bit: 1 = collective scale (WE, ITS)."""
    return bool(code(p) & 0b10)


def scale(p: str) -> str:
    return "collective" if is_collective(p) else "individual"


def surface_partner(p: str) -> str:
    """The unique perspective one surface flip away."""
    return BY_CODE[code(p) ^ SURFACE_FLIP]


def routes():
    """All sixteen routes as (origin, destination) pairs, sorted."""
    return tuple(sorted(ROUTE_NAME))


def inverse(o: str, d: str):
    return (_check(d), _check(o))


def composable(r1, r2) -> bool:
    return r1[1] == r2[0]


def compose(r1, r2):
    """Pair-groupoid composition. Note that the composite forgets the
    intermediate perspective -- that loss is exactly what OIG recovers."""
    if not composable(r1, r2):
        raise CruxError("not_composable", "%s then %s" % (r1, r2))
    return (r1[0], r2[1])


# ---------------------------------------------------------------------------
# Formal movement m = (o, d, p): five bits, thirty-two forms (source s.2)
# ---------------------------------------------------------------------------

def movement(origin: str, destination: str, polarity: str) -> dict:
    if polarity not in POLARITIES:
        raise CruxError("invalid_polarity", str(polarity))
    return {"origin": _check(origin), "destination": _check(destination),
            "polarity": polarity}


def movement_bits(m) -> int:
    return (code(m["origin"]) << 3) | (code(m["destination"]) << 1) \
        | POLARITIES.index(m["polarity"])


def all_movements():
    return tuple(movement(o, d, p)
                 for o in PERSPECTIVES for d in PERSPECTIVES
                 for p in POLARITIES)
