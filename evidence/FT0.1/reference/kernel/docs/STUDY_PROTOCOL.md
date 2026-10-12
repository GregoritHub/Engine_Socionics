# Empirical protocol (first transition study; SPEC sections 33-44, 51-56)

## Roles and blinding
- Typist(s): assign TIM before any trial; two independent raters minimum;
  agreement recorded; result frozen as typing_lock v1.
- Experimenter: runs sessions; never adjudicates codes.
- Coders (>= 2): receive blind packets (no TIM, no predictions, no
  hypothesis direction); disagreement resolved by pre-registered rule
  (consensus discussion or third coder), NEVER by matching theory.
- Analyst: touches theory-enriched exports only after predictions freeze.

## Order of operations (enforced by the software)
1. `study create` + `study freeze` (protocol hash to ledger)
2. `participant import` (typing locks, versioned)
3. `trial randomize` (seeded; plan on ledger pre-outcome)
4. `predictions freeze` (refused for any trial with an outcome)
5. run sessions; `observations import`
6. `coding import` (blind packets only)
7. `export blind` / `export theory`; `analyze`; `report`

## Conditions (per SPEC section 39)
direct vs predicted-intermediate vs control-intermediate transitions with
identical start probe and designed target; only the induced route differs.
Intermediates are chosen from the participant's own routing cube
(predicted = on a shortest route; control = matched length, off route).

## Typing quality gates
`confirmatory` requires the pre-registered typing protocol with >= 2
raters and agreement >= the pre-registered threshold; anything less is
`exploratory` or `nonconfirmatory` and is excluded from confirmatory
analysis. Retyping after data collection appends a new lock version and
demotes affected trials to exploratory.

## Analysis
Primary outcome: log latency (correct trials). Within-subject
(fixed-effects) estimator with leave-one-participant-out holdout.
Nested model ladder M0-M4; report held-out error with uncertainty;
negative controls (shuffled features; contrary-pair indistinguishability
for OIG-lens claims). Significance is never proof of Socionics.
