%% le_transition_model — P(z' | z, tau, p, r, e, u; theta) (SPEC section 21).
%% Operates in structural_only mode until theta is estimated from real
%% observations.  Returns features, permissible routes and hypotheses —
%% NEVER fabricated probabilities.
-module(le_transition_model).
-export([new/0, new/2, mode/1, permissible_routes/4, features/4,
         probability/4]).

new() -> #{mode => structural_only, theta => undefined}.

new(fitted, Theta) when Theta =/= undefined ->
    #{mode => fitted, theta => Theta}.

mode(#{mode := M}) -> M.

permissible_routes(Model, TIM, Z, Target) ->
    #{mode => mode(Model),
      primitive_neighbors => le_routing:neighbors(TIM, Z),
      routing_distance => le_routing:distance(TIM, Z, Target),
      numerical_probabilities =>
          case mode(Model) of
              structural_only -> unavailable_unfitted;
              fitted -> fitted
          end}.

features(_Model, TIM, Z, Target) ->
    le_features:extract(TIM, Z, Target, [], #{}, unfitted).

probability(#{mode := structural_only}, _TIM, _Z, _Target) ->
    erlang:error({structural_only,
                  "no numerical kernel has been estimated from "
                  "observations (SPEC sections 2, 21)"});
probability(#{mode := fitted}, _TIM, _Z, _Target) ->
    erlang:error({not_implemented_until_phase_6, calibration_required}).
