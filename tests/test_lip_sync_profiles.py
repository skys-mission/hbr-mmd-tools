# -*- coding: utf-8 -*-
import unittest

from src.core.lip_sync_profiles import (
    DEFAULT_LIP_SYNC_PRESET,
    LIP_SYNC_PRESETS,
    get_lip_sync_preset_values,
)


class LipSyncProfileTests(unittest.TestCase):
    def test_default_preset_exists(self):
        self.assertIn(DEFAULT_LIP_SYNC_PRESET, LIP_SYNC_PRESETS)

    def test_unknown_preset_falls_back_to_default(self):
        self.assertEqual(
            get_lip_sync_preset_values("unknown"),
            get_lip_sync_preset_values(DEFAULT_LIP_SYNC_PRESET),
        )

    def test_clear_preset_is_more_expressive_than_soft(self):
        clear_values = get_lip_sync_preset_values("clear")
        soft_values = get_lip_sync_preset_values("soft")
        self.assertGreater(clear_values["max_morph_value"], soft_values["max_morph_value"])
        self.assertGreater(clear_values["approach_speed"], soft_values["approach_speed"])

    def test_natural_preset_uses_lower_anticipation_than_clear(self):
        natural_values = get_lip_sync_preset_values("natural")
        clear_values = get_lip_sync_preset_values("clear")
        self.assertLess(natural_values["anticipation_scale"], clear_values["anticipation_scale"])


if __name__ == "__main__":
    unittest.main()
