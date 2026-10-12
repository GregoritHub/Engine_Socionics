#!/usr/bin/env python3
"""Holonic Living Engine V2 acceptance suite.

Covers, in order: kernel purity (SHA-256 manifest + V1 suites re-run),
the Development pillar (Holon Tower), the Memory pillar (Fool's Memory
Path), the intention layer, and the spec 8.7 end-to-end walk.

Run:  python3 verify_v2.py
Exit 0 iff every check passes. Known environmental gap: the shipped V1
archive omits apps/le_legacy, so the V1 suites are asserted to fail on
exactly that absence and nothing else.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from pyref import holon as H                       # noqa: E402
from holon_tower import schema as TS, tree, seal   # noqa: E402
from fools_memory import schema as FS, encode, retrieve, store  # noqa: E402
from intention import context as ctx, generate as gen           # noqa: E402

PASSED = 0
FAILED = []


def check(name, ok, note=""):
    global PASSED
    if ok:
        PASSED += 1
        print("PASS  %s" % name)
    else:
        FAILED.append((name, note))
        print("FAIL  %s  %s" % (name, ("(%s)" % note) if note else ""))


def raises(fn, reason):
    try:
        fn()
        return False
    except Exception as e:
        return getattr(e, "reason", None) == reason


# ===========================================================================
# Kernel purity
# ===========================================================================

def verify_kernel():
    man = json.load(open(os.path.join(HERE, "manifests",
                                      "kernel_sha256.json")))
    same = True
    for fname, want in man["files"].items():
        p = os.path.join(HERE, "pyref", fname)
        got = hashlib.sha256(open(p, "rb").read()).hexdigest() \
            if os.path.exists(p) else None
        if got != want:
            same = False
    check("v2.kernel.sha256_manifest_matches", same,
          "pyref byte-identical to shipped V1 archive")

    r = subprocess.run([sys.executable, os.path.join(HERE, "bin", "le.py"),
                        "verify", "all"], capture_output=True, text=True,
                       cwd=HERE)
    fails = set(re.findall(r"^FAIL\s+(\S+)", r.stdout, re.M))
    check("v2.kernel.v1_suite_only_known_legacy_gap",
          fails <= {"legacy.frozen_v11_sources_present"},
          "unexpected: %s" % sorted(fails - {"legacy.frozen_v11_sources_present"}))
    check("v2.kernel.v1_suite_substantive_count",
          "116/117 passed" in r.stdout, r.stdout.strip().splitlines()[-1]
          if r.stdout.strip() else "no output")

    r2 = subprocess.run([sys.executable,
                         os.path.join(HERE, "pyref", "verify_holon.py")],
                        capture_output=True, text=True, cwd=HERE)
    hfails = set(re.findall(r"^FAIL\s+(\S+)", r2.stdout, re.M))
    known = {"holon.v2.verify_all_exit_0", "holon.v2.verify_all_118",
             "legacy.frozen_v11_sources_present"}
    check("v2.kernel.holon_suite_only_legacy_cascade", hfails <= known,
          "unexpected: %s" % sorted(hfails - known))


# ===========================================================================
# Development pillar — Holon Tower
# ===========================================================================

def verify_tower():
    check("tower.grid_is_36_cells", len(TS.GRID_CELLS) == 36
          and len(set(TS.GRID_CELLS)) == 36)

    spec_example = {
        "version": "tower_v1", "center": "L5",
        "active_cells": [{"vmeme": "L5", "quadrant": "I"}],
        "bloom_stage": "Apply", "sealed": False, "sealed_at": None,
    }
    ok = True
    try:
        TS.validate_cape_phase(spec_example)
    except Exception:
        ok = False
    check("tower.schema_accepts_spec_example", ok)
    check("tower.schema_rejects_bad_vmeme",
          raises(lambda: TS.validate_cape_phase(
              dict(spec_example, center="L10")), "invalid_center"))
    check("tower.schema_rejects_bad_bloom",
          raises(lambda: TS.validate_cape_phase(
              dict(spec_example, bloom_stage="Memorize")),
              "invalid_bloom_stage"))
    check("tower.schema_rejects_duplicate_cell",
          raises(lambda: TS.validate_cape_phase(dict(
              spec_example,
              active_cells=[{"vmeme": "L5", "quadrant": "I"}] * 2)),
              "duplicate_cell"))

    t = tree.new_tower("L1")
    check("tower.new_tower_legal", t["center"] == "L1"
          and t["bloom_stage"] == "Remember" and not t["sealed"])
    check("tower.activate_duplicate_rejected",
          raises(lambda: tree.activate_cell(t, "L1", "I"),
                 "cell_already_active"))
    check("tower.activate_skip_level_rejected",
          raises(lambda: tree.activate_cell(t, "L3", "I"), "skips_level"))
    check("tower.advance_requires_all_quadrants",
          raises(lambda: tree.advance_center(
              tree.set_bloom(t, "Apply")), "advance_illegal"))

    full = t
    for q in ("We", "It", "Its"):
        full = tree.activate_cell(full, "L1", q)
    full = tree.set_bloom(full, "Apply")
    adv = tree.advance_center(full)
    check("tower.advance_moves_center_resets_bloom",
          adv["center"] == "L2" and adv["bloom_stage"] == "Remember"
          and tree.is_active(adv, "L2", "I"))
    check("tower.bloom_monotone_within_center",
          raises(lambda: tree.set_bloom(full, "Remember"),
                 "bloom_regression"))

    sealed = seal.seal(adv, at=100)
    check("tower.seal_sets_flag_and_time",
          sealed["sealed"] and sealed["sealed_at"] == 100)
    check("tower.sealed_rejects_mutation",
          raises(lambda: tree.activate_cell(sealed, "L2", "We"),
                 "tower_sealed")
          and raises(lambda: tree.advance_center(sealed), "tower_sealed")
          and raises(lambda: tree.set_bloom(sealed, "Create"),
                     "tower_sealed"))
    check("tower.seal_is_one_way",
          not hasattr(seal, "unseal")
          and raises(lambda: seal.seal(sealed, at=101), "already_sealed"))

    sh = tree.new_shells()
    check("tower.shells_particularity_guard_locked",
          raises(lambda: TS.validate_shells(
              dict(sh, particularity_guard=False)),
              "particularity_guard_disabled"))
    sh2 = tree.activate_shell(sh, "witness")
    check("tower.shell_activation_appends",
          sh2["active_shells"] == ["witness"]
          and sh["active_shells"] == [])

    # kernel application: computed delta through transition()
    hol = H.create("TIM:lsi", {"domain": {"i": "watch"}, "foreign": {}},
                   seat=6, archetype="scholar")
    rules = tree.materialize_rule("scholar", "ascend", "insight",
                                  tower=adv, shells=sh2)
    ok2, hol2 = H.transition(hol, "ascend", "insight", rules=rules)
    check("tower.delta_lands_via_transition",
          ok2 and hol2.pure_state.cape_phase["center"] == "L2"
          and hol2.pure_state.shells["active_shells"] == ["witness"]
          and hol2.version == hol.version + 1)
    check("tower.transition_extends_trajectory",
          ok2 and len(hol2.trajectory) == len(hol.trajectory) + 1)
    check("tower.projection_carries_development",
          ok2 and H.pure_projection(hol2)["pure_state"]["cape_phase"][
              "center"] == "L2")


# ===========================================================================
# Memory pillar — Fool's Memory Path
# ===========================================================================

SPEC_LOOP = {
    "id": "b5e0c6a1c0de4bd0a8f3d0f1e2a3b4c5",
    "version": "fools_v1",
    "residue": 5,
    "suit": "Coin",
    "rank": 3,
    "band": "4-18",
    "vertices": {"A": "obligation", "B": "liquidity", "C": "penalty"},
    "apex": "due_date",
    "phase_readings": {
        "super_ego": "inherit the rule (pay on time)",
        "ego": "calibrate tactics under pressure",
    },
    "created_at": 0,
    "last_replayed": 0,
    "strength": 1.0,
}


def verify_memory():
    ok = True
    try:
        FS.validate_loop(SPEC_LOOP)
    except Exception:
        ok = False
    check("fools.schema_accepts_spec_example", ok)
    check("fools.fool_is_cursor_never_address",
          raises(lambda: FS.validate_loop(dict(SPEC_LOOP, residue=0)),
                 "fool_not_addressable")
          and raises(lambda: retrieve.locate([], residue=0),
                     "fool_not_addressable"))
    check("fools.residue_range_enforced",
          raises(lambda: FS.validate_loop(dict(SPEC_LOOP, residue=10)),
                 "invalid_residue"))
    check("fools.suit_partner_involution",
          all(FS.suit_partner(FS.suit_partner(s)) == s for s in FS.SUITS)
          and FS.suit_partner("Coin") == "Diamond"
          and FS.suit_partner("Cup") == "Heart")
    check("fools.courts_map_11_to_14",
          FS.normalize_rank("Page") == 11 and FS.normalize_rank("King") == 14
          and raises(lambda: FS.normalize_rank(0), "invalid_rank")
          and raises(lambda: FS.normalize_rank(15), "invalid_rank"))

    pv = FS.phase_values(5, "4-18")
    check("fools.band_4_18_residue_5_gives_se5_ego14_no_identity",
          pv == {"super_ego": 5, "ego": 14})
    check("fools.phase_outside_band_rejected",
          raises(lambda: FS.validate_loop(dict(
              SPEC_LOOP, phase_readings=dict(
                  SPEC_LOOP["phase_readings"],
                  identity="x"))), "phase_outside_band"))
    check("fools.addressability_store_super_ego_only",
          raises(lambda: FS.validate_loop(
              dict(SPEC_LOOP, storage_phase="ego")),
              "store_super_ego_only"))

    enc = encode.encode(
        residue=6, suit="Sword", edge_count=4,
        vertices={"A": "claim", "B": "evidence", "C": "verdict"},
        apex="tribunal",
        phase_readings={"super_ego": "receive the charge",
                        "ego": "weigh it yourself"},
        phases_needed=["super_ego", "ego"], created_at=7)
    check("fools.encode_four_decisions_valid",
          enc["band"] == "6-15" and enc["rank"] == 4
          and enc["storage_phase"] == "super_ego")
    check("fools.encode_band_xor_phases",
          raises(lambda: encode.encode(
              residue=6, suit="Sword", edge_count=4,
              vertices=enc["vertices"], apex="tribunal",
              phase_readings=enc["phase_readings"]), "band_xor_phases"))

    reg = store.MemoryRegister()
    reg.put("h1", SPEC_LOOP)
    reg.put("h1", enc)
    check("fools.put_get_round_trip", len(reg.loops("h1")) == 2)
    check("fools.duplicate_id_rejected",
          raises(lambda: reg.put("h1", SPEC_LOOP), "duplicate_loop_id"))
    before = [lp["id"] for lp in reg.loops("h1")]
    third = encode.encode(
        residue=5, suit="Diamond", edge_count=3,
        vertices={"A": "price", "B": "value", "C": "cost"}, apex="market",
        phase_readings={"super_ego": "quote the ledger"},
        phases_needed=["super_ego"], created_at=9)
    reg.put("h1", third)
    after = [lp["id"] for lp in reg.loops("h1")]
    check("fools.put_never_erases_distinction",
          after[:2] == before and len(after) == 3)

    seq = retrieve.replay(SPEC_LOOP)
    check("fools.replay_order_A_apex_B_C_A",
          [s for s, _ in seq] == ["A", "apex", "B", "C", "A"]
          and seq[1][1] == "due_date" and seq[0][1] == seq[4][1])

    snap = retrieve.snap_missing(reg.loops("h1"), 5, "Coin", 3,
                                 {"A": "obligation", "C": "penalty"})
    check("fools.snap_missing_vertex", snap["missing"] == "B"
          and snap["value"] == "liquidity")

    vc = retrieve.vertical_check(SPEC_LOOP)
    check("fools.vertical_check_plus9",
          vc["ladder"]["super_ego"]["value"] == 5
          and vc["ladder"]["ego"]["value"] == 14
          and vc["ladder"]["ego"]["derived"] is True
          and "identity" not in vc["ladder"])

    hc = retrieve.horizontal_check(SPEC_LOOP, reg.loops("h1"))
    check("fools.horizontal_check_partner_address",
          hc["partner_suit"] == "Diamond"
          and hc["address"] == (5, "Diamond", 3)
          and hc["translated_loops"] == [third["id"]])

    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "reg.json")
        reg.save(p)
        reg2 = store.MemoryRegister.load(p)
        check("fools.persistence_round_trip",
              reg2.loops("h1") == reg.loops("h1"))

    upd = reg.mark_replayed("h1", third["id"], at=42)
    check("fools.replay_marks_strength_and_time",
          upd["last_replayed"] == 42 and upd["strength"] == 1.25)


# ===========================================================================
# Intention layer + end-to-end
# ===========================================================================

def verify_intention():
    rules = gen.load_rules()
    reg = store.MemoryRegister()

    tower = tree.new_tower("L1")
    hol = H.create("TIM:lsi", {"domain": {"i": "watch"}, "foreign": {}},
                   seat=6, cape_phase=tower, archetype="scholar")

    # incomplete pillars: no memory yet
    pkt0 = ctx.assemble(hol, reg)
    ok0, why0 = gen.generate(pkt0, rules)
    check("intent.refuses_without_memory_pillar",
          not ok0 and why0 == "incomplete_pillars")

    reg.put(hol.id, SPEC_LOOP)

    # incomplete pillars: no development
    bare = H.create("TIM:lsi", {"domain": {}, "foreign": {}},
                    archetype="scholar")
    reg.put(bare.id, SPEC_LOOP)
    okb, whyb = gen.generate(ctx.assemble(bare, reg), rules)
    check("intent.refuses_without_development_pillar",
          not okb and whyb == "incomplete_pillars")

    pkt = ctx.assemble(hol, reg)
    check("intent.packet_has_spec6_shape",
          all(k in pkt for k in ("holon_id", "identity", "development",
                                 "memory", "world_observation",
                                 "other_holons"))
          and pkt["identity"]["gamma"] == "TIM:lsi"
          and pkt["identity"]["seat"] == 6
          and pkt["development"]["center"] == "L1"
          and pkt["memory"]["relevant_residues"] == [5])

    ok1, out1 = gen.generate(pkt, rules)
    check("intent.memory_grounds_choice",
          ok1 and out1["intention"] == "settle_obligation"
          and out1["event"] == "due_date")
    ok1b, out1b = gen.generate(ctx.assemble(hol, reg), rules)
    check("intent.deterministic",
          ok1b and (out1["intention"], out1["event"])
          == (out1b["intention"], out1b["event"]))

    cands = gen.candidates(pkt, rules)
    names = {r["intention"] for r in cands}
    check("intent.development_gates_filter",
          "teach" not in names and "study" not in names
          and "settle_obligation" in names and "idle" in names)

    grown = tree.set_bloom(tower, "Understand")
    hol_g = H.create("TIM:lsi", {"domain": {}, "foreign": {}},
                     cape_phase=grown, archetype="scholar")
    reg.put(hol_g.id, SPEC_LOOP)
    names_g = {r["intention"]
               for r in gen.candidates(ctx.assemble(hol_g, reg), rules)}
    check("intent.bloom_unlocks_study",
          "study" in names_g and "teach" not in names_g)

    bad = lambda packet, cands: {"intention": "fly", "event": "moon"}
    okx, whyx = gen.generate(pkt, rules, generator=bad)
    check("intent.external_generator_validated",
          not okx and whyx == "generator_output_illegal")

    # ---- spec 8.7 end-to-end -------------------------------------------
    ok2, res = gen.step(hol, reg, rules)
    if ok2:
        hol2, chosen = res
    check("e2e.step_transitions",
          ok2 and hol2.version == hol.version + 1
          and chosen["intention"] == "settle_obligation")
    check("e2e.content_delta_applied",
          ok2 and hol2.content.domain.get("it") == "payment")
    env = H.observe(hol2)
    check("e2e.observe_returns_legal_envelope",
          env.v is not None and isinstance(env.k, frozenset))
    check("e2e.kernel_projection_local_only",
          H.projection_depends_only_on_local(hol2))


def main():
    print("Holonic Living Engine V2 acceptance")
    print("=" * 64)
    verify_kernel()
    verify_tower()
    verify_memory()
    verify_intention()
    print("=" * 64)
    total = PASSED + len(FAILED)
    print("%d/%d passed" % (PASSED, total))
    for name, note in FAILED:
        print("FAILED: %s %s" % (name, note))
    return 0 if not FAILED else 1


if __name__ == "__main__":
    sys.exit(main())
