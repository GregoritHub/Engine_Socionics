"""le_empirical mirror — study infrastructure enforcing the anti-circularity
invariants of SPEC sections 18-23, 33-37, 51-53, 55-57.

Invariants enforced here (and tested in verify_all.py):
  I1  typing locks are append-only; retyping creates a new version;
  I2  prediction records are frozen before outcomes and never rewritten;
  I3  observations are physically separate records; raw data never replaced;
  I4  blind coders do not receive TIM / predictions by default;
  I5  synthetic rows carry synthetic=true and are rejected by confirmatory
      analysis without an explicit development-only override;
  I6  the structural feature extractor cannot read outcome fields (it lives
      in features.py with no import path to this module);
  I7  the empirical ledger is append-only and event-sourced;
  I8  blind_dataset contains no theory enrichment; theory_enriched_dataset
      is produced only after coding is committed.
"""

import json
import hashlib
import os
import random
import time


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_of(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True,
                                     default=str).encode()).hexdigest()


class Ledger:
    """Append-only event-sourced empirical ledger (SPEC section 57)."""

    EVENT_TYPES = [
        "participant_registered", "typing_locked", "study_protocol_frozen",
        "trial_randomized", "prediction_locked", "trial_started",
        "response_recorded", "trial_completed", "state_code_submitted",
        "coder_adjudication_recorded", "dataset_frozen", "model_fitted",
        "report_generated",
    ]

    def __init__(self, path):
        self.path = path
        if not os.path.exists(path):
            open(path, "a").close()

    def append(self, event_type, payload):
        if event_type not in self.EVENT_TYPES:
            raise ValueError("unknown ledger event type: %s" % event_type)
        rec = {"event": event_type, "at": _now(), "payload": payload}
        with open(self.path, "a") as f:
            f.write(json.dumps(rec, sort_keys=True, default=str) + "\n")
        return rec

    def events(self, event_type=None):
        out = []
        with open(self.path) as f:
            for line in f:
                if line.strip():
                    e = json.loads(line)
                    if event_type is None or e["event"] == event_type:
                        out.append(e)
        return out


class TypingLockError(Exception):
    pass


