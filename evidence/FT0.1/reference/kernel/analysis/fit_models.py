#!/usr/bin/env python3
"""fit_models.py — nested model comparison on an exported study dataset.

LADDER GAP -- read before interpreting any result from this script.

SPEC section 42 defines a six-model ladder, and the kernel carries it in
full: see `pyref.features.model_feature_sets()`, which declares m0_null,
m1_jungian, m2_model_a, m3_routing, m4_model_g, m5_full_dynamic.

This script fits FOUR of the six. Two are silently absent:

  m1_jungian     declared, but `pyref.features.extract()` never emits its
                 four columns (jungian_e/n/t/p), so it cannot be fitted
                 from an exported dataset as things stand.
  m5_full_dynamic  its columns exist but are all `unknown` until the
                 reserve model is fitted, which is correct behaviour, not
                 a defect.

M1 is the one that matters. It is the JUNGIAN BASELINE -- plain E/N/T/P
dichotomies -- and it is therefore the control that answers the sharpest
skeptical question anyone will ask of these results: is the structural
signal just Jungian dichotomies wearing Model A notation? Without M1 in
the ladder, the reported M0 < M2 < M3 < M4 comparison never asks it.

The coordinates exist: `pyref.core.jungian_coord(tim)` returns
(E, N, T, P) and is `derived`, not guessed. The kernel is SHA-256 sealed,
so the fix cannot go in `pyref/`; the four columns have to be produced in
a non-frozen layer and joined into the exported rows before M1 can be
fitted. Until that lands, treat every comparison below as conditional on
a control that has not been run.

Reads <study_dir>/theory_enriched_dataset.jsonl and compares the nested
model ladder of SPEC section 42 on a primary outcome (log latency) with:
  * participant intercepts (repeated-measures treatment, SPEC section 44);
  * leave-one-participant-out holdout (SPEC section 43);
  * confirmatory synthetic-row rejection (SPEC section 52) unless
    --dev-synthetic is passed;
  * a shuffled-TIM negative control (SPEC section 55).

Statistical significance is never converted into proof of Socionics
(SPEC section 63): output reports held-out error with uncertainty.
"""
import collections
import json
import os
import sys

import numpy as np


