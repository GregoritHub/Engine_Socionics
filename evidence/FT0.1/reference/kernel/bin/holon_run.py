#!/usr/bin/env python3
"""Live Holonic Living Engine V1 run. Data in, Holons out. No game loop."""
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from pyref.holon import embed_child, emit, observe, pure_projection, set_parent, transition
from pyref.holon_config import load_config


def _env(e):
    return {
        "v": list(e.v),
        "n": list(e.n),
        "k": sorted(str(x) for x in e.k),
        "p": e.p,
        "depth": list(e.depth),
        "has_r": e.r is not None,
    }


def run(config_dir=None):
    config_dir = config_dir or os.path.join(HERE, "configs")
    cfg = load_config(config_dir)
    world = cfg.create_world()
    guard = cfg.create_character("guard")
    walker = cfg.create_character("walker")
    guard = set_parent(guard, world.id)
    walker = set_parent(walker, world.id)
    world = embed_child(world, guard, observe(guard))
    world = embed_child(world, walker, observe(walker))

    ok, guard2 = transition(guard, "scan", "perceive", rules=cfg.rules)
    if not ok:
        raise SystemExit("transition failed: %s" % guard2)
    ok_ev, ev = emit(guard2, "signal_seen")
    world2 = embed_child(world, guard2, observe(guard2))

    parent_sees = {
        cid: {
            "id": ref.id,
            "last_seen": ref.last_seen,
            "summary": _env(ref.summary),
        }
        for cid, ref in world2.children.items()
    }
    report = {
        "config": config_dir,
        "world": {
            "id": world2.id,
            "gamma": world2.gamma,
            "child_ids": sorted(world2.children),
            "parent_sees": parent_sees,
            "projection_has_children": "children" in pure_projection(world2),
        },
        "guard": {
            "id": guard2.id,
            "gamma": guard2.gamma,
            "seat_before": guard.pure_state.seat,
            "seat_after": guard2.pure_state.seat,
            "domain_after": dict(guard2.content.domain),
            "obs": _env(observe(guard2)),
            "projection": pure_projection(guard2),
        },
        "walker": {
            "id": walker.id,
            "gamma": walker.gamma,
            "obs": _env(observe(walker)),
            "projection": pure_projection(walker),
        },
        "emitted": ev if ok_ev else None,
        "boundary": {
            "parent_has_guard_pure_state": any(
                "pure_state" in json.dumps(v) for v in parent_sees.values()
            ),
            "parent_has_guard_content": any(
                "domain" in json.dumps(v) and "its" in json.dumps(v)
                for v in parent_sees.values()
            ),
        },
    }
    return report


def main(argv):
    directory = argv[0] if argv else None
    report = run(directory)
    print(json.dumps(report, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
