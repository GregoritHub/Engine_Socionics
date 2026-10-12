#!/usr/bin/env python3
"""le.py — Living Engine v2 CLI (verified Python mirror of bin/le).

This is the executable interface in environments without Erlang/OTP,
following the v1.1 precedent (verify/living_engine_ref.py).  The Erlang
sources under apps/ are the deliverable implementation; this mirror runs
the identical rules and the full acceptance suite.

Commands (SPEC section 61):
  le verify all | legacy | geometry | oig | empirical-separation | holon
  le study create <study.json>
  le study freeze <study_id>
  le participant import <study_id> <participants.csv>
  le trial randomize <study_id>
  le predictions freeze <study_id>
  le observations import <study_id> <observations.jsonl>
  le coding import <study_id> <state_codes.jsonl>
  le export blind <study_id>
  le export theory <study_id> [--include-synthetic --dev-override]
  le analyze <study_id> [--dev-synthetic]
  le report <study_id>
"""

import csv
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from pyref import empirical, features                  # noqa: E402
from pyref.schemas import validate                     # noqa: E402

DATA = os.path.join(HERE, "data")


def _study(study_id):
    return empirical.Study(DATA, study_id)


def cmd_verify(what):
    if what == "legacy":
        ref = os.path.join(HERE, "apps", "le_legacy", "living_engine",
                           "verify", "living_engine_ref.py")
        r = subprocess.run([sys.executable, ref])
        return r.returncode
    if what == "holon":
        from pyref import verify_holon
        return verify_holon.run()
    from pyref import verify_all
    return verify_all.run(None if what == "all" else what)


def cmd_study_create(path):
    spec = json.load(open(path))
    validate("study", spec)
    st = _study(spec["study_id"])
    with open(os.path.join(st.dir, "study.json"), "w") as f:
        json.dump(spec, f, indent=2)
    print("study created:", spec["study_id"], "mode:", spec["mode"])
    return 0


def cmd_study_freeze(study_id):
    st = _study(study_id)
    spec = json.load(open(os.path.join(st.dir, "study.json")))
    h = empirical.sha256_of(spec)
    st.ledger.append("study_protocol_frozen",
                     {"study_id": study_id, "protocol_hash": h})
    print("protocol frozen; hash:", h)
    return 0


def cmd_participant_import(study_id, path):
    st = _study(study_id)
    n = 0
    with open(path) as f:
        for row in csv.DictReader(f):
            st.ledger.append("participant_registered",
                             {"subject_id": row["subject_id"]})
            st.lock_typing(
                row["subject_id"], row["primary_tim"].lower(),
                method=row.get("method", "unspecified"),
                confidence=float(row.get("confidence", 0) or 0),
                alternatives=[a for a in
                              row.get("alternatives", "").split(";") if a],
                rater_ids=[r for r in
                           row.get("rater_ids", "").split(";") if r],
                agreement=(float(row["agreement"])
                           if row.get("agreement") else None),
                typing_quality=row.get("typing_quality", "confirmatory"))
            n += 1
    print("imported %d participants with typing locks" % n)
    return 0


def cmd_trial_randomize(study_id):
    st = _study(study_id)
    spec = json.load(open(os.path.join(st.dir, "study.json")))
    subjects = sorted({e["payload"]["subject_id"]
                       for e in st.ledger.events("participant_registered")})
    plan = st.randomize_trials(subjects, spec["conditions"],
                               seed=spec["randomization_seed"],
                               trials_per_condition=spec.get(
                                   "trials_per_condition", 1))
    print("randomized %d trials (seed %d, stored before outcomes)"
          % (len(plan), spec["randomization_seed"]))
    return 0


def cmd_predictions_freeze(study_id):
    st = _study(study_id)
    spec = json.load(open(os.path.join(st.dir, "study.json")))
    n = 0
    for t in st.trials():
        lock = st.current_typing(t["subject_id"])
        if lock is None:
            continue
        tim = lock["primary_tim"]
        cond = spec["condition_definitions"][t["condition_id"]]
        feats = features.extract(
            tim, cond["start_probe"], cond["designed_target_ie"],
            intermediates=cond.get("intermediates", []))
        st.lock_prediction(
            t["trial_id"], model_name="m3_routing",
            model_version="v2.0", parameter_version="unfitted",
            hypothesis=spec.get("primary_hypothesis", "H1"),
            predicted_ordering=spec.get("predicted_ordering", []),
            predicted_route=[cond["start_probe"]]
            + cond.get("intermediates", [])
            + [cond["designed_target_ie"]],
            structural_features=_json_safe(feats))
        n += 1
    print("froze %d predictions (append-only; pre-outcome)" % n)
    return 0


