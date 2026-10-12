%% le_reserve_model behaviour + default unfitted implementation
%% (SPEC section 46).  No invented reserve physics; no physical units.
%% Any later normalized scale must be labeled model normalization.
-module(le_reserve_model).
-export([init/1, predict/3, update/4, name/0]).

name() -> unfitted_reserve.

init(_ModelState) -> unknown.
predict(_ModelState, _Context, _Control) -> unknown.
update(_ModelState, _Context, _Control, _Observation) -> unknown.
