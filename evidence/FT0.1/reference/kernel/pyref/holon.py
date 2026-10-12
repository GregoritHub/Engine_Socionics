"""Holonic Living Engine V1 — Holon wrap around the verified v2 kernel.

This module does not re-derive cubes, frames, or OIG. It wraps them.
16 TIMs are verified special cases of Gamma; they are not required for
every Holon. Structural and untyped Holons use the same 4x3 product
lattice and an empty-but-legal observational envelope.

CAPE phase and shells, if present, are stored as opaque optional fields.
This wrap does not implement a CAPE protocol and does not import surface,
Atlas, expression, libido, or romance modules.

Conditional: a kernel wrap, not a finding about minds.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, replace
from typing import Any, Mapping, Optional, Tuple

from . import core, oig


# Forbidden as pure-state fields or identity keys. Surface lives outside.
SURFACE_KEYS = frozenset({
    "name", "dialogue", "appearance", "audio", "map_xy",
    "player", "romance", "libido",
})

GAMMA_KINDS = frozenset({"tim", "structural", "untyped"})
EMPTY_DEPTH = ("none", "none")
Result = Tuple[bool, Any]


def _copy_map(m: Optional[Mapping]) -> dict:
    if m is None:
        return {}
    if not isinstance(m, Mapping):
        raise HolonError("invalid_map")
    return {str(k): v for k, v in m.items()}


def _scan_surface(keys) -> Optional[str]:
    for k in keys:
        if str(k) in SURFACE_KEYS:
            return str(k)
    return None


class HolonError(Exception):
    """Explicit error atom from a total-or-error operation."""

    def __init__(self, reason: str, detail: str = ""):
        self.reason = reason
        self.detail = detail
        super().__init__(reason if not detail else "%s: %s" % (reason, detail))


def parse_gamma(gamma: str):
    """Return (normalized_gamma, kind, tim_or_name).

    Accepted forms: 'untyped', 'structural:<name>', 'TIM:<one of core.TIMS>'.
    """
    if not isinstance(gamma, str) or not gamma:
        raise HolonError("invalid_gamma", "empty")
    if gamma == "untyped":
        return "untyped", "untyped", None
    if gamma.startswith("structural:"):
        name = gamma.split(":", 1)[1]
        if not name or not all(c.isalnum() or c == "_" for c in name):
            raise HolonError("invalid_gamma", gamma)
        return gamma, "structural", name
    if gamma.startswith("TIM:") or gamma.startswith("tim:"):
        tim = gamma.split(":", 1)[1].lower()
        if tim not in core.TIMS:
            raise HolonError("invalid_gamma", gamma)
        return "TIM:%s" % tim, "tim", tim
    raise HolonError("invalid_gamma", gamma)


def content_keys(content) -> frozenset:
    """OIG carrier keys: present domain labels plus present foreign keys.

    oig.split then partitions those keys into D (its/i/we/it) and F.
    """
    domain, foreign = _content_parts(content)
    keys = set()
    for k, v in domain.items():
        if v is None or v is False or v == "":
            continue
        keys.add(k)
    for k, v in foreign.items():
        if v is None or v is False or v == "":
            continue
        keys.add(k)
    return frozenset(keys)


def _content_parts(content):
    if isinstance(content, Content):
        return content.domain, content.foreign
    if content is None:
        return {}, {}
    if not isinstance(content, Mapping):
        raise HolonError("invalid_content")
    return _copy_map(content.get("domain")), _copy_map(content.get("foreign"))


def freeze_content(content) -> "Content":
    domain, foreign = _content_parts(content)
    hit = _scan_surface(list(domain) + list(foreign))
    if hit:
        raise HolonError("surface_key", hit)
    return Content(domain=domain, foreign=foreign)


@dataclass(frozen=True)
class Content:
    """OIG carrier: independently replaceable domain (D) and foreign (F)."""

    domain: dict = field(default_factory=dict)
    foreign: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {"domain": dict(self.domain), "foreign": dict(self.foreign)}


@dataclass(frozen=True)
class PureState:
    """Local identity only. Never stored on a parent as load-bearing data."""

    gamma_kind: str
    tim: Optional[str] = None
    seat: Optional[int] = None
    cape_phase: Any = None
    shells: Any = None
    domain_content: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.gamma_kind not in GAMMA_KINDS:
            raise HolonError("invalid_gamma_kind", str(self.gamma_kind))
        if self.gamma_kind == "tim":
            if self.tim is None or self.tim not in core.TIMS:
                raise HolonError("invalid_tim", str(self.tim))
        else:
            if self.tim is not None:
                raise HolonError("tim_requires_tim_gamma")
        if self.seat is not None and self.seat not in range(1, 9):
            raise HolonError("invalid_seat", str(self.seat))
        hit = _scan_surface(self.domain_content.keys())
        if hit:
            raise HolonError("surface_key", hit)


@dataclass(frozen=True)
class ObsEnvelope:
    """Summary on the single 4x3 product lattice. Never private state.

    v and n are OIG depth pairs (domain_depth, foreign_depth). Each pair
    generates the 12-bit support S(d,f) via oig.support_of_depths.
    k is the cancelled quotient set V \\ N.
    r is optional/lazy (None until requested for a TIM trajectory).
    """

    v: tuple = EMPTY_DEPTH
    n: tuple = EMPTY_DEPTH
    k: frozenset = field(default_factory=frozenset)
    p: int = 0
    r: Any = None
    depth: tuple = EMPTY_DEPTH

    def v_support(self) -> dict:
        return oig.support_of_depths(*self.v)

    def n_support(self) -> dict:
        return oig.support_of_depths(*self.n)


def empty_envelope() -> ObsEnvelope:
    """Legal empty envelope: empty supports, p=0, r=None.

    Used when Gamma is structural or untyped (no TIM fingerprint).
    Does not invent a second lattice or fake a fingerprint.
    """
    return ObsEnvelope(
        v=EMPTY_DEPTH,
        n=EMPTY_DEPTH,
        k=frozenset(),
        p=0,
        r=None,
        depth=EMPTY_DEPTH,
    )


@dataclass(frozen=True)
class ChildRef:
    """Parent-side handle. Summary is an ObsEnvelope only."""

    id: str
    summary: ObsEnvelope
    last_seen: int


@dataclass(frozen=True)
class Holon:
    """The only pure object. World and characters are Holons at different scales."""

    id: str
    gamma: str
    content: Content
    pure_state: PureState
    trajectory: tuple
    obs: ObsEnvelope
    children: dict
    parent: Optional[str]
    version: int
    archetype: Optional[str] = None


def new_id() -> str:
    return uuid.uuid4().hex


def _refresh_obs(gamma_kind: str, tim: Optional[str], trajectory: tuple,
                 fill_r: bool = False) -> ObsEnvelope:
    if gamma_kind != "tim" or not tim:
        return empty_envelope()
    path = list(trajectory) if trajectory else [frozenset()]
    if len(path) == 1:
        # Single snapshot: V=N=empty, K empty, p=0. Still legal.
        # summarize_trajectory needs at least the endpoints; one point is fine.
        summary = oig.summarize_trajectory(tim, path)
    else:
        summary = oig.summarize_trajectory(tim, path)
    r = summary["temporal_profile"] if fill_r else None
    return ObsEnvelope(
        v=tuple(summary["V"]),
        n=tuple(summary["N"]),
        k=frozenset(summary["K"]),
        p=int(summary["parity"]),
        r=r,
        depth=tuple(summary["V"]),
    )


def create(gamma, init_content, *, seat=None, cape_phase=None, shells=None,
           parent=None, holon_id=None, archetype=None, version=0) -> Holon:
    """create(Gamma, InitContent) -> Holon."""
    norm, kind, rest = parse_gamma(gamma)
    content = freeze_content(init_content)
    tim = rest if kind == "tim" else None
    if seat is not None and seat not in range(1, 9):
        raise HolonError("invalid_seat", str(seat))
    state = PureState(
        gamma_kind=kind,
        tim=tim,
        seat=seat,
        cape_phase=cape_phase,
        shells=shells,
        domain_content=dict(content.domain),
    )
    keys = content_keys(content)
    trajectory = (keys,)
    obs = _refresh_obs(kind, tim, trajectory)
    return Holon(
        id=holon_id or new_id(),
        gamma=norm,
        content=content,
        pure_state=state,
        trajectory=trajectory,
        obs=obs,
        children={},
        parent=parent,
        version=int(version),
        archetype=archetype,
    )


def replace_domain(H: Holon, domain) -> Holon:
    """Total replacement of D. F is unchanged."""
    content = Content(domain=_copy_map(domain), foreign=dict(H.content.foreign))
    hit = _scan_surface(content.domain)
    if hit:
        raise HolonError("surface_key", hit)
    return _commit_content(H, content)


def replace_foreign(H: Holon, foreign) -> Holon:
    """Total replacement of F. D is unchanged."""
    content = Content(domain=dict(H.content.domain), foreign=_copy_map(foreign))
    hit = _scan_surface(content.foreign)
    if hit:
        raise HolonError("surface_key", hit)
    return _commit_content(H, content)


def _commit_content(H: Holon, content: Content, state: Optional[PureState] = None) -> Holon:
    if state is None:
        state = replace(H.pure_state, domain_content=dict(content.domain))
    else:
        state = replace(state, domain_content=dict(content.domain))
    traj = tuple(H.trajectory) + (content_keys(content),)
    obs = _refresh_obs(state.gamma_kind, state.tim, traj)
    return replace(H, content=content, pure_state=state, trajectory=traj,
                   obs=obs, version=H.version + 1)


def _apply_content_delta(content: Content, delta: Optional[Mapping]) -> Content:
    if not delta:
        return content
    domain = dict(content.domain)
    foreign = dict(content.foreign)
    if "replace_domain" in delta:
        domain = _copy_map(delta["replace_domain"])
    if "replace_foreign" in delta:
        foreign = _copy_map(delta["replace_foreign"])
    if "set_domain" in delta:
        domain.update(_copy_map(delta["set_domain"]))
    if "set_foreign" in delta:
        foreign.update(_copy_map(delta["set_foreign"]))
    # Also accept the short forms used in some tables.
    if "domain" in delta and "replace_domain" not in delta and "set_domain" not in delta:
        domain.update(_copy_map(delta["domain"]))
    if "foreign" in delta and "replace_foreign" not in delta and "set_foreign" not in delta:
        foreign.update(_copy_map(delta["foreign"]))
    hit = _scan_surface(list(domain) + list(foreign))
    if hit:
        raise HolonError("surface_key", hit)
    return Content(domain=domain, foreign=foreign)


def _apply_state_delta(state: PureState, delta: Optional[Mapping]) -> PureState:
    if not delta:
        return state
    if "gamma" in delta or "gamma_kind" in delta or "tim" in delta:
        raise HolonError("gamma_immutable")
    kw = {}
    if "seat" in delta:
        seat = delta["seat"]
        if seat is not None and seat not in range(1, 9):
            raise HolonError("invalid_seat", str(seat))
        kw["seat"] = seat
    if "cape_phase" in delta:
        kw["cape_phase"] = delta["cape_phase"]
    if "shells" in delta:
        kw["shells"] = delta["shells"]
    if "domain_content" in delta:
        dc = _copy_map(delta["domain_content"])
        hit = _scan_surface(dc)
        if hit:
            raise HolonError("surface_key", hit)
        kw["domain_content"] = dc
    return replace(state, **kw)


def _lookup_rule(rules, archetype, intention, event):
    if rules is None:
        return None
    table = rules
    if hasattr(rules, "rules"):
        table = rules.rules
    if isinstance(table, Mapping) and "rules" in table:
        table = table["rules"]
    for rule in table:
        if (rule.get("archetype") == archetype
                and rule.get("intention") == intention
                and rule.get("event") == event):
            return rule
    return None


def transition(H: Holon, intention, event, rules=None, archetype=None) -> Result:
    """transition(H, Intention, Event) -> (ok, H') or (False, reason).

    Applies a config rule (Archetype, Intention, Event) -> ContentDelta | StateDelta.
    No hidden globals: the rule table is an argument. Refreshes obs.
    """
    try:
        arch = archetype if archetype is not None else H.archetype
        rule = _lookup_rule(rules, arch, intention, event)
        if rule is None:
            return False, "no_rule"
        content = _apply_content_delta(H.content, rule.get("content_delta"))
        state = _apply_state_delta(H.pure_state, rule.get("state_delta"))
        H2 = _commit_content(H, content, state)
        return True, H2
    except HolonError as e:
        return False, e.reason


def observe(H: Holon, quotient_spec=None) -> ObsEnvelope:
    """observe(H, QuotientSpec) -> summary envelope on the 4x3 lattice.

    For TIM Gamma, V/N/K/parity/R come from pyref.oig. For structural or
    untyped Gamma, the empty-but-legal envelope is returned. quotient_spec
    does not invent a second lattice; requesting R fills the lazy field.
    """
    if H.pure_state.gamma_kind != "tim" or not H.pure_state.tim:
        return H.obs if H.obs is not None else empty_envelope()
    want_r = quotient_spec in ("r", "R", "temporal", "temporal_profile")
    if want_r and H.obs.r is None:
        return _refresh_obs(H.pure_state.gamma_kind, H.pure_state.tim,
                            H.trajectory, fill_r=True)
    return H.obs


def embed_child(parent: Holon, child: Holon, summary) -> Holon:
    """Adds a ChildRef. Never stores the child's private pure_state or raw content."""
    if not isinstance(summary, ObsEnvelope):
        raise HolonError("summary_must_be_envelope")
    ref = ChildRef(id=child.id, summary=summary, last_seen=child.version)
    children = dict(parent.children)
    children[child.id] = ref
    return replace(parent, children=children, version=parent.version + 1)


def detach_child(parent: Holon, child_id: str) -> Holon:
    if child_id not in parent.children:
        raise HolonError("unknown_child", child_id)
    children = dict(parent.children)
    del children[child_id]
    return replace(parent, children=children, version=parent.version + 1)


def emit(H: Holon, intentional_event) -> Result:
    """emit(H, IntentionalEvent) -> (ok, event) a parent or peer may receive."""
    if intentional_event is None:
        return False, "empty_event"
    return True, {"from": H.id, "event": intentional_event}


def pure_projection(H: Holon) -> dict:
    """Local identity only: a function of H.pure_state and H.content.

    Never children, parent private data, sibling state, names, dialogue,
    or map coordinates used as identity.
    """
    ps = H.pure_state
    return {
        "pure_state": {
            "gamma_kind": ps.gamma_kind,
            "tim": ps.tim,
            "seat": ps.seat,
            "cape_phase": ps.cape_phase,
            "shells": ps.shells,
            "domain_content": dict(ps.domain_content),
        },
        "content": H.content.as_dict(),
    }


def set_parent(H: Holon, parent_id) -> Holon:
    """Structural link only."""
    return replace(H, parent=parent_id, version=H.version + 1)


def projection_depends_only_on_local(H: Holon) -> bool:
    """Invariant helper: projection ignores children/parent/obs/id/version."""
    ghost = replace(H, children={}, parent=None, obs=empty_envelope(),
                    version=0, id="ghost")
    return pure_projection(H) == pure_projection(ghost)
