# Legacy v1.1 — verified findings and dispositions (SPEC section 4)

The complete v1.1 tree is preserved unchanged under
`apps/le_legacy/living_engine/`; its own acceptance suite
(`verify/living_engine_ref.py`, 10 checks) still passes and is executed
by `le verify legacy` and inside `le verify all`.

Dispositions required by the build spec:

1. **T^3 "return to start" demoted.**  v1.1's README claim that the
   estafette cycle returns after three steps is not supported by the
   supplied sources.  The sourced estafette (UMA section 10,
   R(a,v,r) = (r, v, 1+a)) has order 4.  v2 exposes only the sourced
   R and R^2 = Activation; any T^3 statement survives solely inside the
   frozen legacy tree and is labeled `legacy`.
2. **README kappa example corrected in v2 docs.**  v1.1's README shows a
   worked kappa of 1.7; agreement statistics are bounded above by 1.
   The frozen file is not edited; docs here record that the value is
   arithmetically impossible and v2's `inter_rater_agreement` is bounded.
3. **Trace O(n) append.**  v1.1 appends to the interaction trace with
   `++` per event (quadratic).  Frozen code untouched; the v2 runtime
   (`le_ledger`) appends to file in O(1) amortized per event.
4. **`content_replacement` naming.**  The legacy event name conflated
   replacement with augmentation.  The v2 ledger names events by what
   happened (`response_recorded`, `state_code_submitted`, ...) and never
   reuses the ambiguous legacy name.
5. **Phenotype isolation.**  Legacy "phenotype" outputs mixed structural
   derivation with interpretation.  v2's feature extractor emits only
   structural variables; all interpretation lives in analysis reports.
6. **Legacy record non-expansion.**  The v1.1 `#state{}` record is not
   extended; the multiscale v2 state is a new `#model_state{}` record.
7. **Benefit/supervision derivations kept.**  v1.1's `le_itr` ego-algebra
   formulas are retained as the source anchor for naming the order-4
   Benefit and Supervision elements of the derived relation group; v2
   verifies that each is a *single* group element consistent across all
   16 TIMs.
