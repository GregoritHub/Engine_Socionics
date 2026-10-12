#!/usr/bin/env python3
"""power_simulation.py — simulation-based power for the preregistered
route contrast (SPEC section 54).  Sample size is NOT hard-coded: power is
simulated from pilot-estimated variance components supplied as arguments.

All simulated data are labeled synthetic; this tool informs design only and
its output is never an empirical result.
"""
import argparse
import json

import numpy as np


def simulate_once(rng, n_subj, n_rep, route_effect, sd_between, sd_within,
                  dropout):
    """One simulated study. Returns True if it would have detected the effect.

    Each retained participant contributes a paired difference (direct minus
    routed) around their own baseline, so between-subject variance drops out
    the way it does in the real within-subject design. Averaging n_rep
    trials per condition is modelled by shrinking the within-subject SD by
    sqrt(n_rep) rather than by simulating each trial.

    Fewer than three surviving participants counts as a non-detection, not
    an error: that is what dropout does to a small design.
    """
    keep = rng.random(n_subj) > dropout
    diffs = []
    for s in range(n_subj):
        if not keep[s]:
            continue
        base = rng.normal(0, sd_between)
        direct = base + rng.normal(0, sd_within / np.sqrt(n_rep))
        routed = base - route_effect + rng.normal(0, sd_within / np.sqrt(n_rep))
        diffs.append(direct - routed)
    diffs = np.array(diffs)
    if len(diffs) < 3:
        return False
    t = diffs.mean() / (diffs.std(ddof=1) / np.sqrt(len(diffs)))
    # Two-sided paired t at alpha = .05. SciPy is not a dependency here, so
    # the critical value is the normal 1.96 plus a small-sample correction
    # that inflates it as df shrinks (df=7 -> ~2.25, against the exact
    # t-critical 2.365). The approximation is slightly ANTI-conservative at
    # small n, so treat the low-n rows of the table as an upper bound on
    # power rather than an estimate of it.
    return abs(t) > 1.96 + 2.0 / max(len(diffs) - 1, 1)


def main():
    """Sweep participant counts and report simulated power for each.

    Every variance component is a required argument: nothing about sample
    size is hard-coded, because a power figure is only meaningful relative
    to pilot-estimated variance that someone actually measured.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--route-effect", type=float, required=True,
                    help="pilot-estimated route effect on log latency")
    ap.add_argument("--sd-between", type=float, required=True)
    ap.add_argument("--sd-within", type=float, required=True)
    ap.add_argument("--reps", type=int, default=20,
                    help="repeated trials per condition per participant")
    ap.add_argument("--dropout", type=float, default=0.1)
    ap.add_argument("--sims", type=int, default=2000)
    ap.add_argument("--out", default="power_report.json")
    args = ap.parse_args()
    rng = np.random.default_rng(7)
    table = {}
    for n in [8, 12, 16, 24, 32, 48, 64]:
        hits = sum(simulate_once(rng, n, args.reps, args.route_effect,
                                 args.sd_between, args.sd_within,
                                 args.dropout)
                   for _ in range(args.sims))
        table[n] = hits / args.sims
        print("n_subjects=%3d  simulated power=%.3f" % (n, table[n]))
    report = {"synthetic": True, "assumptions": vars(args),
              "power_by_n": table,
              "note": "simulation for design only; not an empirical result"}
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
