%% Multiscale model state (SPEC section 17).  Separate from the legacy
%% #state{} record — the legacy record is never expanded.
%% Fields have UNEQUAL epistemic status:
%%   tim      locked experimental assignment (not an engine truth claim)
%%   subtype  slower state; unknown | dominant | creative | normalizing |
%%            harmonizing; not required in the first empirical study
%%   profile  estimated field over 8 IEs; unknown until fitted; every
%%            estimate carries uncertainty + parameter-version provenance
%%   current_state  unknown | IE atom | probability map over 8 IEs
%%   reserve  latent; NO physical units; unknown before calibration
-record(model_state, {
    tim,
    subtype = unknown,
    profile = unknown,
    current_state = unknown,
    reserve = unknown,
    model_version = "v2.0",
    parameter_version = unfitted
}).
