# Empirical readiness report

Machine-generated. Demonstrates the anti-circularity machinery: prediction locks refuse post-outcome creation; typing locks version instead of rewriting; blind packets carry no TIM or prediction; confirmatory exports refuse synthetic rows; the feature extractor is outcome-blind and cost-free; unfitted models answer `unknown` rather than inventing numbers.

```
PASS  emp.prediction_lock_refused_after_outcome
PASS  emp.prediction_append_only
PASS  emp.retyping_creates_new_version
PASS  emp.blind_packet_has_no_tim_or_prediction
PASS  emp.confirmatory_excludes_synthetic
PASS  emp.synthetic_override_required
PASS  emp.synthetic_requires_generator_metadata
PASS  emp.blind_dataset_theory_free
PASS  emp.randomization_reproducible_from_seed
PASS  emp.ledger_rejects_unknown_event_types
PASS  emp.feature_extractor_deterministic_outcome_blind
PASS  emp.no_hard_coded_costs_in_features
PASS  emp.structural_only_model_refuses_probabilities
PASS  emp.unfitted_reserve_returns_unknown
PASS  emp.model_state_defaults_unknown_unfitted
PASS  negctl.h6_oig_cannot_distinguish_contrary
PASS  negctl.tim_distance_differs_from_generic_distance
PASS  negctl.shuffled_tim_changes_features
```
