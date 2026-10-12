%% le_v2_tests — EUnit acceptance tests (run with `rebar3 eunit`).
%% Mirrors pyref/verify_all.py; every count generated, nothing memorized.
-module(le_v2_tests).
-include_lib("eunit/include/eunit.hrl").

stacks_test() ->
    ?assertEqual(ok, le_stacks:verify_stacks()),
    ?assertEqual(16, length(le_stacks:tims())).

geometry_test() ->
    ?assertEqual(12, length(le_position_geometry:cube_edges())),
    ?assertEqual([4,3,2,1,1,2,3,4],
                 [le_position_geometry:dimension(P)
                  || P <- le_position_geometry:positions()]),
    ?assertEqual([1,2,7,8],
                 [P || P <- le_position_geometry:positions(),
                       le_position_geometry:strong(P)]).

frames_test() ->
    ?assertEqual(ok, le_tim_frame:verify_all()).

routing_test() ->
    ?assertEqual([fe, fi, se], le_routing:neighbors(iee, ti)),
    ?assert(lists:all(fun(T) -> length(le_routing:edges(T)) =:= 12 end,
                      le_stacks:tims())).

relations_test() ->
    ?assertEqual(ok, le_relation_group:verify()).

dynamical_group_test_() ->
    {timeout, 120, fun() ->
        ?assertEqual(ok, le_dynamical_group:verify())
    end}.

model_g_test() ->
    ?assertEqual([{te, ne}, {ne, fe}], le_model_g:directed_chords(iee)),
    ?assertEqual(unresolved_source_extraction,
                 le_model_g:block_assignment()),
    ?assertMatch({unresolved_source_extraction, _},
                 le_model_g:role_of_g(5)).

oig_test() ->
    ?assert(lists:all(fun(T) ->
                              {16,10,4,1} =:= le_oig_domain:class_counts(T)
                      end, le_stacks:tims())),
    ?assertEqual(60, length(le_oig:lawful_nv_pairs())),
    ?assertEqual(le_oig:fingerprint(ile), le_oig:fingerprint(ili)).

empirical_separation_test() ->
    ?assertEqual(ok, le_verify:empirical_separation()).

reinin_test() ->
    ?assertEqual(15, length(le_reinin:all_characters())),
    ?assertEqual(35, le_reinin:two_dim_subspace_count()).

unfitted_refusal_test() ->
    ?assertError({structural_only, _},
                 le_transition_model:probability(
                   le_transition_model:new(), iee, ne, ti)).
