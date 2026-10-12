%% le_ledger — append-only event-sourced empirical ledger (SPEC section 57).
%% Wall-clock timestamps live HERE, never inside the deterministic theory
%% kernel.  Events are JSON-ish erlang terms written as lines.
-module(le_ledger).
-export([event_types/0, open/1, append/3, events/1, events/2]).

event_types() ->
    [participant_registered, typing_locked, study_protocol_frozen,
     trial_randomized, prediction_locked, trial_started, response_recorded,
     trial_completed, state_code_submitted, coder_adjudication_recorded,
     dataset_frozen, model_fitted, report_generated].

open(Path) ->
    ok = filelib:ensure_dir(Path),
    case filelib:is_file(Path) of
        true -> ok;
        false -> ok = file:write_file(Path, <<>>)
    end,
    {ledger, Path}.

append({ledger, Path}, EventType, Payload) ->
    case lists:member(EventType, event_types()) of
        false -> erlang:error({unknown_ledger_event_type, EventType});
        true ->
            Rec = #{event => EventType,
                    at => calendar:system_time_to_rfc3339(
                            erlang:system_time(second)),
                    payload => Payload},
            ok = file:write_file(Path,
                                 io_lib:format("~0p.~n", [Rec]),
                                 [append]),
            Rec
    end.

events(L) -> events(L, all).

events({ledger, Path}, Filter) ->
    {ok, Terms} = file:consult(Path),
    [T || T <- Terms,
          Filter =:= all orelse maps:get(event, T) =:= Filter].
