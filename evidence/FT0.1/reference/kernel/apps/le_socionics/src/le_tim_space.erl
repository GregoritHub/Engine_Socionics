%% le_tim_space — Jungian TIM space TJ = F2^4 (SPEC section 13).
%% Status: derived from locked ego pairs.  Coordinate convention documented:
%% E=1 extroverted, N=1 intuitive, T=1 logical, P=1 irrational.
-module(le_tim_space).
-export([jungian_coord/1, all_coords/0]).

jungian_coord(TIM) ->
    {L, C} = le_stacks:ego(TIM),
    Irr = case le_stacks:rationality(L) of irrational -> L; _ -> C end,
    Rat = case Irr of L -> C; _ -> L end,
    E = case le_stacks:attitude(L) of extro -> 1; intro -> 0 end,
    N = case le_stacks:class(Irr) of n -> 1; s -> 0 end,
    T = case le_stacks:class(Rat) of t -> 1; f -> 0 end,
    P = case le_stacks:rationality(L) of irrational -> 1; rational -> 0 end,
    {E, N, T, P}.

all_coords() -> [{T, jungian_coord(T)} || T <- le_stacks:tims()].
