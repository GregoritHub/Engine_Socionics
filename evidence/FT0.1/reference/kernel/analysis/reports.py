#!/usr/bin/env python3
"""reports.py — study report distinguishing result classes (SPEC section 63):
descriptive / confirmatory / exploratory / model comparison / parameter
estimate / negative control / assumption violation.  Effects with
uncertainty; not only p-values; significance is never proof of Socionics."""
import json
import os
import sys


USAGE = "usage: reports.py <study_dir>"


def main():
    """Render REPORT.md, keeping the result classes visibly separated.

    The synthetic banner is not decoration: a demonstration run and an
    empirical run produce the same file name, and the header is what
    stops the two being confused later.
    """
    if len(sys.argv) != 2:
        sys.exit(USAGE)
    study_dir = sys.argv[1]
    study_id = os.path.basename(study_dir.rstrip("/"))
    lines = ["# Study report — %s" % study_id, ""]
    spec_path = os.path.join(study_dir, "study.json")
    synthetic = False
    if os.path.exists(spec_path):
        with open(spec_path, encoding="utf-8") as fh:
            spec = json.load(fh)
        lines += ["Mode: **%s**" % spec["mode"], ""]
        if spec["mode"] == "demonstration":
            lines += ["> All results below are labeled "
                      "`typing_quality = nonconfirmatory`.", ""]
    mc_path = os.path.join(study_dir, "model_comparison.json")
    if os.path.exists(mc_path):
        with open(mc_path, encoding="utf-8") as fh:
            mc = json.load(fh)
        synthetic = mc.get("synthetic_mode", False)
        if synthetic:
            lines += ["## SYNTHETIC DEMONSTRATION RESULT — NOT EMPIRICAL",
                      "",
                      "This section was produced from generator-labeled "
                      "synthetic records under a development override. "
                      "It validates the pipeline, not the theory.", ""]
        else:
            lines += ["## Model comparison (held-out, "
                      "participant-level folds)", ""]
        lines += ["| model | held-out MSE (log latency) | SE | n |",
                  "| --- | --- | --- | --- |"]
        for name, r in mc["models"].items():
            lines.append("| %s | %.4f | %.4f | %d |"
                         % (name, r["heldout_mse"], r["heldout_mse_se"],
                            r["n"]))
        c = mc["negative_control_shuffled"]
        lines += ["", "**Negative control** (features shuffled within "
                  "condition): M3 held-out MSE %.4f ± %.4f."
                  % (c["heldout_mse"], c["heldout_mse_se"]),
                  "", "_%s_" % mc["note"], ""]
    lines += ["## Interpretation boundary", "",
              "Statistical results here quantify predictive differences "
              "between nested structural models on this dataset. They are "
              "not, and cannot be, proof of Socionics (SPEC section 63)."]
    out = os.path.join(study_dir, "REPORT.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
