# Data dictionary

## Ledger events (le_ledger / pyref Ledger)
participant_registered, typing_locked, study_protocol_frozen,
trial_randomized, prediction_locked, trial_started, response_recorded,
trial_completed, state_code_submitted, coder_adjudication_recorded,
dataset_frozen, model_fitted, report_generated.
Append-only JSONL; wall-clock timestamps live only here.

## typing_lock
subject_id, primary_tim, alternatives[], confidence [0,1], method,
rater_ids[], agreement [0,1], evidence_ref, typing_quality
(confirmatory|exploratory|nonconfirmatory), typing_lock_version (>=1),
typing_protocol_version.

## trial
trial_id, subject_id, condition_id, order_index, randomization_seed.
Condition definitions live in study.json: start_probe, designed_target_ie,
intermediates[].

## prediction (locked pre-outcome)
prediction_id, trial_id, model_name, model_version, parameter_version,
hypothesis, predicted_ordering[], predicted_route[], structural_features.

## observation
observation_id, trial_id, subject_id, raw{latency_ms, accuracy, timeout,
...}, instrument_version, synthetic (bool), generator_version,
generator_parameters (required when synthetic).

## state_code
observation_id, coder_id, coded_ie, confidence, evidence_ref,
alternative_ie, blindness_status.

## exports
blind_dataset.jsonl: observation ids + raw_* fields + synthetic flag.
theory_enriched_dataset.jsonl: adds tim, typing_quality,
typing_lock_version, condition_id, structural_features (see
le_features/pyref features for the full variable list).

## structural feature variables (outcome-blind; no costs)
start_*/target_*: model_a_position, position_name, native_dimensionality,
valued, mental_vital, accepting_producing, strong_weak, bold_cautious,
contact_family, model_g_position, model_g_role, model_g_vars.
Route: primitive_routing_distance, generic_ie_distance,
shortest_path_count, chosen_path_length, chosen_path_excess,
primitive_direction_sequence, all_steps_primitive, route_uses_g_chord,
direct_route, intermediate_states, practice_count_*.
Unfitted placeholders are the atom/string "unknown", never a number.
