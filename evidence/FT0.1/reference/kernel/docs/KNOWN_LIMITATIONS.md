# Known limitations

1. **Erlang not compiled in the build environment.**  This build machine
   has no Erlang/OTP or rebar3 and no network access.  The Erlang
   sources under apps/ are complete and are the deliverable
   implementation, but they were not compiled or executed here.  All
   behavior was verified through the 1:1 Python mirror (pyref/), which
   runs the entire 117-check acceptance suite plus the frozen v1.1 suite
   (the same verification precedent v1.1 itself used).  The V3–V5
   Python packages (`crux/`, `demand/`, `holon_tower/`, `algebra/`,
   `metabolism/`) have no Erlang mirror yet (unresolved item 8).  On an
   Erlang machine run: `rebar3 compile && bin/le verify all && rebar3 eunit`.
   Until that is done, treat the Erlang layer as source-verified-by-
   mirror, not machine-executed.
2. **No statsmodels/jsonschema in-environment.**  Model fitting uses a
   within-subject fixed-effects estimator in numpy (documented in
   analysis/fit_models.py); schemas use a small built-in validator whose
   JSON exports are in schemas/.
3. **Single-target demonstration study.**  pilot_001 uses one designed
   target (Ti), so target-position features are subject-constant and
   correctly demean away; a real study should cross targets within
   subject to identify M2-level effects.
4. **Task->IE validity is a hypothesis.**  The task registry ships with
   validation_status pilot_unvalidated everywhere; convergent/
   discriminant validation (SPEC section 41) has not been run.
5. **Exact-meet theorem (OIG 7.3)** is carried at the source's own
   status: canonical witness not exhibited; not independently discharged
   here (OIG D.7).
6. **Unfitted numerical models.**  Transition probabilities, reserve and
   profile dynamics are structurally specified but refuse numeric output
   until parameters are estimated from real observations.
