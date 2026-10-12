%% le_oig_domain — OIG domain quotient chain (SPEC sections 26-27).
%% Status: domain labels/pairs source_defined (OIG C.4 = V11 verbatim);
%% reach map GENERATED from TIM stack + locked domain pairs (never 16
%% hand-written tables); chain dom -> access -> route -> top with class
%% counts 16 -> 10 -> 4 -> 1.
-module(le_oig_domain).
-export([domains/0, class_pair/1, reach/2, reach_map/1, subsets/0,
         delta_access/2, delta_route/2, class_counts/1, capacity_tree/1,
         fingerprint/1]).

domains() -> [its, i, we, it].

class_pair(n) -> [its, i];
class_pair(s) -> [we, it];
class_pair(t) -> [its, it];
class_pair(f) -> [i, we].

%% pos_G(d): generated (OIG C.5 Definition C.1).
reach(TIM, D) ->
    lists:sort([P || P <- lists:seq(1, 8),
                     lists:member(D, class_pair(
                         le_stacks:class(le_stacks:element_at(TIM, P))))]).

reach_map(TIM) -> [{D, reach(TIM, D)} || D <- domains()].

subsets() ->
    [lists:sort(S) || S <- powerset(domains())].

powerset([]) -> [[]];
powerset([H | T]) ->
    PT = powerset(T),
    PT ++ [[H | S] || S <- PT].

delta_access(TIM, DSet) ->
    lists:usort(lists:append([reach(TIM, D) || D <- DSet])).

delta_route(TIM, DSet) ->
    Acc = delta_access(TIM, DSet),
    {lists:member(1, Acc), lists:member(2, Acc)}.

class_counts(TIM) ->
    Subs = subsets(),
    {length(lists:usort(Subs)),
     length(lists:usort([delta_access(TIM, S) || S <- Subs])),
     length(lists:usort([delta_route(TIM, S) || S <- Subs])),
     1}.

capacity_tree(TIM) ->
    Subs = subsets(),
    ByRoute = lists:foldl(
                fun(S, Acc) ->
                        R = delta_route(TIM, S),
                        A = delta_access(TIM, S),
                        maps:update_with(
                          R, fun(M) -> maps:update_with(
                                         A, fun(N) -> N + 1 end, 1, M)
                             end, #{A => 1}, Acc)
                end, #{}, Subs),
    maps:map(fun(_, M) ->
                     lists:reverse(lists:sort(maps:values(M)))
             end, ByRoute).

%% The OIG fingerprint: the labeled reach family of the locked lens.
%% Contrary partners are identical BY CONSTRUCTION under this lens
%% (UMA section 11); an OIG-only classifier returning 16 distinguishable
%% fingerprints is wrong by construction (SPEC section 32).
fingerprint(TIM) -> lists:sort(reach_map(TIM)).
