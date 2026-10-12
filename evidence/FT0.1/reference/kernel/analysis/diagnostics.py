#!/usr/bin/env python3
"""diagnostics.py — task/observation diagnostics (SPEC sections 41, 44).
Floor/ceiling, practice slopes, latency distribution shape, per-condition
summaries, coder agreement summary.  Descriptive only."""
import json
import os
import sys
from collections import defaultdict

import numpy as np


USAGE = "usage: diagnostics.py <study_dir>"


def main():
    """Describe the blind dataset before anyone looks at a model.

    Per participant: trial count, median latency, IQR, mean accuracy, and
    a FLOOR?/CEILING? flag when accuracy leaves too little room for a
    condition effect to show up at all. Descriptive only — this runs on
    the blind export, which carries no TIM.
    """
    if len(sys.argv) != 2:
        sys.exit(USAGE)
    study_dir = sys.argv[1]
    path = os.path.join(study_dir, "blind_dataset.jsonl")
    if not os.path.exists(path):
        sys.exit("no blind_dataset.jsonl in %s — run `le export blind` first"
                 % study_dir)
    with open(path, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    lat = defaultdict(list)
    acc = defaultdict(list)
    for r in rows:
        if r.get("raw_latency_ms") is not None:
            lat[r["subject_id"]].append(float(r["raw_latency_ms"]))
        if r.get("raw_accuracy") is not None:
            acc[r["subject_id"]].append(float(r["raw_accuracy"]))
    print("participants:", len(lat))
    for s in sorted(lat):
        a = np.array(lat[s])
        acc_m = np.mean(acc[s]) if acc[s] else float("nan")
        print("  %s  n=%d  median latency %.0f ms  IQR [%.0f, %.0f]  "
              "accuracy %.2f%s"
              % (s, len(a), np.median(a), np.percentile(a, 25),
                 np.percentile(a, 75), acc_m,
                 "  CEILING?" if acc_m > 0.97 else
                 "  FLOOR?" if acc_m < 0.55 else ""))
    if lat:
        allv = np.concatenate([np.array(v) for v in lat.values()])
        print("overall latency skew (log recommended): mean %.0f, "
              "median %.0f" % (allv.mean(), np.median(allv)))


if __name__ == "__main__":
    main()
