"""Holonic Living Engine V1 — acceptance tests.

Uses the same check() style as verify_all. After the holon checks, runs
the existing v2 suite (verify_all) and fails if that suite fails.
`le verify all` is unchanged: this file is a separate gate.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from pyref.holon import (  # noqa: E402
    ChildRef, Holon, HolonError, ObsEnvelope, PureState,
    create, detach_child, embed_child, emit, empty_envelope,
    observe, parse_gamma, projection_depends_only_on_local,
    pure_projection, replace_domain, replace_foreign, set_parent,
    transition,
)
from pyref.holon_config import ConfigError, load_config  # noqa: E402
from pyref import core, oig  # noqa: E402

RESULTS = []
CONFIGS = os.path.join(HERE, "configs")
ALT_CONFIGS = os.path.join(HERE, "configs", "alt")


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    return bool(cond)


def _world_pair(cfg):
    world = cfg.create_world()
    guard = cfg.create_character("guard")
    walker = cfg.create_character("walker")
    return world, guard, walker


def verify_create_from_config():
    cfg = load_config(CONFIGS)
    world, guard, walker = _world_pair(cfg)
    check("holon.create.world_from_config",
          world.gamma == "structural:generic_v1"
          and world.pure_state.gamma_kind == "structural"
          and world.archetype == "world")
    check("holon.create.guard_tim_lsi",
          guard.gamma == "TIM:lsi"
          and guard.pure_state.gamma_kind == "tim"
          and guard.pure_state.tim == "lsi"
          and guard.pure_state.seat == 1
          and guard.archetype == "guard")
    check("holon.create.walker_untyped",
          walker.gamma == "untyped"
          and walker.pure_state.gamma_kind == "untyped"
          and walker.pure_state.tim is None)
    check("holon.create.same_kind_object",
          type(world) is type(guard) is type(walker) is Holon)
    check("holon.create.ids_opaque_distinct",
          len({world.id, guard.id, walker.id}) == 3
          and all(isinstance(h.id, str) and len(h.id) >= 8
                  for h in (world, guard, walker)))
    check("holon.create.no_names_in_identity",
          all("name" not in pure_projection(h)["content"]["foreign"]
              and "name" not in pure_projection(h)["pure_state"]
              for h in (world, guard, walker)))


def verify_transition_and_obs():
    cfg = load_config(CONFIGS)
    world, guard, walker = _world_pair(cfg)
    before = observe(guard, None)
    ok, guard2 = transition(guard, "scan", "perceive",
                            rules=cfg.rules, archetype="guard")
    check("holon.transition.perceive_ok", ok is True and isinstance(guard2, Holon))
    check("holon.transition.refreshes_obs",
          guard2.obs != before
          and guard2.obs.v != before.v)
    check("holon.transition.seat_to_6",
          guard2.pure_state.seat == 6)
    check("holon.transition.domain_its_set",
          guard2.content.domain.get("its") == "signal"
          and guard2.pure_state.domain_content.get("its") == "signal")
    # TIM path used oig: a domain key appearing should move N off empty.
    check("holon.transition.obs_uses_oig_for_tim",
          guard2.obs.n != ("none", "none")
          or guard2.obs.v != ("none", "none"))
    check("holon.transition.version_bumped",
          guard2.version == guard.version + 1)
    check("holon.transition.gamma_unchanged",
          guard2.gamma == guard.gamma and guard2.id == guard.id)

    # Parent is not mutated by the child's transition. It receives a summary
    # or an intentional event — never private state.
    summary = observe(guard2, None)
    check("holon.transition.parent_receives_envelope",
          isinstance(summary, ObsEnvelope)
          and not hasattr(summary, "pure_state")
          and not hasattr(summary, "content"))
    ok_e, ev = emit(guard2, {"kind": "alert"})
    check("holon.transition.parent_receives_event_only",
          ok_e and ev["from"] == guard2.id
          and "pure_state" not in ev
          and "content" not in ev
          and ev["event"]["kind"] == "alert")
    world2 = embed_child(world, guard2, summary)
    ref = world2.children[guard2.id]
    check("holon.transition.world_childref_is_summary",
          isinstance(ref, ChildRef)
          and isinstance(ref.summary, ObsEnvelope)
          and ref.id == guard2.id)

    ok_miss, err = transition(guard, "scan", "no_such_event",
                              rules=cfg.rules, archetype="guard")
    check("holon.transition.no_rule_is_error",
          ok_miss is False and err == "no_rule")


def verify_pure_projection():
    cfg = load_config(CONFIGS)
    world, guard, walker = _world_pair(cfg)
    secret_guard = create(
        "TIM:lsi",
        {"domain": {"its": "private_mark"}, "foreign": {"stash": 7}},
        seat=4, archetype="guard",
    )
    world2 = embed_child(world, secret_guard, observe(secret_guard, None))
    proj_world = pure_projection(world2)
    blob = json.dumps(proj_world, sort_keys=True, default=str)
    check("holon.projection.no_child_private_domain",
          "private_mark" not in blob and "stash" not in blob)
    check("holon.projection.no_children_key",
          "children" not in proj_world and "parent" not in proj_world)
    check("holon.projection.function_of_local_only",
          projection_depends_only_on_local(world2))
    # Same local identity, different children => same projection.
    world3 = embed_child(world2, walker, observe(walker, None))
    check("holon.projection.ignores_children",
          pure_projection(world2) == pure_projection(world3))
    check("holon.projection.guard_local_has_own_state",
          pure_projection(secret_guard)["pure_state"]["seat"] == 4
          and pure_projection(secret_guard)["content"]["domain"]["its"]
          == "private_mark")


def verify_embed_detach_boundary():
    cfg = load_config(CONFIGS)
    world, guard, walker = _world_pair(cfg)
    gsum = observe(guard, None)
    wsum = observe(walker, None)
    world2 = embed_child(world, guard, gsum)
    world2 = embed_child(world2, walker, wsum)
    check("holon.embed.two_children",
          set(world2.children) == {guard.id, walker.id})
    ref = world2.children[guard.id]
    check("holon.embed.ref_fields_only",
          set(ref.__dataclass_fields__) == {"id", "summary", "last_seen"})
    check("holon.embed.no_child_pure_state",
          not hasattr(ref, "pure_state")
          and not hasattr(ref.summary, "domain_content")
          and guard.pure_state.seat is not None
          and getattr(ref, "seat", None) is None)
    check("holon.embed.summary_is_envelope_not_content",
          isinstance(ref.summary, ObsEnvelope)
          and ref.summary.p in (0, 1))
    world3 = detach_child(world2, guard.id)
    check("holon.detach.removes_only_that_child",
          guard.id not in world3.children
          and walker.id in world3.children)
    try:
        detach_child(world3, guard.id)
        check("holon.detach.unknown_is_error", False)
    except HolonError as e:
        check("holon.detach.unknown_is_error", e.reason == "unknown_child")
    linked = set_parent(guard, world2.id)
    check("holon.set_parent.structural_only",
          linked.parent == world2.id
          and pure_projection(linked) == pure_projection(guard))


def verify_config_reload():
    cfg_a = load_config(CONFIGS)
    cfg_b = load_config(ALT_CONFIGS)
    wa = cfg_a.create_world()
    wb = cfg_b.create_world()
    ga = cfg_a.create_character("guard")
    gb = cfg_b.create_character("guard")
    ka = cfg_a.create_character("walker")
    kb = cfg_b.create_character("walker")
    check("holon.config.two_legal_worlds",
          wa.gamma == "structural:generic_v1"
          and wb.gamma == "structural:plaza_v1"
          and wa.gamma != wb.gamma)
    check("holon.config.guard_differs_without_kernel_edit",
          ga.pure_state.seat == 1 and gb.pure_state.seat == 3
          and ga.content.foreign.get("posture") == "watch"
          and gb.content.foreign.get("posture") == "patrol")
    check("holon.config.walker_gamma_differs",
          ka.gamma == "untyped" and kb.gamma == "structural:roamer_v1")
    check("holon.config.same_operations_on_both",
          type(wa) is type(wb) is Holon)

    # Mutated copy in a temp dir also loads as a different legal world.
    with tempfile.TemporaryDirectory() as td:
        for fn in ("archetypes.json", "world.json", "rules.json"):
            with open(os.path.join(CONFIGS, fn), encoding="utf-8") as src:
                data = json.load(src)
            if fn == "world.json":
                data["world_gamma"] = "structural:mutated_v1"
                data["initial_foreign"] = {"phase": "mutated"}
            with open(os.path.join(td, fn), "w", encoding="utf-8") as out:
                json.dump(data, out)
        cfg_c = load_config(td)
        wc = cfg_c.create_world()
        check("holon.config.mutated_copy_legal_and_different",
              wc.gamma == "structural:mutated_v1"
              and wc.content.foreign.get("phase") == "mutated"
              and wc.gamma != wa.gamma)


def verify_untyped_and_gamma_freeze():
    u = create("untyped", {"domain": {}, "foreign": {"motion": "idle"}})
    check("holon.untyped.works_without_tim",
          u.pure_state.gamma_kind == "untyped"
          and u.pure_state.tim is None
          and isinstance(observe(u, None), ObsEnvelope))
    env = observe(u, None)
    check("holon.untyped.empty_legal_envelope",
          env.v == ("none", "none")
          and env.n == ("none", "none")
          and env.k == frozenset()
          and env.p == 0
          and env.r is None
          and env.depth == ("none", "none"))
    # Empty supports are the 12-bit zeros of the same lattice.
    z = oig.support_of_depths("none", "none")
    check("holon.untyped.same_4x3_lattice",
          env.v_support() == z and env.n_support() == z
          and set(z) == set(oig.QUOTIENTS)
          and all(bit == 0 for bit in z.values()))
    try:
        u.gamma = "TIM:lsi"
        check("holon.gamma.assignment_raises", False)
    except (AttributeError, TypeError, HolonError):
        check("holon.gamma.assignment_raises", True)
    other = create("TIM:lsi", {"domain": {}, "foreign": {}})
    check("holon.gamma.change_is_new_holon",
          other.id != u.id and other.gamma != u.gamma)
    try:
        ok, _ = transition(u, "x", "y", rules=[
            {"archetype": None, "intention": "x", "event": "y",
             "state_delta": {"gamma": "TIM:lsi"}}
        ], archetype=None)
        # lookup uses archetype None; if a rule matched, gamma change errors.
        check("holon.gamma.not_via_delta",
              ok is False)
    except HolonError as e:
        check("holon.gamma.not_via_delta", e.reason == "gamma_immutable")


def verify_df_and_surface():
    h = create("TIM:lsi", {"domain": {"its": "a"}, "foreign": {"tag": 1}})
    h2 = replace_domain(h, {"we": "b"})
    check("holon.df.domain_replace_keeps_foreign",
          h2.content.domain == {"we": "b"}
          and h2.content.foreign == {"tag": 1})
    h3 = replace_foreign(h2, {"tag": 2})
    check("holon.df.foreign_replace_keeps_domain",
          h3.content.foreign == {"tag": 2}
          and h3.content.domain == {"we": "b"})
    try:
        create("untyped", {"domain": {}, "foreign": {"name": "x"}})
        check("holon.surface.rejected_as_identity_key", False)
    except HolonError as e:
        check("holon.surface.rejected_as_identity_key", e.reason == "surface_key")
    try:
        create("TIM:lsi", {"domain": {}, "foreign": {}}, seat=9)
        check("holon.seat.rejects_out_of_range", False)
    except HolonError as e:
        check("holon.seat.rejects_out_of_range", e.reason == "invalid_seat")
    ps = create("untyped", {"domain": {}, "foreign": {}}).pure_state
    check("holon.surface.no_surface_keys_in_pure_state",
          SURFACE_OK(ps))


def SURFACE_OK(ps: PureState) -> bool:
    from pyref.holon import SURFACE_KEYS
    return not (set(ps.domain_content) & SURFACE_KEYS) and not any(
        k in SURFACE_KEYS for k in ("name", "dialogue", "appearance")
        if hasattr(ps, k)
    )


def verify_invalid_config_rejected():
    with tempfile.TemporaryDirectory() as td:
        with open(os.path.join(CONFIGS, "archetypes.json"), encoding="utf-8") as f:
            arches = json.load(f)
        with open(os.path.join(CONFIGS, "world.json"), encoding="utf-8") as f:
            world = json.load(f)
        with open(os.path.join(CONFIGS, "rules.json"), encoding="utf-8") as f:
            rules = json.load(f)
        arches["archetypes"]["guard"]["gamma"] = "TIM:not_a_tim"
        for fn, data in (("archetypes.json", arches),
                         ("world.json", world),
                         ("rules.json", rules)):
            with open(os.path.join(td, fn), "w", encoding="utf-8") as out:
                json.dump(data, out)
        try:
            load_config(td)
            check("holon.config.reject_bad_gamma", False)
        except ConfigError as e:
            check("holon.config.reject_bad_gamma", e.reason == "invalid_gamma")

    with tempfile.TemporaryDirectory() as td:
        with open(os.path.join(CONFIGS, "archetypes.json"), encoding="utf-8") as f:
            arches = json.load(f)
        with open(os.path.join(CONFIGS, "world.json"), encoding="utf-8") as f:
            world = json.load(f)
        with open(os.path.join(CONFIGS, "rules.json"), encoding="utf-8") as f:
            rules = json.load(f)
        rules["rules"].append({
            "archetype": "guard",
            "intention": "shout",
            "event": "banter",
            "content_delta": {},
        })
        for fn, data in (("archetypes.json", arches),
                         ("world.json", world),
                         ("rules.json", rules)):
            with open(os.path.join(td, fn), "w", encoding="utf-8") as out:
                json.dump(data, out)
        try:
            load_config(td)
            check("holon.config.reject_unknown_event", False)
        except ConfigError as e:
            check("holon.config.reject_unknown_event", e.reason == "unknown_event")

    with tempfile.TemporaryDirectory() as td:
        with open(os.path.join(CONFIGS, "archetypes.json"), encoding="utf-8") as f:
            arches = json.load(f)
        with open(os.path.join(CONFIGS, "world.json"), encoding="utf-8") as f:
            world = json.load(f)
        with open(os.path.join(CONFIGS, "rules.json"), encoding="utf-8") as f:
            rules = json.load(f)
        arches["archetypes"]["guard"]["initial_content_schema"]["foreign"]["dialogue"] = "hi"
        for fn, data in (("archetypes.json", arches),
                         ("world.json", world),
                         ("rules.json", rules)):
            with open(os.path.join(td, fn), "w", encoding="utf-8") as out:
                json.dump(data, out)
        try:
            load_config(td)
            check("holon.config.reject_surface_key", False)
        except ConfigError as e:
            check("holon.config.reject_surface_key", e.reason == "surface_key")


def verify_tim_not_required_and_oig_reuse():
    s = create("structural:generic_v1", {"domain": {}, "foreign": {}})
    check("holon.structural.empty_envelope",
          observe(s, None).r is None and observe(s, None).p == 0)
    # TIM observe after a real D change matches oig.summarize_trajectory.
    h = create("TIM:lsi", {"domain": {}, "foreign": {}})
    ok, h2 = transition(h, "scan", "perceive", rules=[{
        "archetype": "guard",
        "intention": "scan",
        "event": "perceive",
        "content_delta": {"set_domain": {"its": "signal"}},
    }], archetype="guard")
    path = list(h2.trajectory)
    expected = oig.summarize_trajectory("lsi", path)
    check("holon.oig.matches_summarize_trajectory",
          ok and tuple(h2.obs.v) == tuple(expected["V"])
          and tuple(h2.obs.n) == tuple(expected["N"])
          and set(h2.obs.k) == set(expected["K"])
          and h2.obs.p == expected["parity"])
    filled = observe(h2, "R")
    check("holon.oig.lazy_r_optional",
          h2.obs.r is None and filled.r is not None)


def verify_existing_v2_suite():
    # Import-run the existing suite (same path le.py verify all uses).
    # verify_all.py cannot be exec'd as a loose script: it has relative imports.
    from pyref import verify_all
    saved = list(verify_all.RESULTS)
    verify_all.RESULTS.clear()
    try:
        rc = verify_all.run()
        n = len(verify_all.RESULTS)
        passed = sum(1 for _, ok, _ in verify_all.RESULTS if ok)
    finally:
        verify_all.RESULTS[:] = saved
    check("holon.v2.verify_all_exit_0", rc == 0, "exit %s" % rc)
    check("holon.v2.verify_all_118", n == 118 and passed == 118,
          "%s/%s passed" % (passed, n))


def run():
    verify_create_from_config()
    verify_transition_and_obs()
    verify_pure_projection()
    verify_embed_detach_boundary()
    verify_config_reload()
    verify_untyped_and_gamma_freeze()
    verify_df_and_surface()
    verify_invalid_config_rejected()
    verify_tim_not_required_and_oig_reuse()
    verify_existing_v2_suite()
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = [(n, d) for n, ok, d in RESULTS if not ok]
    print("Holonic Living Engine V1 — acceptance run")
    print("=" * 64)
    for n, ok, d in RESULTS:
        print("%s  %s%s" % ("PASS" if ok else "FAIL", n,
                            ("  (" + d + ")") if d and not ok else ""))
    print("=" * 64)
    print("%d/%d passed" % (passed, len(RESULTS)))
    if failed:
        for n, d in failed:
            print("FAILED:", n, d)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
