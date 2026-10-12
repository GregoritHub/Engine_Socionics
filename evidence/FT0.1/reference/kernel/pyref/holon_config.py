"""Loader/validator for Holonic Living Engine V1 configuration.

Three JSON documents in one directory:
  archetypes.json   — archetype catalogue
  world.json        — world schema
  rules.json        — (Archetype, Intention, Event) -> delta

Invalid configurations are rejected before any Holon is created.
This module does not hard-code a game. It only checks form and the
locked Gamma / seat / surface-key rules.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Mapping

from .holon import (
    SURFACE_KEYS, Holon, HolonError, create, parse_gamma,
)


REQUIRED_FILES = ("archetypes.json", "world.json", "rules.json")


class ConfigError(HolonError):
    def __init__(self, reason: str, detail: str = ""):
        super().__init__(reason, detail)


def _read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _walk_keys(obj, acc=None):
    if acc is None:
        acc = []
    if isinstance(obj, Mapping):
        for k, v in obj.items():
            acc.append(str(k))
            _walk_keys(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            _walk_keys(v, acc)
    return acc


def _reject_surface(obj, where: str):
    for k in _walk_keys(obj):
        if k in SURFACE_KEYS:
            raise ConfigError("surface_key", "%s:%s" % (where, k))


def _validate_gamma(gamma: str, where: str) -> str:
    try:
        norm, kind, rest = parse_gamma(gamma)
    except HolonError as e:
        raise ConfigError("invalid_gamma", "%s:%s" % (where, gamma)) from e
    return norm


def _validate_seat(seat, where: str):
    if seat is None:
        return
    if not isinstance(seat, int) or seat not in range(1, 9):
        raise ConfigError("invalid_seat", "%s:%s" % (where, seat))


@dataclass(frozen=True)
class HolonConfig:
    archetypes: dict
    world: dict
    rules: list
    source_dir: str

    def allowed_events_for(self, archetype: str) -> set:
        vocab = set(self.world.get("global_event_vocabulary") or [])
        if archetype == "world":
            return vocab
        arch = self.archetypes.get(archetype) or {}
        return vocab | set(arch.get("allowed_events") or [])

    def create_world(self, init_content=None) -> Holon:
        content = init_content if init_content is not None else {
            "domain": {},
            "foreign": dict((self.world.get("initial_foreign") or {})),
        }
        return create(
            self.world["world_gamma"],
            content,
            seat=self.world.get("initial_seat"),
            archetype="world",
        )

    def create_character(self, archetype: str, init_content=None) -> Holon:
        if archetype not in self.archetypes:
            raise ConfigError("unknown_archetype", archetype)
        if archetype not in (self.world.get("allowed_child_archetypes") or []):
            raise ConfigError("archetype_not_allowed", archetype)
        spec = self.archetypes[archetype]
        schema = spec.get("initial_content_schema") or {}
        if init_content is None:
            content = {
                "domain": dict(schema.get("domain") or {}),
                "foreign": dict(schema.get("foreign") or {}),
            }
        else:
            content = init_content
        return create(
            spec["gamma"],
            content,
            seat=spec.get("initial_seat"),
            cape_phase=spec.get("cape_phase"),
            shells=spec.get("shells"),
            archetype=archetype,
        )


def validate_documents(archetypes_doc, world_doc, rules_doc) -> HolonConfig:
    if not isinstance(archetypes_doc, Mapping):
        raise ConfigError("invalid_archetypes")
    arches = archetypes_doc.get("archetypes")
    if not isinstance(arches, Mapping) or not arches:
        raise ConfigError("invalid_archetypes", "missing catalogue")
    _reject_surface(arches, "archetypes")

    for name, spec in arches.items():
        if not isinstance(spec, Mapping):
            raise ConfigError("invalid_archetype", name)
        if "gamma" not in spec:
            raise ConfigError("missing_gamma", name)
        spec["gamma"] = _validate_gamma(spec["gamma"], name)
        _validate_seat(spec.get("initial_seat"), name)
        if spec.get("allowed_events") is not None:
            if not isinstance(spec["allowed_events"], list):
                raise ConfigError("invalid_allowed_events", name)
        schema = spec.get("initial_content_schema") or {}
        _reject_surface(schema, "archetypes.%s.initial_content_schema" % name)

    if not isinstance(world_doc, Mapping):
        raise ConfigError("invalid_world")
    _reject_surface(world_doc, "world")
    if "world_gamma" not in world_doc:
        raise ConfigError("missing_world_gamma")
    world_doc = dict(world_doc)
    world_doc["world_gamma"] = _validate_gamma(world_doc["world_gamma"], "world")
    _validate_seat(world_doc.get("initial_seat"), "world")
    children = world_doc.get("allowed_child_archetypes") or []
    if not isinstance(children, list):
        raise ConfigError("invalid_allowed_child_archetypes")
    for child in children:
        if child not in arches:
            raise ConfigError("unknown_child_archetype", child)
    vocab = world_doc.get("global_event_vocabulary") or []
    if not isinstance(vocab, list):
        raise ConfigError("invalid_event_vocabulary")

    if isinstance(rules_doc, Mapping):
        rules = rules_doc.get("rules")
    else:
        rules = rules_doc
    if not isinstance(rules, list):
        raise ConfigError("invalid_rules")
    _reject_surface(rules, "rules")

    vocab_set = set(vocab)
    for i, rule in enumerate(rules):
        if not isinstance(rule, Mapping):
            raise ConfigError("invalid_rule", str(i))
        arch = rule.get("archetype")
        event = rule.get("event")
        if arch is None or event is None or "intention" not in rule:
            raise ConfigError("incomplete_rule", str(i))
        if arch != "world" and arch not in arches:
            raise ConfigError("unknown_rule_archetype", str(arch))
        allowed = set(vocab_set)
        if arch != "world":
            allowed |= set((arches[arch].get("allowed_events") or []))
        if event not in allowed:
            raise ConfigError("unknown_event", "%s:%s" % (arch, event))
        _validate_seat((rule.get("state_delta") or {}).get("seat"),
                       "rules[%d].seat" % i)
        sd = rule.get("state_delta") or {}
        if any(k in sd for k in ("gamma", "gamma_kind", "tim")):
            raise ConfigError("gamma_immutable", "rules[%d]" % i)

    # Normalize TIM gammas on a copy so callers see the validated form.
    arches_out = {}
    for name, spec in arches.items():
        arches_out[name] = dict(spec)
    return HolonConfig(
        archetypes=arches_out,
        world=world_doc,
        rules=list(rules),
        source_dir="",
    )


def load_config(directory: str) -> HolonConfig:
    """Load and validate the three documents from a directory."""
    directory = os.path.abspath(directory)
    missing = [fn for fn in REQUIRED_FILES
               if not os.path.isfile(os.path.join(directory, fn))]
    if missing:
        raise ConfigError("missing_files", ",".join(missing))
    archetypes_doc = _read_json(os.path.join(directory, "archetypes.json"))
    world_doc = _read_json(os.path.join(directory, "world.json"))
    rules_doc = _read_json(os.path.join(directory, "rules.json"))
    cfg = validate_documents(archetypes_doc, world_doc, rules_doc)
    return HolonConfig(
        archetypes=cfg.archetypes,
        world=cfg.world,
        rules=cfg.rules,
        source_dir=directory,
    )