def load_rows(study_dir, dev_synthetic=False):
    path = os.path.join(study_dir, "theory_enriched_dataset.jsonl")
    if not os.path.exists(path):
        sys.exit("no theory_enriched_dataset.jsonl — run `le export theory` first")
    with open(path, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    syn = [r for r in rows if r.get("synthetic")]
    if syn and not dev_synthetic:
        sys.exit("confirmatory analysis rejects %d synthetic rows; "
                 "pass --dev-synthetic for development only" % len(syn))
    if syn:
        print("WARNING: DEVELOPMENT MODE — %d SYNTHETIC rows included; "
              "results are NOT empirical" % len(syn))
    return [r for r in rows if "structural_features" in r
            and r.get("raw_latency_ms") is not None]


MODEL_COLUMNS = {
    "m0_null": [],
    "m2_model_a": ["target_native_dimensionality", "target_valued_num",
                   "target_mental_num"],
    "m3_routing": ["target_native_dimensionality", "target_valued_num",
                   "target_mental_num",
                   "primitive_routing_distance", "direct_route_num",
                   "chosen_path_excess"],
    "m4_model_g": ["target_native_dimensionality", "target_valued_num",
                   "target_mental_num",
                   "primitive_routing_distance", "direct_route_num",
                   "chosen_path_excess",
                   "route_uses_g_chord_num", "g_braking", "g_manipulative"],
}


def featurize(r):
    f = r["structural_features"]
    role = f.get("target_model_g_role")
    return {
        "target_native_dimensionality": f["target_native_dimensionality"],
        "target_valued_num": 1.0 if f["target_valued"] else 0.0,
        "target_mental_num": 1.0 if f["target_mental_vital"] == "mental" else 0.0,
        "primitive_routing_distance": f["primitive_routing_distance"],
        "direct_route_num": 1.0 if f["direct_route"] else 0.0,
        "chosen_path_excess": f["chosen_path_excess"],
        "route_uses_g_chord_num": 1.0 if f["route_uses_g_chord"] else 0.0,
        "g_braking": 1.0 if role == "braking" else 0.0,
        "g_manipulative": 1.0 if role == "manipulative" else 0.0,
    }


def demean_within_subject(rows, cols):
    """Fixed-effects (within) transform: demean outcome and features within
    each subject.  Subject-constant features (e.g. per-TIM constants in a
    single-target study) vanish, which is exactly the repeated-measures
    treatment of SPEC section 44: inference is about within-subject
    condition effects, never between-subject TIM main effects confounded
    with the person."""
    by_s = collections.defaultdict(list)
    for r in rows:
        by_s[r["subject_id"]].append(r)
    out = []
    for sid, rs in by_s.items():
        ys = np.log(np.array([float(r["raw_latency_ms"]) for r in rs]))
        Fs = np.array([[float(featurize(r)[c]) for c in cols] for r in rs]) \
            if cols else np.zeros((len(rs), 0))
        ybar = ys.mean()
        fbar = Fs.mean(axis=0) if cols else np.zeros(0)
        for r, y, f in zip(rs, ys, Fs):
            out.append({"subject_id": sid, "y_w": y - ybar,
                        "x_w": f - fbar})
    return out


def lopo_cv(rows, cols):
    """Leave-one-participant-out CV on the within-subject transform.
    The null (no columns) predicts each subject's own mean, i.e. y_w = 0.
    Slopes are estimated from training subjects only."""
    subjects = sorted({r["subject_id"] for r in rows})
    w = demean_within_subject(rows, cols)
    errs = []
    for held in subjects:
        tr = [d for d in w if d["subject_id"] != held]
        te = [d for d in w if d["subject_id"] == held]
        if cols:
            Xtr = np.array([d["x_w"] for d in tr])
            ytr = np.array([d["y_w"] for d in tr])
            beta, *_ = np.linalg.lstsq(Xtr, ytr, rcond=None)
        else:
            beta = np.zeros(0)
        for d in te:
            pred = float(np.dot(beta, d["x_w"])) if cols else 0.0
            errs.append((d["y_w"] - pred) ** 2)
    errs = np.array(errs)
    n = len(errs)
    mse = float(errs.mean())
    se = float(errs.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    sigma2 = max(mse, 1e-9)
    heldout_loglik = float(-0.5 * n * (np.log(2 * np.pi * sigma2) + 1))
    return {"heldout_mse": mse, "heldout_mse_se": se, "n": n,
            "heldout_gaussian_loglik": heldout_loglik}


def shuffled_tim_control(rows, cols, seed=1234):
    """Negative control: break the TIM-specific signal and refit.

    Permuting TIM labels and recomputing features would be the obvious
    control, but features are frozen pre-outcome, so recomputing them here
    would reach back across the prediction lock. The honest permutation is
    therefore over the frozen feature vectors themselves: shuffle them
    across subjects WITHIN condition, which destroys the TIM-specific
    structure while leaving the condition design intact.

    A model that scores as well on shuffled features as on intact ones is
    not reading structure; it is reading the condition.
    """
    rng = np.random.default_rng(seed)
    by_cond = {}
    for r in rows:
        by_cond.setdefault(r["condition_id"], []).append(r)
    shuffled = []
    for cond, rs in by_cond.items():
        feats = [r["structural_features"] for r in rs]
        perm = rng.permutation(len(feats))
        for r, j in zip(rs, perm):
            r2 = dict(r)
            r2["structural_features"] = feats[j]
            shuffled.append(r2)
    return lopo_cv(shuffled, cols)


USAGE = "usage: fit_models.py <study_dir> [--dev-synthetic]"


def main():
    """Fit the ladder, run the negative control, write model_comparison.json."""
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(USAGE)
    study_dir = args[0]
    dev = "--dev-synthetic" in sys.argv
    rows = load_rows(study_dir, dev)
    if len({r["subject_id"] for r in rows}) < 2:
        sys.exit("need >= 2 participants for participant-level holdout")
    print("rows: %d  participants: %d  conditions: %s"
          % (len(rows), len({r["subject_id"] for r in rows}),
             sorted({r["condition_id"] for r in rows})))
    results = {}
    for name, cols in MODEL_COLUMNS.items():
        results[name] = lopo_cv(rows, cols)
        r = results[name]
        print("%-12s held-out MSE(log latency) = %.4f +- %.4f  "
              "(gauss loglik %.1f, n=%d)"
              % (name, r["heldout_mse"], r["heldout_mse_se"],
                 r["heldout_gaussian_loglik"], r["n"]))
    ctl = shuffled_tim_control(rows, MODEL_COLUMNS["m3_routing"])
    print("negative control (shuffled features within condition): "
          "M3 held-out MSE = %.4f +- %.4f"
          % (ctl["heldout_mse"], ctl["heldout_mse_se"]))
    out = {"models": results, "negative_control_shuffled": ctl,
           "synthetic_mode": dev,
           "note": ("SYNTHETIC/DEVELOPMENT RESULT — NOT EMPIRICAL" if dev
                    else "empirical-candidate result; interpret with "
                         "uncertainty; not proof of Socionics")}
    with open(os.path.join(study_dir, "model_comparison.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("wrote model_comparison.json")


if __name__ == "__main__":
    main()
