#!/usr/bin/env python3
"""compare_models.py — pairwise comparison table from model_comparison.json.
Reports differences in held-out error with standard errors; never converts
a comparison into proof of the underlying psychological theory."""
import json
import os
import sys


USAGE = "usage: compare_models.py <study_dir>"


def main():
    """Print the pairwise held-out-error table written by fit_models.py.

    Positive cell (row, column) means the row model had HIGHER held-out
    error, i.e. predicted worse. The table is descriptive: a difference
    here is a difference in out-of-sample prediction on this dataset and
    nothing more.
    """
    if len(sys.argv) != 2:
        sys.exit(USAGE)
    study_dir = sys.argv[1]
    path = os.path.join(study_dir, "model_comparison.json")
    if not os.path.exists(path):
        sys.exit("no model_comparison.json in %s — run `le analyze` first"
                 % study_dir)
    with open(path, encoding="utf-8") as fh:
        res = json.load(fh)
    models = res["models"]
    names = list(models)
    print("pairwise held-out MSE differences (row - column):")
    print("%14s" % "" + "".join("%14s" % n for n in names))
    for a in names:
        cells = []
        for b in names:
            d = models[a]["heldout_mse"] - models[b]["heldout_mse"]
            cells.append("%14.4f" % d)
        print("%14s" % a + "".join(cells))
    print("\nnote:", res["note"])


if __name__ == "__main__":
    main()
