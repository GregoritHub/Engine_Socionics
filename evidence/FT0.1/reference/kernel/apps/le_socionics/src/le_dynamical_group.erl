%% le_dynamical_group — full finite dynamical group (SPEC section 15).
%% Status: estafette source_defined — the exact permutation IS supplied by
%% UMA section 10:  R(a,v,r) = (r, v, 1 xor a).
%% (Not inferred from the old CAPE cycle.)  Expected group: F2^3 x| D4,
%% order 64, exponent 4, center {Identity, Super-Ego}.
-module(le_dynamical_group).
-export([estafette/0, elements/0, order/0, element_order/1,
         center/0, nonidentity_center/0, verify/0]).

estafette() ->
    %% linear part (a,v,r) -> (r,v,a); translation (0,0,1)
    {affine, {{0,0,1}, {0,1,0}, {1,0,0}}, {0,0,1}}.

identity_aff() -> {affine, le_gf2:identity(3), {0,0,0}}.

elements() ->
    Gens = le_relation_group:elements() ++ [estafette()],
    generate(sets:from_list([identity_aff()]), [identity_aff()], Gens).

generate(Seen, [], _Gens) -> lists:sort(sets:to_list(Seen));
generate(Seen, [G | Rest], Gens) ->
    New = [le_gf2:affine_compose(H, G) || H <- Gens],
    Fresh = [X || X <- New, not sets:is_element(X, Seen)],
    generate(sets:union(Seen, sets:from_list(Fresh)), Rest ++ Fresh, Gens).

order() -> length(elements()).

element_order(G) -> element_order(G, G, 1).
element_order(G, H, N) ->
    case H =:= identity_aff() of
        true -> N;
        false when N > 128 -> erlang:error(order_overflow);
        false -> element_order(G, le_gf2:affine_compose(G, H), N + 1)
    end.

center() ->
    Els = elements(),
    [G || G <- Els,
          lists:all(fun(H) ->
                            le_gf2:affine_compose(G, H) =:=
                                le_gf2:affine_compose(H, G)
                    end, Els)].

nonidentity_center() ->
    [Z] = [G || G <- center(), G =/= identity_aff()],
    Z.

verify() ->
    Els = elements(),
    64 = length(Els),
    4 = lists:max([element_order(G) || G <- Els]),
    2 = length(center()),
    R = estafette(),
    4 = element_order(R),
    %% R^2 is the Activation position permutation and lies in the relation
    %% group (UMA section 10)
    R2 = le_gf2:affine_compose(R, R),
    true = lists:member(R2, le_relation_group:elements()),
    ese = le_relation_group:apply_relation(R2, ile),
    %% the nonidentity central element is a relation (Super-Ego)
    Z = nonidentity_center(),
    true = lists:member(Z, le_relation_group:elements()),
    ok.
