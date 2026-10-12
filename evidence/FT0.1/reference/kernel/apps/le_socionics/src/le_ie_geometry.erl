%% le_ie_geometry — information-element carrier E = F2^3 (SPEC section 9).
%% Status: derived (UMA section 3 atlas q,e,n:
%% q = rational, e = extroverted, n = internal).
-module(le_ie_geometry).
-export([elements/0, coord/1, element/1, linear_forms/0,
         semantic_dichotomies/0, generic_distance/2]).

elements() -> [si, ni, se, ne, ti, fi, te, fe].

coord(si) -> {0,0,0}; coord(ni) -> {0,0,1}; coord(se) -> {0,1,0};
coord(ne) -> {0,1,1}; coord(ti) -> {1,0,0}; coord(fi) -> {1,0,1};
coord(te) -> {1,1,0}; coord(fe) -> {1,1,1}.

element({0,0,0}) -> si; element({0,0,1}) -> ni; element({0,1,0}) -> se;
element({0,1,1}) -> ne; element({1,0,0}) -> ti; element({1,0,1}) -> fi;
element({1,1,0}) -> te; element({1,1,1}) -> fe.

linear_forms() -> [W || W <- le_gf2:all_vectors(3), W =/= {0,0,0}].

%% Partitions are exact; verbal polarity of each pole is NOT asserted
%% (naming follows the listed order of UMA section 3).
semantic_dichotomies() ->
    #{{1,0,0} => "rational/irrational",
      {0,1,0} => "extroverted/introverted",
      {0,0,1} => "internal/external",
      {1,1,0} => "static/dynamic",
      {1,0,1} => "abstract/involved",
      {0,1,1} => "alpha-gamma/beta-delta axis 1",
      {1,1,1} => "alpha-gamma/beta-delta axis 2"}.

generic_distance(A, B) ->
    {A1,A2,A3} = coord(A), {B1,B2,B3} = coord(B),
    (A1 bxor B1) + (A2 bxor B2) + (A3 bxor B3).
