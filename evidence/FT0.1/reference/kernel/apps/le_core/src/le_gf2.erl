%% le_gf2 — general GF(2) linear/affine algebra (SPEC section 10).
%% Vectors are tuples of 0|1; matrices are tuples of row-tuples.
%% Nothing is hard-coded that can be generated exhaustively.
-module(le_gf2).
-export([vadd/2, dot/2, mat_vec/2, mat_mul/2, identity/1,
         rank/1, det/1, inv/1,
         affine_apply/2, affine_compose/2, affine_inverse/1,
         char_eval/2, all_vectors/1, span/2, annihilator/2, cosets/2]).

vadd(U, V) ->
    list_to_tuple([A bxor B || {A, B} <- lists:zip(tuple_to_list(U),
                                                   tuple_to_list(V))]).

dot(U, V) ->
    lists:foldl(fun({A, B}, S) -> S bxor (A band B) end, 0,
                lists:zip(tuple_to_list(U), tuple_to_list(V))).

mat_vec(M, X) ->
    list_to_tuple([dot(Row, X) || Row <- tuple_to_list(M)]).

mat_mul(A, B) ->
    Bt = transpose(B),
    list_to_tuple([list_to_tuple([dot(Row, Col) || Col <- Bt])
                   || Row <- tuple_to_list(A)]).

transpose(M) ->
    Rows = [tuple_to_list(R) || R <- tuple_to_list(M)],
    [list_to_tuple(C) || C <- transpose_lists(Rows)].

transpose_lists([[] | _]) -> [];
transpose_lists(Rows) ->
    [[hd(R) || R <- Rows] | transpose_lists([tl(R) || R <- Rows])].

identity(N) ->
    list_to_tuple([list_to_tuple([bool_to_int(I =:= J)
                                  || J <- lists:seq(1, N)])
                   || I <- lists:seq(1, N)]).

bool_to_int(true) -> 1;
bool_to_int(false) -> 0.

rank(M) ->
    Rows = [tuple_to_list(R) || R <- tuple_to_list(M)],
    gauss_rank(Rows, 0, 1).

gauss_rank(Rows, Rank, Col) ->
    Width = case Rows of [] -> 0; [R | _] -> length(R) end,
    case Col > Width of
        true -> Rank;
        false ->
            case pivot(Rows, Rank + 1, Col) of
                none -> gauss_rank(Rows, Rank, Col + 1);
                PivIdx ->
                    Rows1 = swap(Rows, Rank + 1, PivIdx),
                    Piv = lists:nth(Rank + 1, Rows1),
                    Rows2 = [case {I =/= Rank + 1,
                                   lists:nth(Col, R) =:= 1} of
                                 {true, true} -> xor_rows(R, Piv);
                                 _ -> R
                             end || {I, R} <- enumerate(Rows1)],
                    gauss_rank(Rows2, Rank + 1, Col + 1)
            end
    end.

pivot(Rows, From, Col) ->
    Cand = [I || {I, R} <- enumerate(Rows), I >= From,
                 lists:nth(Col, R) =:= 1],
    case Cand of [] -> none; [I | _] -> I end.

swap(L, I, I) -> L;
swap(L, I, J) ->
    A = lists:nth(I, L), B = lists:nth(J, L),
    [case K of I -> B; J -> A; _ -> E end || {K, E} <- enumerate(L)].

xor_rows(A, B) -> [X bxor Y || {X, Y} <- lists:zip(A, B)].

enumerate(L) -> lists:zip(lists:seq(1, length(L)), L).

det(M) ->
    N = tuple_size(M),
    case rank(M) of N -> 1; _ -> 0 end.

inv(M) ->
    N = tuple_size(M),
    I = identity(N),
    Aug = [tuple_to_list(element(K, M)) ++ tuple_to_list(element(K, I))
           || K <- lists:seq(1, N)],
    Red = gauss_solve(Aug, 1, N),
    list_to_tuple([list_to_tuple(lists:nthtail(N, R)) || R <- Red]).

gauss_solve(Rows, Col, N) when Col > N -> Rows;
gauss_solve(Rows, Col, N) ->
    PivIdx = case pivot(Rows, Col, Col) of
                 none -> erlang:error({singular_matrix, Col});
                 P -> P
             end,
    Rows1 = swap(Rows, Col, PivIdx),
    Piv = lists:nth(Col, Rows1),
    Rows2 = [case {I =/= Col, lists:nth(Col, R) =:= 1} of
                 {true, true} -> xor_rows(R, Piv);
                 _ -> R
             end || {I, R} <- enumerate(Rows1)],
    gauss_solve(Rows2, Col + 1, N).

%% Affine map {affine, M, B}: X -> M X + B.
affine_apply({affine, M, B}, X) -> vadd(mat_vec(M, X), B).

%% compose(G, H): X -> G(H(X)).
affine_compose({affine, MG, BG}, {affine, MH, BH}) ->
    {affine, mat_mul(MG, MH), vadd(mat_vec(MG, BH), BG)}.

affine_inverse({affine, M, B}) ->
    Mi = inv(M),
    {affine, Mi, mat_vec(Mi, B)}.

char_eval(W, X) -> dot(W, X).

all_vectors(N) ->
    lists:foldl(fun(_, Acc) ->
                        [erlang:append_element(V, Bit)
                         || V <- Acc, Bit <- [0, 1]]
                end, [{}], lists:seq(1, N)).

span(Vectors, N) ->
    Zero = list_to_tuple(lists:duplicate(N, 0)),
    close([Zero | Vectors]).

close(S0) ->
    S = lists:usort(S0),
    S1 = lists:usort(S ++ [vadd(A, B) || A <- S, B <- S]),
    case S1 =:= S of true -> S; false -> close(S1) end.

annihilator(Subspace, N) ->
    [W || W <- all_vectors(N),
          lists:all(fun(V) -> dot(W, V) =:= 0 end, Subspace)].

cosets(Subspace, N) ->
    lists:usort([lists:usort([vadd(X, V) || V <- Subspace])
                 || X <- all_vectors(N)]).
