%% le_prediction_lock — immutable pre-outcome predictions (SPEC section 34).
%% A prediction for a trial is REFUSED if the trial already has an outcome;
%% after creation records are append-only and never overwritten.
-module(le_prediction_lock).
-export([freeze/3, predictions/2]).

freeze(Ledger, TrialId, Spec) ->
    HasOutcome =
        lists:any(fun(E) ->
                          maps:get(trial_id, maps:get(payload, E)) =:= TrialId
                  end, le_ledger:events(Ledger, response_recorded)),
    case HasOutcome of
        true ->
            erlang:error({prediction_lock_refused_outcome_exists, TrialId});
        false ->
            Rec = Spec#{trial_id => TrialId,
                        prediction_id =>
                            erlang:unique_integer([positive, monotonic])},
            le_ledger:append(Ledger, prediction_locked, Rec),
            Rec
    end.

predictions(Ledger, TrialId) ->
    [maps:get(payload, E)
     || E <- le_ledger:events(Ledger, prediction_locked),
        TrialId =:= all orelse
            maps:get(trial_id, maps:get(payload, E)) =:= TrialId].
