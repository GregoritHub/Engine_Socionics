%% le_observation — raw observation records (SPEC section 35).
%% Physically separate from trial specs and predictions; raw data preserved;
%% derived scores stored separately; synthetic rows must carry generator
%% metadata (SPEC section 52).
-module(le_observation).
-export([record/4, observations/1, observations/2]).

record(Ledger, TrialId, SubjectId, Raw) ->
    Synthetic = maps:get(synthetic, Raw, false),
    case Synthetic of
        true ->
            case {maps:is_key(generator_version, Raw),
                  maps:is_key(generator_parameters, Raw)} of
                {true, true} -> ok;
                _ -> erlang:error(synthetic_requires_generator_metadata)
            end;
        false -> ok
    end,
    Rec = #{observation_id =>
                erlang:unique_integer([positive, monotonic]),
            trial_id => TrialId, subject_id => SubjectId,
            raw => maps:remove(synthetic, Raw),
            synthetic => Synthetic},
    le_ledger:append(Ledger, response_recorded, Rec),
    Rec.

observations(Ledger) -> observations(Ledger, include_synthetic).

observations(Ledger, include_synthetic) ->
    [maps:get(payload, E)
     || E <- le_ledger:events(Ledger, response_recorded)];
observations(Ledger, exclude_synthetic) ->
    [O || O <- observations(Ledger), not maps:get(synthetic, O)].
