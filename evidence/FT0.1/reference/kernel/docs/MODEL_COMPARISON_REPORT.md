# Model comparison report (demonstration)

**SYNTHETIC DEMONSTRATION — NOT EMPIRICAL.** Produced from generator-labeled synthetic records under the development override, to prove the pipeline end to end.

| model | held-out MSE (log latency, within-subject) | SE |
| --- | --- | --- |
| m0_null | 0.0425 | 0.0054 |
| m2_model_a | 0.0425 | 0.0054 |
| m3_routing | 0.0305 | 0.0039 |
| m4_model_g | 0.0290 | 0.0039 |

Interpretation of the demonstration: M0 = M2 exactly (single-target design makes target-position features subject-constant; the within-subject estimator removes them, which is correct); M3/M4 improve held-out prediction because the *generator* plants a routing-distance effect. On real data no such outcome is guaranteed.

Negative control (features shuffled within condition): M3 MSE 0.0324 ± 0.0039 — degraded relative to intact features, as required.