def cmd_observations_import(study_id, path):
    st = _study(study_id)
    n = 0
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            validate("observation", rec)
            st.record_observation(
                rec["trial_id"], rec["subject_id"], rec["raw"],
                instrument_version=rec.get("instrument_version", "1"),
                synthetic=rec.get("synthetic", False),
                generator_version=rec.get("generator_version"),
                generator_parameters=rec.get("generator_parameters"))
            n += 1
    print("imported %d observations" % n)
    return 0


def cmd_coding_import(study_id, path):
    st = _study(study_id)
    n = 0
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            validate("state_code", rec)
            st.submit_state_code(
                rec["observation_id"], rec["coder_id"], rec["coded_ie"],
                rec["confidence"],
                evidence_ref=rec.get("evidence_ref"),
                alternative_ie=rec.get("alternative_ie"),
                blind=rec.get("blind", True))
            n += 1
    print("imported %d state codes" % n)
    return 0


def cmd_export(kind, study_id, argv):
    st = _study(study_id)
    if kind == "blind":
        rows = st.export_blind(include_synthetic=True)
        out = os.path.join(st.dir, "blind_dataset.jsonl")
    else:
        inc = "--include-synthetic" in argv
        dev = "--dev-override" in argv
        spec = json.load(open(os.path.join(st.dir, "study.json")))

        def feature_fn(tim, cond_id):
            c = spec["condition_definitions"][cond_id]
            return _json_safe(features.extract(
                tim, c["start_probe"], c["designed_target_ie"],
                intermediates=c.get("intermediates", [])))

        try:
            rows = st.export_theory(feature_fn, include_synthetic=inc,
                                    confirmatory=True,
                                    allow_synthetic_override=dev)
        except ValueError as e:
            print("REFUSED:", e)
            return 1
        out = os.path.join(st.dir, "theory_enriched_dataset.jsonl")
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(_json_safe(r), sort_keys=True) + "\n")
    st.ledger.append("dataset_frozen",
                     {"kind": kind, "rows": len(rows),
                      "hash": empirical.sha256_of(rows)})
    print("wrote %d rows -> %s" % (len(rows), out))
    return 0


def cmd_analyze(study_id, argv):
    dev = "--dev-synthetic" in argv
    script = os.path.join(HERE, "analysis", "fit_models.py")
    args = [sys.executable, script, os.path.join(DATA, study_id)]
    if dev:
        args.append("--dev-synthetic")
    return subprocess.run(args).returncode


def cmd_report(study_id):
    script = os.path.join(HERE, "analysis", "reports.py")
    return subprocess.run([sys.executable, script,
                           os.path.join(DATA, study_id)]).returncode


def _json_safe(obj):
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, (frozenset, set)):
        return sorted(_json_safe(v) for v in obj)
    return obj


def main(argv):
    if argv and argv[0] == "holon" and (len(argv) == 1 or argv[1] == "run"):
        import json
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "holon_run", os.path.join(os.path.dirname(os.path.abspath(__file__)), "holon_run.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        directory = argv[2] if len(argv) >= 3 else os.path.join(HERE, "configs")
        print(json.dumps(mod.run(directory), indent=2, sort_keys=True, default=str))
        return 0
    if len(argv) >= 2 and argv[0] == "verify":
        return cmd_verify(argv[1])
    if len(argv) >= 3 and argv[0] == "study" and argv[1] == "create":
        return cmd_study_create(argv[2])
    if len(argv) >= 3 and argv[0] == "study" and argv[1] == "freeze":
        return cmd_study_freeze(argv[2])
    if len(argv) >= 4 and argv[0] == "participant" and argv[1] == "import":
        return cmd_participant_import(argv[2], argv[3])
    if len(argv) >= 3 and argv[0] == "trial" and argv[1] == "randomize":
        return cmd_trial_randomize(argv[2])
    if len(argv) >= 3 and argv[0] == "predictions" and argv[1] == "freeze":
        return cmd_predictions_freeze(argv[2])
    if len(argv) >= 4 and argv[0] == "observations" and argv[1] == "import":
        return cmd_observations_import(argv[2], argv[3])
    if len(argv) >= 4 and argv[0] == "coding" and argv[1] == "import":
        return cmd_coding_import(argv[2], argv[3])
    if len(argv) >= 3 and argv[0] == "export":
        return cmd_export(argv[1], argv[2], argv[3:])
    if len(argv) >= 2 and argv[0] == "analyze":
        return cmd_analyze(argv[1], argv[2:])
    if len(argv) >= 2 and argv[0] == "report":
        return cmd_report(argv[1])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
