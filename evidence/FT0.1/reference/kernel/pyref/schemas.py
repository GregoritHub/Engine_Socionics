"""Versioned record schemas + a small dependency-free validator
(SPEC section 62).  Malformed records are rejected.

Each schema: {"version", "required": {field: type}, "optional": {field: type}}
type is one of: str, int, float, number, bool, dict, list, ie, tim, quality.
"""

from .core import TIMS, ELEMENTS

SCHEMAS = {
    "study": {
        "version": "1",
        "required": {"study_id": "str", "mode": "study_mode",
                     "conditions": "list", "condition_definitions": "dict",
                     "randomization_seed": "int"},
        "optional": {"trials_per_condition": "int",
                     "primary_hypothesis": "str",
                     "predicted_ordering": "list",
                     "task_registry_version": "str",
                     "protocol_version": "str", "notes": "str"},
    },
    "participant": {
        "version": "1",
        "required": {"subject_id": "str"},
        "optional": {"registered_at": "str"},
    },
    "typing_lock": {
        "version": "1",
        "required": {"subject_id": "str", "primary_tim": "tim",
                     "confidence": "number", "method": "str",
                     "typing_quality": "quality"},
        "optional": {"alternatives": "list", "rater_ids": "list",
                     "agreement": "number", "evidence_ref": "str",
                     "typing_protocol_version": "str"},
    },
    "task_family": {
        "version": "1",
        "required": {"task_family_id": "str", "semantic_version": "str",
                     "designed_target_ie": "ie",
                     "operation_description": "str", "scoring_rule": "str",
                     "validation_status": "str"},
        "optional": {"contrast_ie": "ie", "difficulty_parameters": "dict",
                     "pilot_statistics": "dict"},
    },
    "trial": {
        "version": "1",
        "required": {"trial_id": "str", "subject_id": "str",
                     "condition_id": "str"},
        "optional": {"session_id": "str", "order_index": "int",
                     "randomization_seed": "int"},
    },
    "prediction": {
        "version": "1",
        "required": {"trial_id": "str", "model_name": "str",
                     "model_version": "str", "parameter_version": "str",
                     "hypothesis": "str"},
        "optional": {"predicted_ordering": "list",
                     "predicted_route": "list",
                     "structural_features": "dict",
                     "code_commit": "str",
                     "source_manifest_hash": "str"},
    },
    "observation": {
        "version": "1",
        "required": {"trial_id": "str", "subject_id": "str", "raw": "dict"},
        "optional": {"instrument_version": "str", "synthetic": "bool",
                     "generator_version": "str",
                     "generator_parameters": "dict"},
    },
    "state_code": {
        "version": "1",
        "required": {"observation_id": "str", "coder_id": "str",
                     "coded_ie": "ie", "confidence": "number"},
        "optional": {"evidence_ref": "str", "alternative_ie": "ie",
                     "blind": "bool", "coding_protocol_version": "str"},
    },
    "parameter_set": {
        "version": "1",
        "required": {"parameter_version": "str", "model_name": "str",
                     "fitted_from_dataset_hash": "str",
                     "estimates": "dict"},
        "optional": {"uncertainty": "dict", "fit_diagnostics": "dict"},
    },
    "model_result": {
        "version": "1",
        "required": {"model_name": "str", "dataset_hash": "str",
                     "metric": "str", "value": "number"},
        "optional": {"holdout": "str", "notes": "str"},
    },
    "manifest": {
        "version": "1",
        "required": {"kind": "str", "hashes": "dict"},
        "optional": {"git_commit": "str", "engine_version": "str",
                     "created_at": "str"},
    },
}


class SchemaError(ValueError):
    pass


def _check_type(name, value, ty):
    ok = {
        "str": lambda v: isinstance(v, str),
        "int": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "float": lambda v: isinstance(v, float),
        "number": lambda v: isinstance(v, (int, float))
        and not isinstance(v, bool),
        "bool": lambda v: isinstance(v, bool),
        "dict": lambda v: isinstance(v, dict),
        "list": lambda v: isinstance(v, list),
        "ie": lambda v: v in ELEMENTS,
        "tim": lambda v: v in TIMS,
        "quality": lambda v: v in ("confirmatory", "exploratory",
                                   "nonconfirmatory"),
        "study_mode": lambda v: v in ("confirmatory", "exploratory",
                                      "demonstration"),
    }[ty]
    if not ok(value):
        raise SchemaError("field %r: expected %s, got %r" % (name, ty, value))


def validate(schema_name, record):
    if schema_name not in SCHEMAS:
        raise SchemaError("unknown schema: %s" % schema_name)
    sch = SCHEMAS[schema_name]
    if not isinstance(record, dict):
        raise SchemaError("record must be an object")
    for k, ty in sch["required"].items():
        if k not in record:
            raise SchemaError("%s: missing required field %r"
                              % (schema_name, k))
        _check_type(k, record[k], ty)
    for k, ty in sch["optional"].items():
        if k in record and record[k] is not None:
            _check_type(k, record[k], ty)
    return True
