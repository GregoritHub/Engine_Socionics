%% le_export — two separate data products (SPEC section 56).
%% blind_dataset: raw task/observation variables only (no TIM, no theory).
%% theory_enriched_dataset: adds TIM + structural features; confirmatory
%% mode REJECTS synthetic rows unless a development-only override is given
%% (SPEC section 52).
-module(le_export).
-export([blind_dataset/1, theory_dataset/2, theory_dataset/3]).

blind_dataset(Ledger) ->
    [#{observation_id => maps:get(observation_id, O),
       trial_id => maps:get(trial_id, O),
       subject_id => maps:get(subject_id, O),
       synthetic => maps:get(synthetic, O),
       raw => maps:get(raw, O)}
     || O <- le_observation:observations(Ledger)].

theory_dataset(Ledger, Opts) -> theory_dataset(Ledger, Opts, confirmatory).

theory_dataset(Ledger, Opts, Mode) ->
    IncludeSyn = maps:get(include_synthetic, Opts, false),
    Override = maps:get(allow_synthetic_override, Opts, false),
    case {Mode, IncludeSyn, Override} of
        {confirmatory, true, false} ->
            erlang:error({confirmatory_rejects_synthetic,
                          "pass allow_synthetic_override => true only "
                          "for development"});
        _ -> ok
    end,
    Trials = trial_index(Ledger),
    [begin
         Lock = le_participant:current_typing(Ledger,
                                              maps:get(subject_id, O)),
         Cond = maps:get(maps:get(trial_id, O), Trials, undefined),
         Row0 = #{observation_id => maps:get(observation_id, O),
                  trial_id => maps:get(trial_id, O),
                  subject_id => maps:get(subject_id, O),
                  condition_id => Cond,
                  synthetic => maps:get(synthetic, O),
                  raw => maps:get(raw, O),
                  tim => case Lock of undefined -> undefined;
                             _ -> maps:get(primary_tim, Lock) end,
                  typing_quality =>
                      case Lock of undefined -> undefined;
                          _ -> maps:get(typing_quality, Lock) end,
                  typing_lock_version =>
                      case Lock of undefined -> undefined;
                          _ -> maps:get(typing_lock_version, Lock) end},
         case {Lock, Cond} of
             {undefined, _} -> Row0;
             {_, undefined} -> Row0;
             _ ->
                 Row0#{structural_features =>
                           le_features:extract(
                             maps:get(primary_tim, Lock),
                             maps:get(start_probe, Opts, ne),
                             Cond, [], #{}, unfitted)}
         end
     end
     || O <- le_observation:observations(Ledger),
        IncludeSyn orelse not maps:get(synthetic, O)].

trial_index(Ledger) ->
    maps:from_list(
      lists:append(
        [[{maps:get(trial_id, T), maps:get(condition_id, T)}
          || T <- maps:get(plan, maps:get(payload, E))]
         || E <- le_ledger:events(Ledger, trial_randomized)])).
