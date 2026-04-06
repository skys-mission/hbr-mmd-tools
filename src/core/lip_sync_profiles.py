# -*- coding: utf-8 -*-
# Copyright (c) 2026, https://github.com/skys-mission and Half-Bottled Reverie
"""
Lip sync generation presets.
"""


DEFAULT_LIP_SYNC_PRESET = "natural"
LIP_SYNC_PRESETS = {
    "natural": {
        "buffer": 0.18,
        "approach_speed": 2.6,
        "db_threshold": -47.0,
        "rms_threshold": 0.035,
        "max_morph_value": 0.92,
        "anticipation_scale": 0.72,
    },
    "clear": {
        "buffer": 0.10,
        "approach_speed": 3.6,
        "db_threshold": -49.0,
        "rms_threshold": 0.025,
        "max_morph_value": 0.98,
        "anticipation_scale": 1.0,
    },
    "soft": {
        "buffer": 0.24,
        "approach_speed": 1.9,
        "db_threshold": -45.0,
        "rms_threshold": 0.045,
        "max_morph_value": 0.82,
        "anticipation_scale": 0.88,
    },
}


def get_lip_sync_preset_values(preset_name):
    """Return resolved preset values for lip sync generation."""
    if preset_name not in LIP_SYNC_PRESETS:
        preset_name = DEFAULT_LIP_SYNC_PRESET
    return dict(LIP_SYNC_PRESETS[preset_name])
