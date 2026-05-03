# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
随机眨眼服务。
"""

import random

from ..core.config_manager import get_config_manager
from .selection_service import (
    clear_shape_key_keyframes_in_range,
    find_selected_meshes_with_shape_keys,
)


def load_blink_config(selection):
    """加载已选眨眼配置。"""
    if not selection:
        raise ValueError("Please select a configuration")

    config = get_config_manager().load_config("blink", selection)
    if not config:
        raise ValueError(f"Failed to load config: {selection}")
    return config


def generate_random_blink(context):
    """执行随机眨眼生成。"""
    scene = context.scene
    config = load_blink_config(scene.blink_config_selection)
    blink_data = generate_blink_frames(
        start_frame=scene.blink_start_frame,
        end_frame=scene.blink_end_frame,
        fps=scene.render.fps,
        interval_seconds=scene.blinking_frequency,
        wave_ratio=scene.blinking_wave_ratio,
        config=config,
    )
    meshes = find_mmd_meshes_with_config(context, config)
    for mesh in meshes:
        apply_blink_animation_with_config(
            mesh,
            blink_data,
            scene.blink_start_frame,
            scene.blink_end_frame,
            config,
        )
    blink_shape_key = config.get("shape_keys", {}).get("blink", "まばたき")
    return {
        "config": config,
        "mesh_count": len(meshes),
        "blink_shape_key": blink_shape_key,
        "keyframe_count": len(blink_data.get(blink_shape_key, [])),
    }


def generate_blink_frames(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    start_frame,
    end_frame,
    fps,
    interval_seconds,
    wave_ratio,
    config=None,
):
    """生成眨眼形态键动画帧序列。"""
    frames = {}
    current_time = start_frame / fps
    end_time = end_frame / fps
    blink_shape_key = config.get("shape_keys", {}).get("blink", "まばたき") if config else "まばたき"
    frames.setdefault(blink_shape_key, [])

    while current_time < end_time:
        ratio = random.uniform(1 - wave_ratio, 1 + wave_ratio)
        # 防止 wave_ratio 接近 1 时 ratio 触底导致零间隔死循环
        ratio = max(0.1, ratio)
        actual_interval = interval_seconds * ratio
        blink_time = current_time + actual_interval
        blink_frame = int(blink_time * fps)
        if blink_frame > end_frame:
            break
        frames.setdefault(blink_shape_key, []).extend([
            {"frame": blink_frame - 2, "value": 0.0},
            {"frame": blink_frame, "value": 1.0},
            {"frame": blink_frame + 2, "value": 0.0},
        ])
        current_time = blink_time

    frames[blink_shape_key].insert(0, {"frame": start_frame, "value": 0.0})
    frames[blink_shape_key].append({"frame": end_frame, "value": 0.0})

    return frames


def find_mmd_meshes_with_config(context, config):
    """根据配置查找包含指定眨眼形态键的网格对象。"""
    blink_shape_key = config.get("shape_keys", {}).get("blink", "まばたき") if config else "まばたき"
    meshes = find_selected_meshes_with_shape_keys(context, [blink_shape_key])
    return meshes


def apply_blink_animation_with_config(mesh, frames, start_frame, end_frame, config=None):
    """根据配置文件将眨眼动画应用到网格对象。"""
    blink_shape_key = config.get("shape_keys", {}).get("blink", "まばたき") if config else "まばたき"

    for shape_key_name, keyframes in frames.items():
        if shape_key_name != blink_shape_key:
            continue

        shape_key = None
        for key_block in mesh.data.shape_keys.key_blocks:
            if key_block.name == shape_key_name:
                shape_key = key_block
                break

        if not shape_key:
            continue

        clear_shape_key_keyframes_in_range(mesh, shape_key_name, start_frame, end_frame)

        for keyframe in keyframes:
            shape_key.value = keyframe["value"]
            shape_key.keyframe_insert(data_path="value", frame=keyframe["frame"])

        mesh.data.update_tag()
