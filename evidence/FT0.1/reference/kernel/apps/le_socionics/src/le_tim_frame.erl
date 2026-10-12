%% le_tim_frame — TIMs as affine frames f_T : P -> E (SPEC section 11).
%% Status: derived.  The affine representation is DERIVED from the stack and
%% verified exhaustively across all eight positions; is_affine/1 fails loudly
%% if a stack cannot be represented as the expected affine frame.
-module(le_tim_frame).
-export([frame/1, matrix/1, offset/1, apply/2, inverse/2, is_affine/1,
         orientation/1, verify_all/0]).

frame(TIM) ->
    Points = [{le_position_geometry:coord(P),
               le_ie_geometry:coord(le_stacks:element_at(TIM, P))}
              || P <- le_position_geometry:positions()],
    B = proplists:get_value({0,0,0}, Points),
    Col = fun(E) -> le_gf2:vadd(proplists:get_value(E, Points), B) end,
    {C1, C2, C3} = {Col({1,0,0}), Col({0,1,0}), Col({0,0,1})},
    M = {{element(1,C1), element(1,C2), element(1,C3)},
         {element(2,C1), element(2,C2), element(2,C3)},
         {element(3,C1), element(3,C2), element(3,C3)}},
    Aff = {affine, M, B},
    Ok = lists:all(fun({X, Y}) -> le_gf2:affine_apply(Aff, X) =:= Y end,
                   Points),
    case Ok of
        true -> Aff;
        false -> erlang:error({stack_not_affine, TIM})
    end.

matrix(TIM) -> {affine, M, _} = frame(TIM), M.
offset(TIM) -> {affine, _, B} = frame(TIM), B.

apply(TIM, Position) ->
    le_ie_geometry:element(
      le_gf2:affine_apply(frame(TIM), le_position_geometry:coord(Position))).

inverse(TIM, IE) ->
    le_position_geometry:position(
      le_gf2:affine_apply(le_gf2:affine_inverse(frame(TIM)),
                          le_ie_geometry:coord(IE))).

is_affine(TIM) ->
    try frame(TIM), true catch error:{stack_not_affine, _} -> false end.

%% UMA section 4: the leading-to-creative displacement t = first matrix
%% column; lawful values {1,1,0} and {1,1,1}.  The binary choice coincides
%% with the Democratic/Aristocratic partition (verbal polarity unasserted).
orientation(TIM) ->
    {affine, M, _} = frame(TIM),
    {element(1, element(1, M)), element(1, element(2, M)),
     element(1, element(3, M))}.

verify_all() ->
    Tims = le_stacks:tims(),
    true = lists:all(fun is_affine/1, Tims),
    true = lists:all(fun(T) -> le_gf2:det(matrix(T)) =:= 1 end, Tims),
    true = lists:all(
             fun(T) ->
                     lists:all(fun(P) ->
                                       apply(T, P) =:=
                                           le_stacks:element_at(T, P)
                               end, le_position_geometry:positions())
             end, Tims),
    16 = length(lists:usort([frame(T) || T <- Tims])),
    true = lists:all(fun(T) ->
                             lists:member(orientation(T),
                                          [{1,1,0}, {1,1,1}])
                     end, Tims),
    ok.
