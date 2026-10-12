%% le_routing — type-specific cognitive routing cube (SPEC section 12).
%% Status: derived (UMA section 18 transported routing cube).
%% NEVER the generic IE cube: adjacency is Hamming-1 in POSITION coordinates
%% pulled back through the TIM frame.
-module(le_routing).
-export([neighbors/2, edges/1, distance/2, distance/3, shortest_paths/3,
         path_features/2, primitive_direction/3]).

neighbors(TIM, IE) ->
    F = le_tim_frame:frame(TIM),
    Finv = le_gf2:affine_inverse(F),
    P = le_gf2:affine_apply(Finv, le_ie_geometry:coord(IE)),
    lists:sort([le_ie_geometry:element(
                  le_gf2:affine_apply(F, le_gf2:vadd(P, E)))
                || E <- [{1,0,0}, {0,1,0}, {0,0,1}]]).

edges(TIM) ->
    lists:usort([{min(A, B), max(A, B)}
                 || A <- le_ie_geometry:elements(),
                    B <- neighbors(TIM, A)]).

distance(TIM, {IE1, IE2}) -> distance(TIM, IE1, IE2).

distance(TIM, IE1, IE2) ->
    Finv = le_gf2:affine_inverse(le_tim_frame:frame(TIM)),
    {A1,A2,A3} = le_gf2:affine_apply(Finv, le_ie_geometry:coord(IE1)),
    {B1,B2,B3} = le_gf2:affine_apply(Finv, le_ie_geometry:coord(IE2)),
    (A1 bxor B1) + (A2 bxor B2) + (A3 bxor B3).

primitive_direction(TIM, IE1, IE2) ->
    Finv = le_gf2:affine_inverse(le_tim_frame:frame(TIM)),
    D = le_gf2:vadd(le_gf2:affine_apply(Finv, le_ie_geometry:coord(IE1)),
                    le_gf2:affine_apply(Finv, le_ie_geometry:coord(IE2))),
    case D of
        {1,0,0} -> {ok, D}; {0,1,0} -> {ok, D}; {0,0,1} -> {ok, D};
        _ -> not_primitive
    end.

shortest_paths(TIM, A, A) -> [[A]];
shortest_paths(TIM, A, B) ->
    Dist = distance(TIM, A, B),
    grow([[A]], TIM, B, Dist).

grow(Paths, _TIM, B, 0) -> [P || P <- Paths, lists:last(P) =:= B];
grow(Paths, TIM, B, N) ->
    Next = [P ++ [Nb] || P <- Paths, Nb <- neighbors(TIM, lists:last(P)),
                         distance(TIM, Nb, B) =:=
                             distance(TIM, lists:last(P), B) - 1],
    grow(Next, TIM, B, N - 1).

path_features(TIM, Path) ->
    Edges = lists:zip(lists:droplast(Path), tl(Path)),
    Dirs = [primitive_direction(TIM, X, Y) || {X, Y} <- Edges],
    Chords = le_model_g:directed_chords(TIM),
    UsesChord = lists:any(fun({X, Y}) ->
                                  lists:member({X, Y}, Chords) orelse
                                      lists:member({Y, X}, Chords)
                          end, Edges),
    #{path => Path,
      path_length => length(Edges),
      primitive_direction_sequence => Dirs,
      all_steps_primitive =>
          lists:all(fun(D) -> D =/= not_primitive end, Dirs),
      uses_model_g_chord => UsesChord}.
