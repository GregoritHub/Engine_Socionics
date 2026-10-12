%% le_model_g — Model G as an atlas on the SAME carrier (SPEC section 16).
%% NOT a second eight-node state space.
%% Status:
%%   G<->A permutation      source_defined (UMA section 13):
%%                          (G1..G8) = (A1,A8,A3,A6,A2,A5,A4,A7)
%%   positional variables   source_defined (UMA section 13):
%%                          lambda = 1+v+r, sigma = 1+a, xi = 1+a+r
%%   roles                  source_defined for G1 Leader, G2 Creative,
%%                          G4 Launching, G6 Manipulative, G7 Braking;
%%                          G3/G5/G8 role names and the position-to-block
%%                          assignment are unresolved_source_extraction.
%%   directed chords        source_defined (UMA section 19):
%%                          G4->G1, G1->G2, i.e. A6->A1->A8
%% No numerical energy values anywhere: categorical metadata only.
-module(le_model_g).
-export([g_to_a/1, a_to_g/1, positional_vars/1, g_role/2, g_position/2,
         role_of_g/1, energetic_note/1, block_names/0, block_assignment/0,
         directed_chords/1, hybrid_graph/1, edge_metadata/3]).

g_to_a(1) -> 1; g_to_a(2) -> 8; g_to_a(3) -> 3; g_to_a(4) -> 6;
g_to_a(5) -> 2; g_to_a(6) -> 5; g_to_a(7) -> 4; g_to_a(8) -> 7.

a_to_g(A) -> [G] = [X || X <- lists:seq(1, 8), g_to_a(X) =:= A], G.

positional_vars(APos) ->
    {A, V, R} = le_position_geometry:coord(APos),
    #{lambda => 1 bxor V bxor R,      %% corresponds to Model A strength
      sigma  => 1 bxor A,             %% accepting/producing polarity
      xi     => 1 bxor A bxor R}.     %% bold/cautious polarity

role_of_g(1) -> leader;
role_of_g(2) -> creative_g;
role_of_g(3) -> {unresolved_source_extraction,
                 "depends strongly on external support (UMA sec 19)"};
role_of_g(4) -> launching;
role_of_g(5) -> {unresolved_source_extraction, none};
role_of_g(6) -> manipulative;
role_of_g(7) -> braking;
role_of_g(8) -> {unresolved_source_extraction, none}.

energetic_note(1) -> "allocates resources (Leader)";
energetic_note(2) -> "receives an energy boost from the Leader";
energetic_note(4) -> "initiates the Leader";
energetic_note(6) -> "replenishes reserves";
energetic_note(7) -> "inhibition and energy loss; high resistance to workload";
energetic_note(_) -> none_sourced.

block_names() -> [social_mission, social_adaptation,
                  creative_self_realization, inflation].

%% UMA section 13 names the blocks but does not state which positions form
%% which block; SPEC section 76: do not guess.
block_assignment() -> unresolved_source_extraction.

g_position(TIM, IE) -> a_to_g(le_stacks:position_of(TIM, IE)).

g_role(TIM, IE) -> role_of_g(g_position(TIM, IE)).

%% Directed chords as IE pairs for this TIM: A6 -> A1 -> A8.
directed_chords(TIM) ->
    [{le_stacks:element_at(TIM, 6), le_stacks:element_at(TIM, 1)},
     {le_stacks:element_at(TIM, 1), le_stacks:element_at(TIM, 8)}].

hybrid_graph(TIM) ->
    Prim = le_routing:edges(TIM),
    Chords = directed_chords(TIM),
    PrimEdges =
        [#{from => A, to => B, directed => false,
           provenance =>
               case lists:member({A, B}, Chords) orelse
                    lists:member({B, A}, Chords) of
                   true -> both;
                   false -> primitive_model_a_route
               end}
         || {A, B} <- Prim],
    ChordEdges =
        [#{from => A, to => B, directed => true,
           provenance => model_g_directed_chord}
         || {A, B} <- Chords,
            not lists:member({min(A,B), max(A,B)}, Prim)],
    PrimEdges ++ ChordEdges.

edge_metadata(TIM, FromIE, ToIE) ->
    [E || E <- hybrid_graph(TIM),
          (maps:get(from, E) =:= FromIE andalso maps:get(to, E) =:= ToIE)
          orelse (not maps:get(directed, E) andalso
                  maps:get(from, E) =:= ToIE andalso
                  maps:get(to, E) =:= FromIE)].
