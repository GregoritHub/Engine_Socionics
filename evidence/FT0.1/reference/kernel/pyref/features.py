"""le_features mirror — theory-derived structural feature extractor.

SPEC sections 24-25:
  * returns structural variables independently;
  * NO hard-coded transition costs, weights, or invented coefficients;
  * outcome-blind by construction: this module has no access to observation
    records and imports nothing from the empirical layer;
  * profile/reserve-dependent features are absent until models are fitted
    (parameter_version 'unfitted' => they are reported as 'unknown').
"""

from .core import (position_of, ACCESS, pos_strong, pos_contact, pos_bold,
                   pos_dimension, routing_distance, routing_neighbors,
                   shortest_paths, primitive_direction, ELEMENTS)
from .oig import fingerprint  # noqa: F401  (fingerprint available to callers)
from . import core


def _position_features(tim, ie, prefix):
    p = position_of(tim, ie)
    a = ACCESS[p]
    return {
        prefix + "_model_a_position": p,
        prefix + "_position_name": a["name"],
        prefix + "_native_dimensionality": a["dimensionality"],
        prefix + "_valued": a["valued"],
        prefix + "_mental_vital": a["frame"],
        prefix + "_accepting_producing": a["mode"],
        prefix + "_strong_weak": "strong" if pos_strong(p) else "weak",
        prefix + "_bold_cautious": "bold" if pos_bold(p) else "cautious",
        prefix + "_contact_family": pos_contact(p),
    }


def _g_features(tim, ie, prefix):
    g = core.g_position_of_ie(tim, ie)
    role = core.G_ROLE[g]
    return {
        prefix + "_model_g_position": g,
        prefix + "_model_g_role": (role if isinstance(role, str)
                                   else "unresolved_source_extraction"),
        prefix + "_model_g_energetic_note":
            core.G_ENERGETIC_NOTE.get(g, "none_sourced"),
        prefix + "_model_g_vars": core.g_positional_vars(core.G_TO_A[g]),
    }


def path_features(tim, path):
    """Structural description of an explicit IE path (list of IEs)."""
    edges = list(zip(path, path[1:]))
    chords = set(core.directed_chords(tim))
    dirs = []
    uses_chord = False
    for a, b in edges:
        d = primitive_direction(tim, a, b)
        dirs.append(d)
        if (a, b) in chords:
            uses_chord = True
    return {
        "path": list(path),
        "path_length": len(edges),
        "primitive_direction_sequence": dirs,
        "all_steps_primitive": all(d is not None for d in dirs),
        "uses_model_g_chord": uses_chord,
    }


def extract(tim, start_ie, target_ie, intermediates=None, context=None,
            practice=None, parameter_version="unfitted"):
    """The structural feature vector (SPEC section 24).

    practice: optional dict with integer exposure counts, an
    experimental_instrument input (history of exposures), never an outcome.
    """
    intermediates = intermediates or []
    practice = practice or {}
    path = [start_ie] + list(intermediates) + [target_ie]
    dist = routing_distance(tim, start_ie, target_ie)
    sps = shortest_paths(tim, start_ie, target_ie)
    chosen = path_features(tim, path)
    feats = {"tim": tim, "start_ie": start_ie, "target_ie": target_ie}
    feats.update(_position_features(tim, start_ie, "start"))
    feats.update(_position_features(tim, target_ie, "target"))
    feats.update(_g_features(tim, start_ie, "start"))
    feats.update(_g_features(tim, target_ie, "target"))
    feats.update({
        "primitive_routing_distance": dist,
        "generic_ie_distance": _generic_distance(start_ie, target_ie),
        "shortest_path_count": len(sps),
        "chosen_path_length": chosen["path_length"],
        "chosen_path_excess": chosen["path_length"] - dist,
        "primitive_direction_sequence":
            chosen["primitive_direction_sequence"],
        "all_steps_primitive": chosen["all_steps_primitive"],
        "route_uses_g_chord": chosen["uses_model_g_chord"],
        "direct_route": len(intermediates) == 0,
        "intermediate_states": list(intermediates),
        "practice_count_route": practice.get(("route", tuple(path)), 0),
        "practice_count_target_ie": practice.get(("ie", target_ie), 0),
        "practice_count_transition_pair":
            practice.get(("pair", start_ie, target_ie), 0),
        "parameter_version": parameter_version,
    })
    # fitted-model features are absent/unknown before calibration (SPEC 24)
    if parameter_version == "unfitted":
        feats.update({
            "estimated_target_profile_enhancement": "unknown",
            "estimated_starting_reserve": "unknown",
            "estimated_reserve_sensitivity": "unknown",
        })
    if context is not None:
        feats["context_ref"] = context.get("task_id", "unspecified")
    return feats


def _generic_distance(a, b):
    from .core import IE_COORD, hamming
    return hamming(IE_COORD[a], IE_COORD[b])


def model_feature_sets():
    """Which features each comparison model may use (SPEC section 42)."""
    return {
        "m0_null": ["practice_count_target_ie", "practice_count_route",
                    "context_ref"],
        "m1_jungian": ["jungian_e", "jungian_n", "jungian_t", "jungian_p"],
        "m2_model_a": ["target_native_dimensionality", "target_valued",
                       "target_mental_vital", "target_accepting_producing"],
        "m3_routing": ["primitive_routing_distance", "shortest_path_count",
                       "chosen_path_excess", "direct_route",
                       "generic_ie_distance"],
        "m4_model_g": ["target_model_g_role", "route_uses_g_chord",
                       "target_model_g_position"],
        "m5_full_dynamic": ["estimated_target_profile_enhancement",
                            "estimated_starting_reserve"],
    }