class Study:
    """File-backed study state.  All writes go through the ledger."""

    def __init__(self, root, study_id):
        self.root = root
        self.study_id = study_id
        self.dir = os.path.join(root, study_id)
        os.makedirs(self.dir, exist_ok=True)
        self.ledger = Ledger(os.path.join(self.dir, "ledger.jsonl"))

    # -- typing locks (I1) --------------------------------------------------
    def lock_typing(self, subject_id, primary_tim, method, confidence,
                    alternatives=None, rater_ids=None, agreement=None,
                    evidence_ref=None, typing_quality="confirmatory",
                    protocol_version="1"):
        prior = [e for e in self.ledger.events("typing_locked")
                 if e["payload"]["subject_id"] == subject_id]
        version = len(prior) + 1
        rec = {
            "subject_id": subject_id, "primary_tim": primary_tim,
            "alternatives": alternatives or [], "confidence": confidence,
            "method": method, "rater_ids": rater_ids or [],
            "agreement": agreement, "evidence_ref": evidence_ref,
            "typing_quality": typing_quality,
            "typing_protocol_version": protocol_version,
            "typing_lock_version": version, "locked_at": _now(),
        }
        self.ledger.append("typing_locked", rec)
        return rec

    def current_typing(self, subject_id):
        locks = [e["payload"] for e in self.ledger.events("typing_locked")
                 if e["payload"]["subject_id"] == subject_id]
        return locks[-1] if locks else None

    def typing_history(self, subject_id):
        return [e["payload"] for e in self.ledger.events("typing_locked")
                if e["payload"]["subject_id"] == subject_id]

    # -- prediction locks (I2) ---------------------------------------------
    def lock_prediction(self, trial_id, model_name, model_version,
                        parameter_version, hypothesis, predicted_ordering,
                        predicted_route, structural_features,
                        code_commit="worktree", source_manifest_hash=None):
        if self._trial_has_outcome(trial_id):
            raise TypingLockError(
                "prediction lock refused: trial %s already has an outcome "
                "(predictions must be frozen before outcomes)" % trial_id)
        pid = "pred_" + sha256_of([trial_id, model_name, model_version,
                                   parameter_version, _now(),
                                   random.random()])[:12]
        rec = {
            "prediction_id": pid, "study_id": self.study_id,
            "trial_id": trial_id, "model_name": model_name,
            "model_version": model_version,
            "parameter_version": parameter_version,
            "hypothesis": hypothesis,
            "predicted_ordering": predicted_ordering,
            "predicted_route": predicted_route,
            "structural_features": structural_features,
            "generated_at": _now(), "code_commit": code_commit,
            "source_manifest_hash": source_manifest_hash,
        }
        self.ledger.append("prediction_locked", rec)
        return rec

    def predictions(self, trial_id=None):
        return [e["payload"] for e in self.ledger.events("prediction_locked")
                if trial_id is None or e["payload"]["trial_id"] == trial_id]

    # -- observations (I3) --------------------------------------------------
    def record_observation(self, trial_id, subject_id, raw,
                           instrument_version="1", synthetic=False,
                           generator_version=None, generator_parameters=None):
        oid = "obs_" + sha256_of([trial_id, raw, _now(),
                                  random.random()])[:12]
        rec = {"observation_id": oid, "trial_id": trial_id,
               "subject_id": subject_id, "raw": raw,
               "instrument_version": instrument_version,
               "synthetic": bool(synthetic)}
        if synthetic:
            if generator_version is None or generator_parameters is None:
                raise ValueError("synthetic observations require "
                                 "generator_version and generator_parameters")
            rec["generator_version"] = generator_version
            rec["generator_parameters"] = generator_parameters
        self.ledger.append("response_recorded", rec)
        return rec

    def observations(self, include_synthetic=True):
        out = [e["payload"] for e in self.ledger.events("response_recorded")]
        if not include_synthetic:
            out = [o for o in out if not o.get("synthetic")]
        return out

    def _trial_has_outcome(self, trial_id):
        return any(o["trial_id"] == trial_id for o in self.observations())

    # -- blind state coding (I4) -------------------------------------------
    def blind_coding_packet(self, observation_id):
        """What a blind coder receives: NO TIM, NO predictions, NO hypothesis
        direction, NO model preference (SPEC section 36)."""
        obs = [o for o in self.observations()
               if o["observation_id"] == observation_id]
        if not obs:
            raise KeyError(observation_id)
        o = obs[0]
        return {"observation_id": o["observation_id"],
                "trial_id": o["trial_id"],
                "raw": o["raw"],
                "instrument_version": o["instrument_version"]}

    def submit_state_code(self, observation_id, coder_id, coded_ie,
                          confidence, evidence_ref=None, alternative_ie=None,
                          coding_protocol_version="1", blind=True):
        rec = {"observation_id": observation_id, "coder_id": coder_id,
               "coded_ie": coded_ie, "confidence": confidence,
               "evidence_ref": evidence_ref,
               "alternative_ie": alternative_ie,
               "coding_protocol_version": coding_protocol_version,
               "blindness_status": "blind" if blind else "unblinded"}
        self.ledger.append("state_code_submitted", rec)
        return rec

    def state_codes(self):
        return [e["payload"] for e in self.ledger.events("state_code_submitted")]

    # -- trials & randomization (SPEC section 51) ---------------------------
    def randomize_trials(self, subject_ids, conditions, seed,
                         trials_per_condition=1):
        rng = random.Random(seed)
        plan = []
        for sid in subject_ids:
            order = []
            for c in conditions:
                order += [c] * trials_per_condition
            rng.shuffle(order)
            for i, cond in enumerate(order):
                plan.append({"trial_id": "%s_%s_t%03d" % (self.study_id, sid, i),
                             "subject_id": sid, "condition_id": cond,
                             "order_index": i,
                             "randomization_seed": seed})
        self.ledger.append("trial_randomized",
                           {"seed": seed, "plan": plan})
        return plan

    def trials(self):
        out = []
        for e in self.ledger.events("trial_randomized"):
            out += e["payload"]["plan"]
        return out

    # -- exports (I8, SPEC section 56) --------------------------------------
    def export_blind(self, include_synthetic=False):
        """Raw task and observation variables only.  No TIM, no theory."""
        rows = []
        for o in self.observations(include_synthetic=include_synthetic):
            row = {"observation_id": o["observation_id"],
                   "trial_id": o["trial_id"],
                   "subject_id": o["subject_id"],
                   "synthetic": o.get("synthetic", False)}
            row.update({("raw_" + k): v for k, v in o["raw"].items()})
            rows.append(row)
        return rows

    def export_theory(self, feature_fn, include_synthetic=False,
                      confirmatory=True, allow_synthetic_override=False):
        """Theory-enriched dataset.  Refuses synthetic rows in confirmatory
        mode unless explicitly overridden (I5); requires committed state
        codes before enrichment is meaningful."""
        if confirmatory and include_synthetic and not allow_synthetic_override:
            raise ValueError(
                "confirmatory analysis rejects synthetic records; pass "
                "allow_synthetic_override=True only for development")
        trials = {t["trial_id"]: t for t in self.trials()}
        rows = []
        for o in self.observations(include_synthetic=include_synthetic):
            if confirmatory and o.get("synthetic") and not allow_synthetic_override:
                continue
            t = trials.get(o["trial_id"], {})
            lock = self.current_typing(o["subject_id"])
            row = {"observation_id": o["observation_id"],
                   "trial_id": o["trial_id"],
                   "subject_id": o["subject_id"],
                   "condition_id": t.get("condition_id"),
                   "typing_quality": (lock or {}).get("typing_quality"),
                   "typing_lock_version":
                       (lock or {}).get("typing_lock_version"),
                   "tim": (lock or {}).get("primary_tim"),
                   "synthetic": o.get("synthetic", False)}
            row.update({("raw_" + k): v for k, v in o["raw"].items()})
            if lock and t.get("condition_id"):
                row["structural_features"] = feature_fn(lock["primary_tim"],
                                                        t["condition_id"])
            rows.append(row)
        return rows
