%% le_oig — product quotient lattice, signatures, fingerprints
%% (SPEC sections 26, 29, 32).
%% 12 product quotients; visibility vis(Q) = vis_D OR vis_F (never AND);
%% 12 structured supports S(d,f); union = componentwise strength max.
-module(le_oig).
-export([quotients/0, q_class/3, signature/3, depth_pair/3,
         support/2, support_union/2, all_supports/0,
         lawful_nv_pairs/0, shell_of/2, meet_vp_count/0,
         fingerprint/1]).

quotients() ->
    [{D, F} || D <- [dom, access, route, top],
               F <- [unpaired, paired, top]].

q_class(TIM, Content, {DL, FL}) ->
    {D, F} = le_oig_foreign:split(Content),
    {domain_class(TIM, D, DL), le_oig_foreign:foreign_class(F, FL)}.

domain_class(_TIM, D, dom) -> lists:usort(D);
domain_class(TIM, D, access) -> le_oig_domain:delta_access(TIM, D);
domain_class(TIM, D, route) -> le_oig_domain:delta_route(TIM, D);
domain_class(_TIM, _D, top) -> top.

signature(TIM, C0, C1) ->
    [{Q, case q_class(TIM, C0, Q) =/= q_class(TIM, C1, Q) of
             true -> 1; false -> 0
         end} || Q <- quotients()].

%% Depth = coarsest quotient level of each chain at which the change is
%% visible (OIG 4.2); visibility monotone toward finer levels.
depth_pair(TIM, C0, C1) ->
    Bits = maps:from_list(signature(TIM, C0, C1)),
    DFired = [L || L <- [route, access, dom],
                   maps:get({L, top}, Bits) =:= 1],
    FFired = [L || L <- [paired, unpaired],
                   maps:get({top, L}, Bits) =:= 1],
    {case DFired of [] -> none; [D | _] -> D end,
     case FFired of [] -> none; [F | _] -> F end}.

d_fine(none) -> 0; d_fine(route) -> 1; d_fine(access) -> 2; d_fine(dom) -> 3.
f_fine(none) -> 0; f_fine(paired) -> 1; f_fine(unpaired) -> 2.
d_strength(none) -> 0; d_strength(dom) -> 1; d_strength(access) -> 2;
d_strength(route) -> 3.
f_strength(none) -> 0; f_strength(unpaired) -> 1; f_strength(paired) -> 2.

%% S(d,f): fires at (DL,FL) iff domain fineness(DL) >= fineness(d) (d/=none)
%% OR foreign fineness(FL) >= fineness(f) (f/=none).
support({DD, FF}, {DL, FL}) ->
    VisD = DD =/= none andalso DL =/= top andalso
        d_fine(DL) >= d_fine(DD),
    VisF = FF =/= none andalso FL =/= top andalso
        f_fine(FL) >= f_fine(FF),
    case VisD orelse VisF of true -> 1; false -> 0 end.

support_union({D1, F1}, {D2, F2}) ->
    {case d_strength(D1) >= d_strength(D2) of true -> D1; false -> D2 end,
     case f_strength(F1) >= f_strength(F2) of true -> F1; false -> F2 end}.

all_supports() ->
    [{{D, F}, [{Q, support({D, F}, Q)} || Q <- quotients()]}
     || D <- [none, dom, access, route], F <- [none, unpaired, paired]].

lawful_nv_pairs() ->
    [{{DN, FN}, {DV, FV}}
     || DV <- [none, dom, access, route], FV <- [none, unpaired, paired],
        DN <- [none, dom, access, route], FN <- [none, unpaired, paired],
        d_strength(DN) =< d_strength(DV),
        f_strength(FN) =< f_strength(FV)].

shell_of(N, V) ->
    [Q || Q <- quotients(), support(V, Q) =:= 1, support(N, Q) =:= 0].

meet_vp_count() ->
    length(lists:usort(
             [{V, P} || {D, F} = V <- [{X, Y}
                                       || X <- [none, dom, access, route],
                                          Y <- [none, unpaired, paired]],
                        P <- case f_strength(F) >= f_strength(paired) of
                                 true -> [0, 1];
                                 false -> [0]
                             end,
                        D =:= D])).

fingerprint(TIM) -> le_oig_domain:fingerprint(TIM).
