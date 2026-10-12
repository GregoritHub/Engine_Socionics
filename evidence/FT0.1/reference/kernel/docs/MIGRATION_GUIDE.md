# Migration guide: v1.1 -> v2

| v1.1 concept | v2 location | change |
| --- | --- | --- |
| hard-coded stacks table | le_stacks:definitive/1 | identical values; now ALSO generated from ego algebra and cross-checked at verify time |
| le_itr relation functions | le_relation_group | relations are now affine group elements computed from frames; v1.1 formulas kept as anchors for benefit/supervision names |
| CAPE / estafette cycle | le_dynamical_group:estafette/0 | replaced by the sourced UMA section 10 permutation (order 4); T^3 claim demoted to legacy |
| #state{} record | #model_state{} (le_dynamic) | new record; legacy record untouched |
| interaction trace (list ++) | le_ledger (append-only file) | O(1) amortized appends; typed event vocabulary |
| phenotype output | le_features:extract/6 | structural variables only, outcome-blind, no costs |
| kappa example | le_state_coding:inter_rater_agreement/2 | bounded agreement in [0,1] |
| OIG tables | le_oig* / pyref/oig.py | reach maps generated from stacks + locked domain pairs; all counts re-derived |

Nothing in `apps/le_legacy/` was edited; run its suite any time with
`python3 bin/le.py verify legacy`.
