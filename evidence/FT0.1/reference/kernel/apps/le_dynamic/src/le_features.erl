%% le_features — structural feature extractor (SPEC sections 24-25).
%% The most important first empirical component.
%% OUTCOME-BLIND BY CONSTRUCTION: no clause reads observation records; the
%% module has no dependency on le_empirical.  NO hard-coded transition
%% costs; structural variables are output independently and coefficients
%% are determined only by empirical fitting.
-module(le_features).
-export([extract/6, model_feature_sets/0]).

position_features(TIM, IE, Prefix) ->
    P = le_stacks:position_of(TIM, IE),
    A = le_position_geometry:access(P),
    [{key(Prefix, model_a_position), P},
     {key(Prefix, position_name), maps:get(name, A)},
     {key(Prefix, native_dimensionality), maps:get(dimensionality, A)},
     {key(Prefix, valued), maps:get(valued, A)},
     {key(Prefix, mental_vital), maps:get(frame, A)},
     {key(Prefix, accepting_producing), maps:get(mode, A)},
     {key(Prefix, strong_weak),
      case le_position_geometry:strong(P) of true -> strong;
          false -> weak end},
     {key(Prefix, bold_cautious),
      case le_position_geometry:bold(P) of 1 -> bold; 0 -> cautious end},
     {key(Prefix, contact_family), le_position_geometry:contact(P)}].

g_features(TIM, IE, Prefix) ->
    G = le_model_g:g_position(TIM, IE),
    Role = case le_model_g:role_of_g(G) of
               {unresolved_source_extraction, _} ->
                   unresolved_source_extraction;
               R -> R
           end,
    [{key(Prefix, model_g_position), G},
     {key(Prefix, model_g_role), Role},
     {key(Prefix, model_g_energetic_note), le_model_g:energetic_note(G)},
     {key(Prefix, model_g_vars),
      le_model_g:positional_vars(le_model_g:g_to_a(G))}].

key(Prefix, Name) ->
    list_to_atom(atom_to_list(Prefix) ++ "_" ++ atom_to_list(Name)).

extract(TIM, StartIE, TargetIE, Intermediates, Practice, ParamVersion) ->
    Path = [StartIE | Intermediates] ++ [TargetIE],
    Dist = le_routing:distance(TIM, StartIE, TargetIE),
    SPs = le_routing:shortest_paths(TIM, StartIE, TargetIE),
    Chosen = le_routing:path_features(TIM, Path),
    Base =
        [{tim, TIM}, {start_ie, StartIE}, {target_ie, TargetIE}]
        ++ position_features(TIM, StartIE, start)
        ++ position_features(TIM, TargetIE, target)
        ++ g_features(TIM, StartIE, start)
        ++ g_features(TIM, TargetIE, target)
        ++ [{primitive_routing_distance, Dist},
            {generic_ie_distance,
             le_ie_geometry:generic_distance(StartIE, TargetIE)},
            {shortest_path_count, length(SPs)},
            {chosen_path_length, maps:get(path_length, Chosen)},
            {chosen_path_excess, maps:get(path_length, Chosen) - Dist},
            {primitive_direction_sequence,
             maps:get(primitive_direction_sequence, Chosen)},
            {all_steps_primitive, maps:get(all_steps_primitive, Chosen)},
            {route_uses_g_chord, maps:get(uses_model_g_chord, Chosen)},
            {direct_route, Intermediates =:= []},
            {intermediate_states, Intermediates},
            {practice_count_route,
             maps:get({route, Path}, Practice, 0)},
            {practice_count_target_ie,
             maps:get({ie, TargetIE}, Practice, 0)},
            {practice_count_transition_pair,
             maps:get({pair, StartIE, TargetIE}, Practice, 0)},
            {parameter_version, ParamVersion}],
    Fitted = case ParamVersion of
                 unfitted ->
                     [{estimated_target_profile_enhancement, unknown},
                      {estimated_starting_reserve, unknown},
                      {estimated_reserve_sensitivity, unknown}];
                 _ -> []
             end,
    maps:from_list(Base ++ Fitted).

%% Which features each comparison model may use (SPEC section 42).
model_feature_sets() ->
    #{m0_null => [practice_count_target_ie, practice_count_route],
      m1_jungian => [jungian_e, jungian_n, jungian_t, jungian_p],
      m2_model_a => [target_native_dimensionality, target_valued,
                     target_mental_vital, target_accepting_producing],
      m3_routing => [primitive_routing_distance, shortest_path_count,
                     chosen_path_excess, direct_route, generic_ie_distance],
      m4_model_g => [target_model_g_role, route_uses_g_chord,
                     target_model_g_position],
      m5_full_dynamic => [estimated_target_profile_enhancement,
                          estimated_starting_reserve]}.
