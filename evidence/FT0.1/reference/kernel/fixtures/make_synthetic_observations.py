#!/usr/bin/env python3
"""Generate LABELED synthetic observations for the pilot_001 demonstration.

Every row carries synthetic=true + generator metadata (SPEC section 52).
The generator plants a routing-distance effect so the pipeline demo has
signal to find; that is a property of the GENERATOR, not of people.
"""
import json
import random
import sys

sys.path.insert(0, __file__.rsplit("/", 2)[0])
from pyref import core, empirical

GEN_VERSION = "synthgen-1.2"


def main(study_dir, out_path):
    spec = json.load(open(study_dir + "/study.json"))
    st = empirical.Study(study_dir.rsplit("/", 1)[0],
                         spec["study_id"])
    rng = random.Random(spec["randomization_seed"] + 1)
    params = {"seed": spec["randomization_seed"] + 1,
              "base_log_ms": 6.8, "subject_sd": 0.25, "noise_sd": 0.18,
              "per_excess_step": 0.22, "nonshortest_penalty": 0.15}
    subj_effect = {}
    rows = []
    for t in st.trials():
        sid = t["subject_id"]
        lock = st.current_typing(sid)
        tim = lock["primary_tim"]
        cond = spec["condition_definitions"][t["condition_id"]]
        inter = cond.get("intermediates", [])
        path = [cond["start_probe"]] + inter + [cond["designed_target_ie"]]
        dist = core.routing_distance(tim, path[0], path[-1])
        # v2.1 (synthgen-1.2): an instructed waypoint list is not a
        # unit-step path; its effective cost is the shortest lawful
        # completion through the waypoints in the pure routing cube.
        # The former per-step criterion mis-scored non-adjacent hops
        # (it treated ne->fe->ti as on-route and penalized "direct").
        effective = core.waypoint_route_length(tim, path)
        excess = effective - dist
        on_short = effective == dist
        if sid not in subj_effect:
            subj_effect[sid] = rng.gauss(0, params["subject_sd"])
        mu = (params["base_log_ms"] + subj_effect[sid]
              + params["per_excess_step"] * max(excess, 0)
              + (0 if on_short else params["nonshortest_penalty"]))
        latency = round(2.718281828 ** (mu + rng.gauss(0, params["noise_sd"])))
        rows.append({"trial_id": t["trial_id"], "subject_id": sid,
                     "raw": {"latency_ms": latency,
                             "accuracy": 1 if rng.random() > 0.08 else 0,
                             "timeout": False},
                     "instrument_version": "demo-1",
                     "synthetic": True,
                     "generator_version": GEN_VERSION,
                     "generator_parameters": params})
    with open(out_path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print("wrote %d synthetic observations -> %s" % (len(rows), out_path))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
