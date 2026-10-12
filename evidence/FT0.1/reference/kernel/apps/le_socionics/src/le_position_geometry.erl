%% le_position_geometry — Model A carrier P = F2^3 (SPEC section 7).
%% Status: derived (UMA section 2 coordinates a,v,r).
%% a = accepting0/producing1, v = valued0/unvalued1, r = mental0/vital1.
-module(le_position_geometry).
-export([positions/0, coord/1, position/1, neighbors/1, hamming_distance/2,
         direction/2, cube_edges/0,
         access/1, strong/1, contact/1, bold/1, dimension/1]).

positions() -> lists:seq(1, 8).

coord(1) -> {0,0,0}; coord(2) -> {1,0,0}; coord(3) -> {0,1,0};
coord(4) -> {1,1,0}; coord(5) -> {0,0,1}; coord(6) -> {1,0,1};
coord(7) -> {0,1,1}; coord(8) -> {1,1,1}.

position({0,0,0}) -> 1; position({1,0,0}) -> 2; position({0,1,0}) -> 3;
position({1,1,0}) -> 4; position({0,0,1}) -> 5; position({1,0,1}) -> 6;
position({0,1,1}) -> 7; position({1,1,1}) -> 8.

neighbors(P) ->
    C = coord(P),
    lists:sort([position(le_gf2:vadd(C, E))
                || E <- [{1,0,0}, {0,1,0}, {0,0,1}]]).

hamming_distance(P, Q) ->
    {A1,A2,A3} = coord(P), {B1,B2,B3} = coord(Q),
    (A1 bxor B1) + (A2 bxor B2) + (A3 bxor B3).

direction(P, Q) -> le_gf2:vadd(coord(P), coord(Q)).

cube_edges() ->
    lists:usort([{min(P, Q), max(P, Q)}
                 || P <- positions(), Q <- neighbors(P)]).

%% Position metadata — status: source_defined (OIG C.3 = V11 verbatim).
%% Naming provenance: OIG C.3 says conscious/automatic; UMA section 2 says
%% mental/vital for coordinate r.  Sets coincide; mental/vital used here.
access(1) -> #{dimensionality => 4, name => leading,       frame => mental, valued => true,  mode => accepting};
access(2) -> #{dimensionality => 3, name => creative,      frame => mental, valued => true,  mode => producing};
access(3) -> #{dimensionality => 2, name => role,          frame => mental, valued => false, mode => accepting};
access(4) -> #{dimensionality => 1, name => vulnerable,    frame => mental, valued => false, mode => producing};
access(5) -> #{dimensionality => 1, name => suggestive,    frame => vital,  valued => true,  mode => accepting};
access(6) -> #{dimensionality => 2, name => activating,    frame => vital,  valued => true,  mode => producing};
access(7) -> #{dimensionality => 3, name => ignoring,      frame => vital,  valued => false, mode => accepting};
access(8) -> #{dimensionality => 4, name => demonstrative, frame => vital,  valued => false, mode => producing}.

%% Derived fields (UMA section 2): strong <=> v=r; contact = a+v+r;
%% bold = 1+a+r; d = 1 + 2*strong + bold.
strong(P) -> {_, V, R} = coord(P), V =:= R.
contact(P) -> {A, V, R} = coord(P), A bxor V bxor R.
bold(P) -> {A, _, R} = coord(P), 1 bxor A bxor R.
dimension(P) ->
    S = case strong(P) of true -> 1; false -> 0 end,
    1 + 2 * S + bold(P).
