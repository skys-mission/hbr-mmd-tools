# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
口型生成服务。
"""

from ..audio.lips import Lips
from ..core.config_manager import get_config_manager
from ..core.config_schema import CANONICAL_LIP_SYNC_KEYS
from .selection_service import (
    clear_shape_key_keyframes_in_range,
    find_selected_meshes_with_shape_keys,
)
from ..util.logger import Log


def load_lip_sync_config(selection):
    """加载已选口型配置。"""
    if not selection:
        raise ValueError("Please select a configuration")

    config = get_config_manager().load_config("lip_sync", selection)
    if not config:
        raise ValueError(f"Failed to load config: {selection}")
    return config


def generate_lip_sync(context):
    """执行口型生成。"""
    scene = context.scene
    fps = scene.render.fps
    config = load_lip_sync_config(scene.lips_config_selection)
    lips = Lips.mmd_lips_gen(
        wav_path=scene.lips_audio_path,
        buffer=scene.buffer_frame,
        approach_speed=scene.approach_speed,
        db_threshold=scene.db_threshold,
        rms_threshold=scene.rms_threshold,
        max_morph_value=scene.max_morph_value,
        start_frame=scene.lips_start_frame,
        fps=fps,
    )
    meshes = find_mesh_with_config(context, config)
    for mesh in meshes:
        set_lips_to_mesh_with_config(mesh, lips, scene.lips_start_frame, config)
    return {
        "config": config,
        "mesh_count": len(meshes),
        "lips": lips,
    }


def find_mesh_with_config(context, config):
    """根据配置查找包含指定形态键的对象。"""
    shape_keys = list(config.get("shape_keys", {}).values())
    found_objects = find_selected_meshes_with_shape_keys(context, shape_keys)
    if found_objects:
        Log.info(f"Found {len(found_objects)} objects containing configured shape keys")
        for obj in found_objects:
            Log.info(f"Object {obj.name} found with configured shape keys")
    return found_objects


def set_lips_to_mesh_with_config(mesh, lips, start_frame, config):  # pylint: disable=too-many-locals,too-many-branches
    """根据配置将 lips 数据应用到网格模型上。"""
    shape_key_mapping = config.get("shape_keys", {})
    adjustment_rules = config.get("adjustment_rules", {})
    config_morph_list = list(shape_key_mapping.values())

    max_frame = 0
    for _, morph_frames in lips.items():
        for morph_frame in morph_frames:
            max_frame = max(morph_frame["frame"], max_frame)

    start = max(start_frame, 1)
    end = max(max_frame, start_frame)
    existing_morphs = [
        key.name for key in mesh.data.shape_keys.key_blocks
    ] if mesh.data.shape_keys else []

    for morph_key in config_morph_list:
        if morph_key in existing_morphs:
            clear_shape_key_keyframes_in_range(mesh, morph_key, start, end)

    for source_key, target_morph_key in shape_key_mapping.items():
        if target_morph_key in existing_morphs:
            existing_frames = [item["frame"] for item in lips.get(source_key, [])]
            if start_frame not in existing_frames:
                set_shape_key_value(mesh, target_morph_key, 0.0, start_frame, "KEYFRAME")

    for source_key in CANONICAL_LIP_SYNC_KEYS:
        morph_frames = lips.get(source_key, [])
        target_morph_key = shape_key_mapping.get(source_key, source_key)
        if target_morph_key not in existing_morphs:
            Log.warning(f"Target shape key '{target_morph_key}' not found in mesh")
            continue

        adjustment_rule = adjustment_rules.get(source_key, {})
        priority = adjustment_rule.get("priority", 1.0)
        adjustment_factor = adjustment_rule.get("adjustment_factor", 1.0)
        valid_frames = (item for item in morph_frames if item["frame"] >= start_frame)

        for morph_frame in valid_frames:
            adjusted_value = _calculate_adjusted_value(
                mesh,
                morph_frame,
                config_morph_list,
                existing_morphs,
                target_morph_key,
                adjustment_factor,
                priority,
            )

            set_shape_key_value(
                obj=mesh,
                shape_key_name=target_morph_key,
                value=adjusted_value,
                frame=morph_frame["frame"],
                f_type=morph_frame["frame_type"],
            )
            Log.info(
                f"Set shape key '{target_morph_key}' "
                f"with frame {morph_frame['frame']} and value {adjusted_value}"
            )


def _calculate_adjusted_value(
    mesh,
    morph_frame,
    config_morph_list,
    existing_morphs,
    target_morph_key,
    adjustment_factor,
    priority,
):  # pylint: disable=too-many-arguments,too-many-positional-arguments
    if morph_frame["value"] <= 0:
        return 0

    sum_values = 0.0
    count = 0
    for morph in config_morph_list:
        if morph not in existing_morphs or morph == target_morph_key:
            continue
        current_val = get_shape_key_value_at_frame(
            mesh,
            morph,
            morph_frame["frame"],
        )
        if current_val is None:
            continue
        sum_values += current_val
        count += 1

    adjusted_value = morph_frame["value"]
    if count > 0:
        adjusted_value -= (sum_values / count) * adjustment_factor
        if count == 1:
            adjusted_value = morph_frame["value"] - (sum_values / count)

    adjusted_value *= priority
    adjusted_value = max(adjusted_value, 0.0)
    adjusted_value = min(adjusted_value, 0.99)
    return adjusted_value


def set_shape_key_value(obj, shape_key_name, value, frame, f_type):
    """设置指定对象的形态键值。"""
    if obj and obj.type == "MESH":  # pylint: disable=too-many-nested-blocks
        shape_keys = obj.data.shape_keys
        if shape_keys and shape_key_name in shape_keys.key_blocks:
            shape_key = shape_keys.key_blocks[shape_key_name]
            anim_data = shape_key.id_data.animation_data
            has_existing_key = False
            if anim_data and anim_data.action:
                for fcu in anim_data.action.fcurves:
                    if fcu.data_path == f'key_blocks["{shape_key.name}"].value':
                        for keyframe in fcu.keyframe_points:
                            if keyframe.co[0] == frame:
                                has_existing_key = True
            if round(shape_key.value, 1) == 0.0 and has_existing_key:
                return
            if f_type in ("buffer_start", "buffer_end"):
                shape_key.value = max(value, shape_key.value)
            else:
                shape_key.value = value
            shape_key.keyframe_insert(data_path="value", frame=frame)
        else:
            Log.warning(f"The shape key '{shape_key_name}' does not exist.")
    else:
        Log.warning("The object is not of the mesh type.")


def get_shape_key_value_at_frame(obj, shape_key_name, frame):
    """获取指定对象的形态键在特定帧的值。"""
    if obj and obj.type == "MESH":  # pylint: disable=too-many-nested-blocks
        shape_keys = obj.data.shape_keys
        if shape_keys and shape_key_name in shape_keys.key_blocks:
            anim_data = shape_keys.animation_data
            if anim_data and anim_data.action:
                for fcu in anim_data.action.fcurves:
                    if fcu.data_path == f'key_blocks["{shape_key_name}"].value':
                        for keyframe in fcu.keyframe_points:
                            if keyframe.co[0] == frame:
                                return keyframe.co[1]
                        return fcu.evaluate(frame)
            return shape_keys.key_blocks[shape_key_name].value
        Log.warning(f"The shape key '{shape_key_name}' does not exist.")
        return None
    Log.warning("The object is not of the mesh type.")
    return None
