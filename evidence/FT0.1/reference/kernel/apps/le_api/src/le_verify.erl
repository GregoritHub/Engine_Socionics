%% le_verify — Erlang-side acceptance runner (`le verify ...`).
%% Mirrors pyref/verify_all.py.  Every count generated, nothing memorized.
-module(le_verify).
-export([all/0, geometry/0, oig/0, empirical_separation/0]).

all() ->
    ok = geometry(),
    ok = oig(),
    ok = empirical_separation(),
    io:format("le_verify: all sections passed~n"),
    ok.

geometry() ->
    ok = le_stacks:verify_stacks(),
    8 = length(le_position_geometry:positions()),
    12 = length(le_position_geometry:cube_edges()),
    true = lists:all(fun(P) ->
                             length(le_position_geometry:neighbors(P)) =:= 3
                     end, le_position_geometry:positions()),
    [4,3,2,1,1,2,3,4] =
        [maps:get(dimensionality, le_position_geometry:access(P))
         || P <- le_position_geometry:positions()],
    true = lists:all(fun(P) ->
                             le_position_geometry:dimension(P) =:=
                                 maps:get(dimensionality,
                                          le_position_geometry:access(P))
                     end, le_position_geometry:positions()),
    [1,2,7,8] = [P || P <- le_position_geometry:positions(),
                      le_position_geometry:strong(P)],
    7 = length(le_ie_geometry:linear_forms()),
    true = lists:all(
             fun(W) ->
                     4 =:= length([E || E <- le_ie_geometry:elements(),
                                        le_gf2:dot(W, le_ie_geometry:coord(E))
                                            =:= 0])
             end, le_ie_geometry:linear_forms()),
    ok = le_tim_frame:verify_all(),
    15 = length(le_reinin:all_characters()),
    true = lists:all(fun(W) ->
                             {P0, P1} = le_reinin:pole_members(W),
                             length(P0) =:= 8 andalso length(P1) =:= 8
                     end, le_reinin:all_characters()),
    35 = le_reinin:two_dim_subspace_count(),
    true = lists:all(fun(T) ->
                             12 =:= length(le_routing:edges(T)) andalso
                                 lists:all(fun(IE) ->
                                                   3 =:= length(
                                                     le_routing:neighbors(T, IE))
                                           end, le_ie_geometry:elements())
                     end, le_stacks:tims()),
    [fe, fi, se] = le_routing:neighbors(iee, ti),
    ok = le_relation_group:verify(),
    ok = le_dynamical_group:verify(),
    ok.

oig() ->
    true = lists:all(fun(T) ->
                             {16, 10, 4, 1} =:= le_oig_domain:class_counts(T)
                     end, le_stacks:tims()),
    true = lists:all(
             fun(T) ->
                     Tree = lists:sort(maps:values(
                                         le_oig_domain:capacity_tree(T))),
                     Tree =:= lists:sort([[1,1], [1,1], [1,1], [7,1,1,1]])
             end, le_stacks:tims()),
    [{i, [1,4,6,7]}, {it, [2,3,5,8]}, {its, [1,2,7,8]}, {we, [3,4,5,6]}] =
        lists:sort(le_oig_domain:reach_map(ile)),
    12 = length(le_oig:quotients()),
    12 = length(lists:usort([S || {_, S} <- le_oig:all_supports()])),
    60 = length(le_oig:lawful_nv_pairs()),
    Shells = lists:foldl(
               fun({N, V}, Acc) ->
                       K = le_oig:shell_of(N, V),
                       maps:update_with(K, fun(L) -> [{N,V} | L] end,
                                        [{N,V}], Acc)
               end, #{}, le_oig:lawful_nv_pairs()),
    49 = maps:size(Shells),
    12 = length(maps:get([], Shells)),
    true = lists:all(fun({K, V}) ->
                             K =:= [] orelse length(V) =:= 1
                     end, maps:to_list(Shells)),
    16 = le_oig:meet_vp_count(),
    FPs = [{T, le_oig:fingerprint(T)} || T <- le_stacks:tims()],
    8 = length(lists:usort([F || {_, F} <- FPs])),
    true = lists:all(
             fun({A, B}) ->
                     le_oig:fingerprint(A) =:= le_oig:fingerprint(B)
             end,
             [{ile, ili}, {sei, see}, {ese, esi}, {lii, lie},
              {eie, eii}, {lsi, lse}, {sle, sli}, {iei, iee}]),
    ok.

empirical_separation() ->
    Dir = "/tmp/le_v2_erl_test_" ++
        integer_to_list(erlang:unique_integer([positive])),
    L = le_ledger:open(filename:join(Dir, "ledger.terms")),
    le_participant:lock_typing(L, s1, #{primary_tim => iee,
                                        method => interview,
                                        confidence => 0.8}),
    Plan = le_randomization:randomize(L, "u", [s1], [ti, se], 42),
    [#{trial_id := T1} | _] = Plan,
    le_prediction_lock:freeze(L, T1, #{model_name => m3_routing,
                                       model_version => "v2.0",
                                       parameter_version => unfitted,
                                       hypothesis => h1}),
    le_observation:record(L, T1, s1, #{latency_ms => 950, accuracy => 1}),
    {'EXIT', _} =
        (catch le_prediction_lock:freeze(L, T1, #{model_name => m3_routing})),
    le_participant:lock_typing(L, s1, #{primary_tim => ile,
                                        method => reassessment,
                                        confidence => 0.6}),
    2 = length(le_participant:typing_history(L, s1)),
    [Obs | _] = le_observation:observations(L),
    Packet = le_state_coding:blind_packet(L, maps:get(observation_id, Obs)),
    false = maps:is_key(tim, Packet),
    {'EXIT', _} = (catch le_observation:record(L, t2, s1,
                                               #{synthetic => true})),
    {'EXIT', _} =
        (catch le_export:theory_dataset(L, #{include_synthetic => true},
                                        confirmatory)),
    {'EXIT', _} =
        (catch le_transition_model:probability(le_transition_model:new(),
                                               iee, ne, ti)),
    ok.
