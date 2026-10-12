%% le_reinin — Reinin dual space (SPEC section 13).
%% Status: locked name table source_defined (UMA section 6); everything
%% else generated.  Verbal pole polarity (which pole carries which name)
%% is NOT asserted; only the partitions.
-module(le_reinin).
-export([character/2, all_characters/0, character_name/1, pole_members/1,
         shared_characters/1, annihilator/1, cosets/1,
         two_dim_subspace_count/0]).

character(W, TIM) -> le_gf2:dot(W, le_tim_space:jungian_coord(TIM)).

all_characters() -> [W || W <- le_gf2:all_vectors(4), W =/= {0,0,0,0}].

character_name({1,0,0,0}) -> "extraverted/introverted";
character_name({0,1,0,0}) -> "intuitive/sensing";
character_name({0,0,1,0}) -> "logical/ethical";
character_name({0,0,0,1}) -> "irrational/rational";
character_name({1,1,0,0}) -> "carefree/farsighted";
character_name({1,0,1,0}) -> "yielding/obstinate";
character_name({1,0,0,1}) -> "static/dynamic";
character_name({0,1,1,0}) -> "democratic/aristocratic";
character_name({0,1,0,1}) -> "tactical/strategic";
character_name({0,0,1,1}) -> "constructivist/emotivist";
character_name({1,1,1,0}) -> "positivist/negativist";
character_name({1,1,0,1}) -> "judicious/decisive";
character_name({1,0,1,1}) -> "subjectivist/objectivist";
character_name({0,1,1,1}) -> "process/result";
character_name({1,1,1,1}) -> "asking/declaring".

pole_members(W) ->
    {[T || T <- le_stacks:tims(), character(W, T) =:= 0],
     [T || T <- le_stacks:tims(), character(W, T) =:= 1]}.

shared_characters(TypeGroup) ->
    [W || W <- all_characters(),
          length(lists:usort([character(W, T) || T <- TypeGroup])) =:= 1].

annihilator(DirectionSpace) -> le_gf2:annihilator(DirectionSpace, 4).

cosets(Subspace) -> le_gf2:cosets(Subspace, 4).

%% Generated, not memorized: the count of 2-dim subspaces of F2^4.
two_dim_subspace_count() ->
    NZ = all_characters(),
    Subs = lists:usort([lists:usort([{0,0,0,0}, U, V, le_gf2:vadd(U, V)])
                        || U <- NZ, V <- NZ, U =/= V,
                           le_gf2:vadd(U, V) =/= {0,0,0,0}]),
    length([S || S <- Subs, length(S) =:= 4]).
