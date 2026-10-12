"""Generative intention layer — intention + event production (spec 6, 8.6).

The default generator is deterministic and rule-based: it filters the
extended rule table (rules_v2.json) to entries that are

  * addressed to this Holon's archetype,
  * developmentally legal (optional min_center / min_bloom gates against
    the Development pillar), and
  * within the world's event vocabulary when one is supplied,

then scores candidates by memory grounding — overlap between the rule's
intention/event tokens and the vertices, apexes, and phase readings of
the Holon's active loops, with recently replayed loops weighing more —
and returns the best (intention, event) pair. Ties break lexicographically,
so two runs on the same packet always agree.

An optional `generator` callable (e.g. an LLM adapter) may replace the
scorer; its output is still validated against the rule table, so nothing
illegal ever reaches transition(). step() is the end-to-end driver:
assemble -> require_complete -> generate -> transition.
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Callable, Mapping, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyref import holon as H

from holon_tower.schema import bloom_index, vmeme_index
from intention import context as ctx

RULES_V2_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "rules_v2.json")

Result = Tuple[bool, object]

_TOKEN = re.compile(r"[a-z0-9_]+")


def load_rules(path: str = RULES_V2_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        doc = json.load(f)
    if not isinstance(doc, Mapping) or "rules" not in doc:
        raise ctx.ContextError("invalid_rules_doc", path)
    return doc


def _tokens(text: str) -> set:
    return set(_TOKEN.findall(str(text).lower()))


def _memory_tokens(memory: Mapping) -> Tuple[set, set]:
    """(all-loop tokens, recently-replayed tokens)."""
    def bag(loops):
        toks = set()
        for lp in loops:
            for v in lp["vertices"].values():
                toks |= _tokens(v)
            toks |= _tokens(lp["apex"])
            for reading in lp["phase_readings"].values():
                toks |= _tokens(reading)
        return toks
    return bag(memory["active_loops"]), bag(memory["recently_replayed"])


def _developmentally_legal(rule: Mapping, development: Mapping) -> bool:
    if development.get("version") == "tower_v2":
        return _legal_v2(rule, development)
    mc = rule.get("min_center")
    if mc is not None and vmeme_index(development["center"]) < vmeme_index(mc):
        return False
    mb = rule.get("min_bloom")
    if mb is not None and (bloom_index(development["bloom_stage"])
                           < bloom_index(mb)):
        return False
    if rule.get("requires_unsealed") and development["sealed"]:
        return False
    return True


def _legal_v2(rule: Mapping, development: Mapping) -> bool:
    """Gates against generated altitude. A rule may require a minimum
    altitude, or a specific retained capacity -- never a tier name, because
    under the generated law there are no tier names to require."""
    ma = rule.get("min_altitude")
    if ma is not None and development["altitude"] < ma:
        return False
    need = rule.get("requires_retained")
    if need is not None and not set(
            [need] if isinstance(need, str) else need) <= set(
            development["retained"]):
        return False
    # tower_v1-only gates are inert against a tower_v2 packet rather than
    # silently passing: a rule written for the old ladder does not apply.
    if rule.get("min_center") is not None or rule.get("min_bloom") is not None:
        return False
    return True


def candidates(packet: Mapping, rules: Mapping,
               event_vocabulary=None) -> list:
    packet = ctx.require_complete(packet)
    arch = packet.get("archetype")
    out = []
    for rule in rules["rules"]:
        if rule.get("archetype") != arch:
            continue
        if not _developmentally_legal(rule, packet["development"]):
            continue
        if event_vocabulary is not None and rule["event"] not in event_vocabulary:
            continue
        out.append(rule)
    return out


def score(rule: Mapping, packet: Mapping, bags=None) -> float:
    """`bags` is the (all, recent) token pair. Hoisted by the caller: it is
    a pure function of the packet, and rebuilding it once per candidate made
    scoring O(rules x loops x text) on every tick of every holon."""
    all_toks, recent_toks = bags if bags is not None \
        else _memory_tokens(packet["memory"])
    rule_toks = _tokens(rule["intention"]) | _tokens(rule["event"]) \
        | _tokens(" ".join(rule.get("grounding", [])))
    s = 0.0
    s += 2.0 * len(rule_toks & recent_toks)     # fresh memory weighs more
    s += 1.0 * len(rule_toks & all_toks)
    if rule.get("min_center") or rule.get("min_bloom"):
        s += 0.5                                 # developmental specificity
    return s


def generate(packet: Mapping, rules: Mapping, *,
             event_vocabulary=None,
             generator: Optional[Callable] = None) -> Result:
    """Produce (ok, {"intention", "event", "why"}) or (False, reason)."""
    try:
        cands = candidates(packet, rules, event_vocabulary)
    except ctx.ContextError as e:
        return False, e.reason
    if not cands:
        return False, "no_legal_rule"
    if generator is not None:
        pick = generator(packet, cands)
        chosen = next((r for r in cands
                       if r["intention"] == pick.get("intention")
                       and r["event"] == pick.get("event")), None)
        if chosen is None:
            return False, "generator_output_illegal"
        why = {"mode": "external_generator"}
    else:
        bags = _memory_tokens(packet["memory"])
        ranked = sorted(cands,
                        key=lambda r: (-score(r, packet, bags),
                                       r["intention"], r["event"]))
        chosen = ranked[0]
        why = {"mode": "rule_based",
               "score": score(chosen, packet, bags),
               "considered": len(cands)}
    return True, {"intention": chosen["intention"],
                  "event": chosen["event"], "why": why}


def step(holon, register, rules: Mapping, *,
         world_observation=None, other_holons=None,
         event_vocabulary=None, generator=None) -> Result:
    """End-to-end (spec 8.7): assemble -> generate -> transition.

    Returns (True, (holon', chosen)) or (False, reason). All state change
    goes through the kernel's transition(); the packet never mutates
    anything.
    """
    packet = ctx.assemble(holon, register,
                          world_observation=world_observation,
                          other_holons=other_holons)
    ok, out = generate(packet, rules, event_vocabulary=event_vocabulary,
                       generator=generator)
    if not ok:
        return False, out
    ok2, res = H.transition(holon, out["intention"], out["event"],
                            rules=rules)
    if not ok2:
        return False, "transition_refused:%s" % res
    return True, (res, out)
