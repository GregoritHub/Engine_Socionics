%% le_stacks — the definitive Model A stacks. ABSOLUTE (SPEC section 5).
%% Status: source_defined (SPEC section 5 = OIG Appendix C.2).
%% Stacks are ALSO generated from the locked ego algebra; verify_stacks/0
%% asserts generated =:= definitive for all 16 TIMs (build failure otherwise).
-module(le_stacks).
-export([tims/0, definitive/1, generated/1, ego/1, element_at/2,
         position_of/2, class/1, attitude/1, rationality/1, sib/1, opp/1,
         verify_stacks/0]).

tims() -> [eie, eii, ese, esi, iee, iei, ile, ili,
           lie, lii, lse, lsi, see, sei, sle, sli].

definitive(iee) -> [ne, fi, se, ti, si, te, ni, fe];
definitive(ile) -> [ne, ti, se, fi, si, fe, ni, te];
definitive(sle) -> [se, ti, ne, fi, ni, fe, si, te];
definitive(see) -> [se, fi, ne, ti, ni, te, si, fe];
definitive(iei) -> [ni, fe, si, te, se, ti, ne, fi];
definitive(ili) -> [ni, te, si, fe, se, fi, ne, ti];
definitive(sli) -> [si, te, ni, fe, ne, fi, se, ti];
definitive(sei) -> [si, fe, ni, te, ne, ti, se, fi];
definitive(eie) -> [fe, ni, te, si, ti, se, fi, ne];
definitive(ese) -> [fe, si, te, ni, ti, ne, fi, se];
definitive(lse) -> [te, si, fe, ni, fi, ne, ti, se];
definitive(lie) -> [te, ni, fe, si, fi, se, ti, ne];
definitive(eii) -> [fi, ne, ti, se, te, si, fe, ni];
definitive(esi) -> [fi, se, ti, ne, te, ni, fe, si];
definitive(lsi) -> [ti, se, fi, ne, fe, ni, te, si];
definitive(lii) -> [ti, ne, fi, se, fe, si, te, ni].

class(ne) -> n; class(ni) -> n; class(se) -> s; class(si) -> s;
class(te) -> t; class(ti) -> t; class(fe) -> f; class(fi) -> f.

attitude(E) when E =:= ne; E =:= se; E =:= te; E =:= fe -> extro;
attitude(_) -> intro.

rationality(E) ->
    case class(E) of
        n -> irrational; s -> irrational; _ -> rational
    end.

sib(ne) -> se; sib(se) -> ne; sib(ni) -> si; sib(si) -> ni;
sib(te) -> fe; sib(fe) -> te; sib(ti) -> fi; sib(fi) -> ti.

opp(ne) -> ni; opp(ni) -> ne; opp(se) -> si; opp(si) -> se;
opp(te) -> ti; opp(ti) -> te; opp(fe) -> fi; opp(fi) -> fe.

ego(TIM) ->
    [L, C | _] = definitive(TIM),
    {L, C}.

%% OIG C.2 stack rule: (l,c,SIB l,SIB c,OPP SIB l,OPP SIB c,OPP l,OPP c)
generated(TIM) ->
    {L, C} = ego(TIM),
    [L, C, sib(L), sib(C), opp(sib(L)), opp(sib(C)), opp(L), opp(C)].

element_at(TIM, Pos) -> lists:nth(Pos, definitive(TIM)).

position_of(TIM, El) ->
    Stack = definitive(TIM),
    length(lists:takewhile(fun(X) -> X =/= El end, Stack)) + 1.

%% Build gate: any disagreement between generated and definitive is failure.
verify_stacks() ->
    Bad = [T || T <- tims(), generated(T) =/= definitive(T)],
    case Bad of
        [] -> ok;
        _ -> erlang:error({definitive_stack_mismatch, Bad})
    end.
