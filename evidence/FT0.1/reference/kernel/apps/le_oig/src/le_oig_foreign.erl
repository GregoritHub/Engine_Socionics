%% le_oig_foreign — foreign quotient chain (SPEC section 28).
%% unpaired = exact foreign state (carrier-dependent / unbounded);
%% paired = empty vs nonempty (2 classes); top = 1 class.
%% Foreign keys are NEVER interpreted semantically (SPEC section 26).
-module(le_oig_foreign).
-export([split/1, foreign_class/2]).

%% Content is a list/set of opaque keys; the D/F split per OIG C.4.
split(Content) ->
    Keys = lists:usort(Content),
    D = [K || K <- Keys, lists:member(K, le_oig_domain:domains())],
    F = Keys -- D,
    {D, F}.

foreign_class(F, unpaired) -> lists:usort(F);
foreign_class(F, paired) -> F =/= [];
foreign_class(_, top) -> top.
