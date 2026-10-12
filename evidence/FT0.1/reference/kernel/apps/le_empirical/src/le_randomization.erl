%% le_randomization — reproducible randomization (SPEC section 51).
%% Deterministic from a stored seed; the plan is written to the ledger
%% BEFORE outcomes.
-module(le_randomization).
-export([randomize/5]).

randomize(Ledger, StudyId, SubjectIds, Conditions, Seed) ->
    rand:seed(exsss, {Seed, Seed * 7 + 1, Seed * 131 + 17}),
    Plan =
        lists:append(
          [begin
               Order = shuffle(Conditions),
               [#{trial_id =>
                      lists:flatten(io_lib:format("~s_~s_t~3..0B",
                                                  [StudyId, Sid, I])),
                  subject_id => Sid,
                  condition_id => lists:nth(I + 1, Order),
                  order_index => I,
                  randomization_seed => Seed}
                || I <- lists:seq(0, length(Order) - 1)]
           end || Sid <- SubjectIds]),
    le_ledger:append(Ledger, trial_randomized,
                     #{seed => Seed, plan => Plan}),
    Plan.

shuffle(L) ->
    [X || {_, X} <- lists:sort([{rand:uniform(), X} || X <- L])].
