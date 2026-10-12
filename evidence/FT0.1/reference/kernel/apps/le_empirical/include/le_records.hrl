%% Empirical records (SPEC sections 18, 33-35).
%% typing_lock is immutable: retyping creates a NEW version; history is
%% never rewritten.
-record(typing_lock, {
    subject_id,
    primary_tim,
    alternatives = [],
    confidence,
    method,
    rater_ids = [],
    agreement,
    evidence_ref,
    typing_quality = confirmatory,   %% confirmatory|exploratory|nonconfirmatory
    locked_at,
    typing_lock_version = 1,
    typing_protocol_version
}).

-record(trial_spec, {
    study_id, trial_id, subject_id, session_id, condition_id,
    typing_lock_version,
    start_probe, designed_target_ie, intermediate_probe = none,
    environment,          %% versioned experimental context `e` (SPEC 22)
    control,              %% deliberate control `u` (SPEC 23)
    structural_features,
    prediction_id, randomization_seed, protocol_version
}).

-record(prediction, {
    prediction_id, study_id, trial_id,
    model_name, model_version, parameter_version,
    hypothesis, predicted_ordering, predicted_route, structural_features,
    generated_at, code_commit, source_manifest_hash
}).

-record(observation, {
    observation_id, trial_id, subject_id,
    started_at, ended_at,
    latency_ms, accuracy, response, error_code, timeout,
    self_report = #{}, behavioral_metrics = #{}, physiology = none,
    blind_state_codes = [], instrument_version,
    synthetic = false, generator_version, generator_parameters
}).

-record(state_code, {
    observation_id, coder_id, coded_ie, confidence,
    evidence_ref, alternative_ie, coding_protocol_version,
    blindness_status = blind
}).
