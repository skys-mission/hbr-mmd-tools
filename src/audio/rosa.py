# pylint: skip-file
# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and Half-Bottled Reverie
"""
Audio analysis for lip sync generation.
"""
import os
import sys
import bpy  # pylint: disable=import-error
from ..core.compat import get_bundled_python_lib_path
from .viseme_curve import compute_openness, score_visemes, zero_weights

def load_pkg():
    """
    ...
    """
    addon_dir = os.path.abspath(os.path.dirname(__file__))
    _ = bpy.app.version
    plib_path = get_bundled_python_lib_path(addon_dir)
    if plib_path not in sys.path:
        sys.path.append(plib_path)

load_pkg()

import librosa
import numpy as np


# 加载音频文件
def load_audio(file_path):
    """
    ...
    """
    y, sr = librosa.load(file_path, sr=16000)  # 加载音频（采样率 16kHz）
    return y, sr


def _estimate_formants(frame, sr):
    spectrum = np.abs(np.fft.rfft(frame)) ** 2
    freqs = np.fft.rfftfreq(len(frame), 1 / sr)

    valid_mask = (freqs >= 180.0) & (freqs <= 3200.0)
    if not np.any(valid_mask):
        return None, None

    valid_spectrum = spectrum[valid_mask]
    valid_freqs = freqs[valid_mask]
    if not len(valid_spectrum):
        return None, None

    peak_count = min(12, len(valid_spectrum))
    peak_indexes = np.argpartition(valid_spectrum, -peak_count)[-peak_count:]
    ranked_indexes = peak_indexes[np.argsort(valid_spectrum[peak_indexes])[::-1]]

    f1 = None
    f2 = None
    for index in ranked_indexes:
        frequency = float(valid_freqs[index])
        if f1 is None and 180.0 <= frequency <= 1100.0:
            f1 = frequency
            continue
        if f1 is not None and frequency >= max(700.0, f1 + 120.0):
            f2 = frequency
            break

    if f1 is not None and f2 is not None:
        return f1, f2

    fallback_freqs = sorted(float(valid_freqs[index]) for index in ranked_indexes[:2])
    if len(fallback_freqs) == 2:
        return fallback_freqs[0], fallback_freqs[1]
    return None, None


def rosa(audio_path, db_threshold=-50, rms_threshold=0.01):
    y, sr = load_audio(audio_path)
    frame_length = 1024
    hop_length = 160
    if len(y) < frame_length:
        y = np.pad(y, (0, frame_length - len(y)))
    frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)
    window = np.hanning(frame_length)

    results = []
    for index, frame in enumerate(frames.T):
        windowed = frame * window
        frame_rms = float(np.sqrt(np.mean(windowed ** 2)))
        frame_db = float(20 * np.log10(frame_rms + 1e-10))
        openness = compute_openness(frame_db, frame_rms, db_threshold, rms_threshold)
        timestamp = round(((index * hop_length) + (frame_length / 2.0)) / sr, 4)

        weights = zero_weights()
        if openness > 1e-3:
            f1, f2 = _estimate_formants(windowed, sr)
            weights = score_visemes(f1, f2)

        results.append({
            "time": timestamp,
            "openness": round(openness, 4),
            "weights": weights,
        })

    if os.path.exists(audio_path):
        try:
            os.remove(audio_path)
        except Exception as e:
            print(f"删除临时文件 {audio_path} 时出错: {e}")
    return results
