%% le_profile_model — functional profile field (SPEC section 47).
%% Default: unknown for every IE with unfitted provenance.
%% native structural position != learned competence != current activation —
%% fitting may modify p_t; it must NEVER modify the definitive stacks.
-module(le_profile_model).
-export([init/1, name/0]).

name() -> unfitted_profile.

init(_ModelState) ->
    maps:from_list(
      [{IE, #{estimate => unknown, uncertainty => unknown,
              parameter_version => unfitted}}
       || IE <- le_ie_geometry:elements()]).
