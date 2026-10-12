%% le_oig_trace — trajectory observations (SPEC section 30).
%% Instantaneous trace, cumulative V, net N, cancellation K, binary parity P.
%% Trace is NOT class path; non-adjacent recurrence is NOT inferred from
%% adjacent signatures (that is le_oig_recurrence's job).
-module(le_oig_trace).
-export([trace/2, cumulative_v/2, net_n/2, cancellation_k/2, parity_p/2,
         summarize/2]).

trace(TIM, Path) ->
    [le_oig:depth_pair(TIM, C0, C1)
     || {C0, C1} <- lists:zip(lists:droplast(Path), tl(Path))].

cumulative_v(TIM, Path) ->
    lists:foldl(fun le_oig:support_union/2, {none, none}, trace(TIM, Path)).

net_n(TIM, Path) ->
    le_oig:depth_pair(TIM, hd(Path), lists:last(Path)).

cancellation_k(TIM, Path) ->
    le_oig:shell_of(net_n(TIM, Path), cumulative_v(TIM, Path)).

parity_p(TIM, Path) ->
    QPair = {top, paired},
    lists:foldl(fun({C0, C1}, Acc) ->
                        Bits = maps:from_list(le_oig:signature(TIM, C0, C1)),
                        Acc bxor maps:get(QPair, Bits)
                end, 0,
                lists:zip(lists:droplast(Path), tl(Path))).

summarize(TIM, Path) ->
    #{trace => trace(TIM, Path),
      v => cumulative_v(TIM, Path),
      n => net_n(TIM, Path),
      k => cancellation_k(TIM, Path),
      parity => parity_p(TIM, Path),
      temporal_profile => le_oig_recurrence:profile(TIM, Path)}.
