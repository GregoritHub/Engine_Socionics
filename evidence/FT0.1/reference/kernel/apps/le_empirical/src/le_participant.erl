%% le_participant — subject identity separated from model state
%% (SPEC sections 18-19).  Typing locks are versioned and append-only:
%% experimental outcomes NEVER silently rewrite a pre-experimental TIM
%% assignment; retyping appends a new version.
-module(le_participant).
-include("le_records.hrl").
-export([lock_typing/3, current_typing/2, typing_history/2]).

lock_typing(Ledger, SubjectId, Spec) ->
    Quality = maps:get(typing_quality, Spec, confirmatory),
    true = lists:member(Quality,
                        [confirmatory, exploratory, nonconfirmatory]),
    Prior = typing_history(Ledger, SubjectId),
    Version = length(Prior) + 1,
    Rec = #{subject_id => SubjectId,
            primary_tim => maps:get(primary_tim, Spec),
            alternatives => maps:get(alternatives, Spec, []),
            confidence => maps:get(confidence, Spec),
            method => maps:get(method, Spec),
            rater_ids => maps:get(rater_ids, Spec, []),
            agreement => maps:get(agreement, Spec, undefined),
            evidence_ref => maps:get(evidence_ref, Spec, undefined),
            typing_quality => Quality,
            typing_protocol_version =>
                maps:get(typing_protocol_version, Spec, <<"1">>),
            typing_lock_version => Version},
    le_ledger:append(Ledger, typing_locked, Rec),
    Rec.

typing_history(Ledger, SubjectId) ->
    [maps:get(payload, E)
     || E <- le_ledger:events(Ledger, typing_locked),
        maps:get(subject_id, maps:get(payload, E)) =:= SubjectId].

current_typing(Ledger, SubjectId) ->
    case typing_history(Ledger, SubjectId) of
        [] -> undefined;
        H -> lists:last(H)
    end.
