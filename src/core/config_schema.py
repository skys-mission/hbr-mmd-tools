# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
配置文件 schema 与校验。
"""


SUPPORTED_CONFIG_TYPES = {"lip_sync", "blink"}
CANONICAL_LIP_SYNC_KEYS = ("a", "i", "u", "e", "o", "n")
LIP_SYNC_KEY_ALIASES = {
    "a": "a",
    "A": "a",
    "あ": "a",
    "i": "i",
    "I": "i",
    "い": "i",
    "u": "u",
    "U": "u",
    "う": "u",
    "e": "e",
    "E": "e",
    "え": "e",
    "o": "o",
    "O": "o",
    "お": "o",
    "n": "n",
    "N": "n",
    "ん": "n",
}


class ConfigValidationError(ValueError):
    """配置校验异常。"""


def validate_config(config_type, config_data):
    """校验并返回标准化后的配置数据。"""
    if config_type not in SUPPORTED_CONFIG_TYPES:
        raise ConfigValidationError(f"Unsupported config type: {config_type}")
    if not isinstance(config_data, dict):
        raise ConfigValidationError("Config data must be a JSON object")

    allowed_fields = {"name", "description", "version", "author", "type", "shape_keys"}
    if config_type == "lip_sync":
        allowed_fields.add("adjustment_rules")
    if config_type == "blink":
        allowed_fields.add("parameters")

    unknown_fields = sorted(set(config_data.keys()) - allowed_fields)
    if unknown_fields:
        raise ConfigValidationError(
            f"Unknown fields in {config_type} config: {', '.join(unknown_fields)}"
        )

    normalized = {
        "name": _require_non_empty_string(config_data.get("name"), "name"),
        "description": _require_non_empty_string(
            config_data.get("description"),
            "description",
        ),
        "version": _require_non_empty_string(config_data.get("version"), "version"),
        "type": config_type,
        "shape_keys": _validate_shape_keys(config_type, config_data.get("shape_keys")),
    }

    if "author" in config_data:
        normalized["author"] = _require_non_empty_string(config_data.get("author"), "author")

    raw_type = config_data.get("type")
    if raw_type is not None and raw_type != config_type:
        raise ConfigValidationError(
            f"Config field 'type' must be '{config_type}', got '{raw_type}'"
        )

    if config_type == "lip_sync":
        normalized["adjustment_rules"] = _validate_adjustment_rules(
            config_type,
            config_data.get("adjustment_rules", {})
        )
    if config_type == "blink" and "parameters" in config_data:
        normalized["parameters"] = _validate_blink_parameters(config_data.get("parameters"))

    return normalized


def _require_non_empty_string(value, field_name):
    if not isinstance(value, str) or not value.strip():
        raise ConfigValidationError(f"Field '{field_name}' must be a non-empty string")
    return value.strip()


def _validate_shape_keys(config_type, shape_keys):
    if not isinstance(shape_keys, dict) or not shape_keys:
        raise ConfigValidationError("Field 'shape_keys' must be a non-empty object")

    normalized = {}
    for source_key, target_key in shape_keys.items():
        normalized_key = _require_non_empty_string(source_key, "shape_keys key")
        if config_type == "lip_sync":
            normalized_key = _normalize_lip_sync_key(normalized_key, "shape_keys key")
        normalized_value = _require_non_empty_string(target_key, f"shape_keys.{normalized_key}")
        if normalized_key in normalized and normalized[normalized_key] != normalized_value:
            raise ConfigValidationError(
                f"Duplicate canonical key in shape_keys: {normalized_key}"
            )
        normalized[normalized_key] = normalized_value

    if config_type == "blink":
        if "blink" not in normalized:
            raise ConfigValidationError("Blink config must define shape_keys.blink")
        if set(normalized.keys()) != {"blink"}:
            raise ConfigValidationError("Blink config only supports shape_keys.blink")

    return normalized


def _validate_adjustment_rules(config_type, adjustment_rules):
    if adjustment_rules is None:
        return {}
    if not isinstance(adjustment_rules, dict):
        raise ConfigValidationError("Field 'adjustment_rules' must be an object")

    normalized = {}
    for rule_name, rule in adjustment_rules.items():
        normalized_name = _require_non_empty_string(rule_name, "adjustment_rules key")
        if config_type == "lip_sync":
            normalized_name = _normalize_lip_sync_key(
                normalized_name,
                "adjustment_rules key",
            )
        if not isinstance(rule, dict):
            raise ConfigValidationError(
                f"Field 'adjustment_rules.{normalized_name}' must be an object"
            )

        normalized_rule = {}
        if "priority" in rule:
            normalized_rule["priority"] = _validate_number(
                rule["priority"],
                f"adjustment_rules.{normalized_name}.priority",
                minimum=0.0,
            )
        if "adjustment_factor" in rule:
            normalized_rule["adjustment_factor"] = _validate_number(
                rule["adjustment_factor"],
                f"adjustment_rules.{normalized_name}.adjustment_factor",
                minimum=0.0,
            )

        unknown_fields = sorted(set(rule.keys()) - {"priority", "adjustment_factor"})
        if unknown_fields:
            raise ConfigValidationError(
                f"Unknown fields in adjustment_rules.{normalized_name}: {', '.join(unknown_fields)}"
            )

        if normalized_name in normalized and normalized[normalized_name] != normalized_rule:
            raise ConfigValidationError(
                f"Duplicate canonical key in adjustment_rules: {normalized_name}"
            )
        normalized[normalized_name] = normalized_rule

    return normalized


def _validate_blink_parameters(parameters):
    if not isinstance(parameters, dict):
        raise ConfigValidationError("Field 'parameters' must be an object")

    normalized = {}
    if "default_interval_seconds" in parameters:
        normalized["default_interval_seconds"] = _validate_number(
            parameters["default_interval_seconds"],
            "parameters.default_interval_seconds",
            minimum=0.0,
        )
    if "default_wave_ratio" in parameters:
        normalized["default_wave_ratio"] = _validate_number(
            parameters["default_wave_ratio"],
            "parameters.default_wave_ratio",
            minimum=0.0,
            maximum=1.0,
        )

    unknown_fields = sorted(
        set(parameters.keys()) - {"default_interval_seconds", "default_wave_ratio"}
    )
    if unknown_fields:
        raise ConfigValidationError(
            f"Unknown fields in parameters: {', '.join(unknown_fields)}"
        )

    return normalized


def _validate_number(value, field_name, minimum=None, maximum=None):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ConfigValidationError(f"Field '{field_name}' must be a number")

    normalized = float(value)
    if minimum is not None and normalized < minimum:
        raise ConfigValidationError(f"Field '{field_name}' must be >= {minimum}")
    if maximum is not None and normalized > maximum:
        raise ConfigValidationError(f"Field '{field_name}' must be <= {maximum}")

    return normalized


def _normalize_lip_sync_key(value, field_name):
    normalized = LIP_SYNC_KEY_ALIASES.get(value)
    if normalized is None:
        raise ConfigValidationError(
            f"Unsupported lip sync key '{value}' in field '{field_name}'"
        )
    return normalized
