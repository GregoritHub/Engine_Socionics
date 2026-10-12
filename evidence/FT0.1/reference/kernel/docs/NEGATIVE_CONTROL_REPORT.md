# Negative control report

Software-level controls (all enforced by `le verify all`):

1. **Contrary indistinguishability (H6 gate).** Under the locked OIG lens, contrary partners have identical fingerprints for all 8 pairs; an OIG-only classifier that separates them is wrong by construction.
2. **TIM-specific vs generic distance.** Routing distance differs from generic IE Hamming distance for every TIM somewhere, so M3 cannot be a relabeled generic-distance model.
3. **Label sensitivity.** Changing the TIM label changes the feature vector (shuffled-label analyses are meaningful).

Data-level control in the demonstration analysis: features shuffled within condition degrade M3 held-out error (0.0324 vs 0.0305 intact).
