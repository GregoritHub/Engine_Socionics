%% le_relation_group — classical intertype relations as affine
%% transformations of Model A position space (SPEC section 14).
%% Status: derived (UMA section 9).  Elements are COMPUTED from the frames,
%% never taken from a memorized table.
%%
%% Composition convention (used everywhere; documented; SPEC section 14):
%%   rel(T1, T2) = the unique affine G : P -> P with f_T2 = f_T1 o G.
%%   Chain rule: rel(T1,T3) = rel(T1,T2) composed-after rel(T2,T3), i.e.
%%   le_gf2:affine_compose(Rel12, Rel23) where compose(G,H)(x) = G(H(x))
%%   gives rel(T1,T3) = compose(Rel12, Rel23).
%%
%% RELATION NAMING (SPEC sections 14, 76): only names anchored in the
%% supplied sources are used —
%%   identity      definitional
%%   duality       V11 README anchor instance ILE -> SEI
%%   contrary      SPEC section 32 locked pairs
%%   activation    UMA section 10 (estafette squared)
%%   super_ego     UMA section 10 (nonidentity center of the 64-group)
%%   benefit / benefit_inverse        V11 le_itr structural derivation
%%   supervision / supervision_inverse V11 le_itr structural derivation
%% The remaining transformations carry stable structural ids
%% {unresolved_relation_name, AffineKey}; see UNRESOLVED_SOURCE_ITEMS.
-module(le_relation_group).
-export([rel/2, elements/0, apply_relation/2, name_of/1, named/1,
         contrary/1, dual/1, beneficiary/1, supervisee/1, verify/0]).

rel(T1, T2) ->
    le_gf2:affine_compose(
      le_gf2:affine_inverse(le_tim_frame:frame(T1)),
      le_tim_frame:frame(T2)).

elements() ->
    lists:usort([rel(T1, T2) || T1 <- le_stacks:tims(),
                                T2 <- le_stacks:tims()]).

apply_relation(G, TIM) ->
    Target = le_gf2:affine_compose(le_tim_frame:frame(TIM), G),
    case [T || T <- le_stacks:tims(),
               le_tim_frame:frame(T) =:= Target] of
        [T2] -> T2;
        [] -> erlang:error({not_a_lawful_frame, G, TIM})
    end.

contrary_pairs() ->
    [{ile, ili}, {sei, see}, {ese, esi}, {lii, lie},
     {eie, eii}, {lsi, lse}, {sle, sli}, {iei, iee}].

contrary(TIM) ->
    case lists:keyfind(TIM, 1, contrary_pairs()) of
        {_, B} -> B;
        false -> {A, _} = lists:keyfind(TIM, 2, contrary_pairs()), A
    end.

dual(TIM) -> apply_relation(rel(ile, sei), TIM).

%% V11 le_itr structural derivations (sourced legacy derivation).
beneficiary(TIM) ->
    {L, C} = le_stacks:ego(TIM),
    tim_from_ego(le_stacks:sib(le_stacks:opp(C)), le_stacks:opp(L)).

supervisee(TIM) ->
    {L, C} = le_stacks:ego(TIM),
    tim_from_ego(C, le_stacks:sib(L)).

tim_from_ego(L, C) ->
    [T] = [X || X <- le_stacks:tims(), le_stacks:ego(X) =:= {L, C}],
    T.

named(identity) -> rel(ile, ile);
named(duality) -> rel(ile, sei);
named(contrary) -> rel(ile, contrary(ile));
named(activation) ->
    R = le_dynamical_group:estafette(),
    le_gf2:affine_compose(R, R);
named(super_ego) -> le_dynamical_group:nonidentity_center();
named(benefit) -> rel(ile, beneficiary(ile));
named(benefit_inverse) -> le_gf2:affine_inverse(named(benefit));
named(supervision) -> rel(ile, supervisee(ile));
named(supervision_inverse) -> le_gf2:affine_inverse(named(supervision)).

name_of(G) ->
    Anchored = [identity, duality, contrary, activation, super_ego,
                benefit, benefit_inverse, supervision, supervision_inverse],
    case [N || N <- Anchored, named(N) =:= G] of
        [N | _] -> N;
        [] -> {unresolved_relation_name, G}
    end.

verify() ->
    Els = elements(),
    16 = length(Els),
    %% closure + inverses
    true = lists:all(fun({A, B}) ->
                             lists:member(le_gf2:affine_compose(A, B), Els)
                     end, [{A, B} || A <- Els, B <- Els]),
    true = lists:all(fun(A) ->
                             lists:member(le_gf2:affine_inverse(A), Els)
                     end, Els),
    %% simple transitivity theorem test (SPEC section 14): for any two TIMs
    %% exactly one relation carries the frame of T1 to that of T2.
    true = lists:all(
             fun({T1, T2}) ->
                     G = rel(T1, T2),
                     lists:member(G, Els) andalso
                         apply_relation(G, T1) =:= T2 andalso
                         [G] =:= [X || X <- Els,
                                       apply_relation(X, T1) =:= T2]
             end,
             [{T1, T2} || T1 <- le_stacks:tims(), T2 <- le_stacks:tims()]),
    %% coherent anchored relations
    true = lists:all(fun({A, B}) -> rel(A, B) =:= named(contrary) end,
                     contrary_pairs()),
    true = lists:all(fun(T) ->
                             rel(T, beneficiary(T)) =:= named(benefit)
                     end, le_stacks:tims()),
    true = lists:all(fun(T) ->
                             rel(T, supervisee(T)) =:= named(supervision)
                     end, le_stacks:tims()),
    ok.
