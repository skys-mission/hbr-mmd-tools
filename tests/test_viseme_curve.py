# -*- coding: utf-8 -*-
"""Tests for viseme curve helpers."""
import unittest

from src.audio.viseme_curve import (  # pylint: disable=import-error
    build_viseme_keyframes,
    compute_openness,
    score_visemes,
)


def _weights(**overrides):
    weights = {"a": 0.0, "i": 0.0, "u": 0.0, "e": 0.0, "o": 0.0, "n": 0.0}
    weights.update(overrides)
    return weights


class VisemeCurveTests(unittest.TestCase):
    """Regression tests for viseme curve generation."""

    def test_compute_openness_grows_with_energy(self):
        """Openness should increase with stronger audio energy."""
        quiet = compute_openness(-55.0, 0.01, -50.0, 0.05)
        loud = compute_openness(-18.0, 0.20, -50.0, 0.05)
        self.assertLess(quiet, loud)
        self.assertGreaterEqual(loud, 0.0)
        self.assertLessEqual(loud, 1.0)

    def test_score_visemes_prefers_matching_formant_prototype(self):
        """Formant prototypes should map to the expected dominant viseme."""
        a_weights = score_visemes(850.0, 1450.0)
        i_weights = score_visemes(320.0, 2250.0)
        self.assertEqual(max(a_weights, key=a_weights.get), "a")
        self.assertEqual(max(i_weights, key=i_weights.get), "i")

    def test_build_viseme_keyframes_keeps_soft_transition(self):
        """Keyframes should preserve a smooth transition between visemes."""
        samples = [
            {"time": 0.0, "openness": 0.0, "weights": _weights()},
            {"time": 0.04, "openness": 0.8, "weights": _weights(a=1.0)},
            {"time": 0.08, "openness": 0.85, "weights": _weights(a=0.2, i=0.8)},
            {"time": 0.12, "openness": 0.0, "weights": _weights()},
        ]

        keyframes = build_viseme_keyframes(samples, start_frame=1, fps=24, max_morph_value=1.0)
        a_values = [point for point in keyframes["a"] if point["value"] > 0.0]
        i_values = [point for point in keyframes["i"] if point["value"] > 0.0]

        self.assertTrue(a_values)
        self.assertTrue(i_values)
        self.assertLessEqual(i_values[0]["frame"], 2.92)
        self.assertEqual(keyframes["a"][0]["value"], 0.0)
        self.assertEqual(keyframes["i"][0]["value"], 0.0)


if __name__ == "__main__":
    unittest.main()
