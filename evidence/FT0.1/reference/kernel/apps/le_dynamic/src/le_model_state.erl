%% le_model_state — constructor and guards for #model_state{}.
-module(le_model_state).
-include("le_model_state.hrl").
-export([new/1, new/2, subtypes/0]).

subtypes() -> [unknown, dominant, creative, normalizing, harmonizing].

new(TIM) -> new(TIM, unknown).

new(TIM, Subtype) ->
    true = lists:member(TIM, le_stacks:tims()),
    true = lists:member(Subtype, subtypes()),
    #model_state{tim = TIM, subtype = Subtype}.
