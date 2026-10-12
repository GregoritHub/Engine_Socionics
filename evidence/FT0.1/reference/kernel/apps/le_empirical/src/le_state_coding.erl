%% le_state_coding — blind state coding (SPEC section 36).
%% Coders do NOT automatically receive TIM, predicted route/state, model
%% preference or hypothesis direction.  Multiple independent coders;
%% inter-rater agreement computed; disagreement is NEVER adjudicated by
%% picking whichever code matches the theoretical prediction.
-module(le_state_coding).
-export([blind_packet/2, submit/3, codes/1, inter_rater_agreement/2]).

blind_packet(Ledger, ObservationId) ->
    [O] = [X || X <- le_observation:observations(Ledger),
                maps:get(observation_id, X) =:= ObservationId],
    #{observation_id => ObservationId,
      trial_id => maps:get(trial_id, O),
      raw => maps:get(raw, O)}.
    %% deliberately absent: subject TIM, predictions, hypotheses

submit(Ledger, ObservationId, Code) ->
    Rec = Code#{observation_id => ObservationId,
                blindness_status => maps:get(blindness_status, Code, blind)},
    le_ledger:append(Ledger, state_code_submitted, Rec),
    Rec.

codes(Ledger) ->
    [maps:get(payload, E)
     || E <- le_ledger:events(Ledger, state_code_submitted)].

inter_rater_agreement(Ledger, ObservationId) ->
    Cs = [maps:get(coded_ie, C) || C <- codes(Ledger),
          maps:get(observation_id, C) =:= ObservationId],
    case Cs of
        [] -> undefined;
        _ ->
            Pairs = [{A, B} || A <- Cs, B <- Cs, A =< B, A =/= B],
            case length(Cs) < 2 of
                true -> single_coder;
                false ->
                    Agree = length([1 || {A, B} <- Pairs, A =:= B]),
                    Agree / max(1, length(Pairs))
            end
    end.
