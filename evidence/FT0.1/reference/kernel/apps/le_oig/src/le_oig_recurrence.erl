%% le_oig_recurrence — temporal equality profile R (SPEC section 30).
%% For every quotient Q: i ~_Q j iff [c_i]_Q = [c_j]_Q; the induced time
%% partition R_Q.  Captures non-adjacent recurrence WITHOUT class names.
-module(le_oig_recurrence).
-export([profile/2, partition/3]).

partition(TIM, Path, Q) ->
    Indexed = lists:zip(lists:seq(0, length(Path) - 1), Path),
    Groups = lists:foldl(
               fun({I, C}, Acc) ->
                       Cls = le_oig:q_class(TIM, C, Q),
                       maps:update_with(Cls, fun(L) -> [I | L] end,
                                        [I], Acc)
               end, #{}, Indexed),
    lists:sort([lists:sort(Is) || Is <- maps:values(Groups)]).

profile(TIM, Path) ->
    [{Q, partition(TIM, Path, Q)} || Q <- le_oig:quotients()].
