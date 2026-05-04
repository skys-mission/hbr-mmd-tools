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
    """
    生成自然眨眼形态键动画帧序列。

    特性:
    - 正态分布的眨眼间隔
    - 支持双眨眼 (double blink)
    - 支持半眨眼 (half blink)
    - 闭眼快、睁眼慢的不对称曲线
    """
    frames = {}
    blink_shape_key = (
        config.get("shape_keys", {}).get("blink", "まばたき")
        if config else "まばたき"
    )

    current_time = start_frame / fps
    end_time = end_frame / fps
    std_dev = interval_seconds * max(0.01, wave_ratio) / 2.5

    all_blinks = []  # (time_seconds, is_double_follow_up)

    while current_time < end_time:
        next_interval = random.gauss(interval_seconds, std_dev)
        next_interval = max(0.3, next_interval)
        blink_time = current_time + next_interval

        if blink_time >= end_time:
            break

        all_blinks.append((blink_time, False))
        current_time = blink_time

        # double blink: 约 10% 概率，第二次在 0.15-0.30 秒后
        if random.random() < 0.10 and current_time + 0.30 < end_time:
            double_time = current_time + random.uniform(0.15, 0.30)
            if double_time < end_time:
                all_blinks.append((double_time, True))
                current_time = double_time

    for blink_time, is_double in all_blinks:
        blink_frame = int(round(blink_time * fps))

        # 半眨眼概率: 正常 15%，双眨眼的第二次 30%
        half_chance = 0.30 if is_double else 0.15
        is_half = random.random() < half_chance
        peak_value = random.uniform(0.25, 0.55) if is_half else 1.0

        # 双眨眼的第二次通常更快更短
        if is_double:
            duration = random.uniform(0.18, 0.28)
            close_ratio = random.uniform(0.30, 0.45)
            hold_ratio = random.uniform(0.05, 0.15)
        else:
            duration = random.uniform(0.28, 0.48)
            close_ratio = random.uniform(0.25, 0.40)
            hold_ratio = random.uniform(0.10, 0.25)

        open_ratio = max(0.0, 1.0 - close_ratio - hold_ratio)

        close_dur = duration * close_ratio
        hold_dur = duration * hold_ratio
        open_dur = duration * open_ratio

        close_frames = max(1, int(round(close_dur * fps)))
        hold_frames = max(0, int(round(hold_dur * fps)))
        open_frames = max(1, int(round(open_dur * fps)))

        # 确保至少有关闭和睁开
        close_frames = max(close_frames, 1)
        open_frames = max(open_frames, 1)

        keyframes = []

        # 起点 (眼睛全开)
        keyframes.append({"frame": blink_frame - close_frames, "value": 0.0})

        # 闭眼中间过渡 (如果关闭阶段 >= 2 帧)
        if close_frames >= 2:
            mid_close = blink_frame - close_frames // 2
            keyframes.append({"frame": mid_close, "value": peak_value * 0.5})

        # 峰值 (全闭或半闭)
        keyframes.append({"frame": blink_frame, "value": peak_value})

        # 停留 (如果 hold_frames >= 1)
        if hold_frames >= 1:
            keyframes.append({"frame": blink_frame + hold_frames, "value": peak_value})

        # 睁眼中间过渡 (如果睁开阶段 >= 3 帧)
        if open_frames >= 3:
            mid_open = blink_frame + hold_frames + open_frames // 2
            keyframes.append({"frame": mid_open, "value": peak_value * 0.3})

        # 终点 (眼睛全开)
        keyframes.append(
            {"frame": blink_frame + hold_frames + open_frames, "value": 0.0}
        )

        frames.setdefault(blink_shape_key, []).extend(keyframes)

    # 去重并按帧排序
    def _dedup_sort(frame_list):
        seen = set()
        unique = []
        for kf in sorted(frame_list, key=lambda x: x["frame"]):
            fk = kf["frame"]
            if fk not in seen:
                seen.add(fk)
                unique.append(kf)
        return unique

    if blink_shape_key in frames:
        frames[blink_shape_key] = _dedup_sort(frames[blink_shape_key])

    # 插入起始和结束帧
    frames.setdefault(blink_shape_key, []).insert(0, {"frame": start_frame, "value": 0.0})
    frames.setdefault(blink_shape_key, []).append({"frame": end_frame, "value": 0.0})

    if blink_shape_key in frames:
        frames[blink_shape_key] = _dedup_sort(frames[blink_shape_key])

    return frames


def find_mmd_meshes_with_config(context, config):
    """根据配置查找包含指定眨眼形态键的网格对象。"""
    blink_shape_key = (
        config.get("shape_keys", {}).get("blink", "まばたき")
        if config else "まばたき"
    )
    meshes = find_selected_meshes_with_shape_keys(context, [blink_shape_key])
    return meshes


def apply_blink_animation_with_config(mesh, frames, start_frame, end_frame, config=None):
    """根据配置文件将眨眼动画应用到网格对象。"""
    blink_shape_key = (
        config.get("shape_keys", {}).get("blink", "まばたき")
        if config else "まばたき"
    )

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

        # 设置关键帧 handle 类型使曲线更自然
        _set_keyframe_handles(mesh, shape_key_name)

        mesh.data.update_tag()


def _set_keyframe_handles(mesh, shape_key_name):
    """设置眨眼关键帧的 handle 类型为 AUTO_CLAMPED，使贝塞尔曲线更圆润。"""
    shape_keys = mesh.data.shape_keys
    if not shape_keys or not shape_keys.animation_data or not shape_keys.animation_data.action:
        return

    data_path = f'key_blocks["{shape_key_name}"].value'
    for fcurve in shape_keys.animation_data.action.fcurves:
        if fcurve.data_path != data_path:
            continue
        for kp in fcurve.keyframe_points:
            kp.handle_left_type = "AUTO_CLAMPED"
            kp.handle_right_type = "AUTO_CLAMPED"
            kp.interpolation = "BEZIER"
        break
