# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
选中对象与形态键相关的公共服务。
"""

from ..util.logger import Log


def find_selected_meshes_with_shape_keys(context, shape_key_names):
    """在选中对象树范围内查找包含指定形态键的网格对象。"""
    selected_objects = context.selected_objects
    if not selected_objects:
        Log.raise_error("Please select an object first.", Exception)

    target_shape_keys = [name for name in shape_key_names if name]
    if not target_shape_keys:
        Log.raise_error("No target shape keys were provided.", Exception)

    found_objects = []
    seen = set()
    for obj in selected_objects:
        _collect_meshes_with_shape_keys(obj, target_shape_keys, found_objects, seen)

    if not found_objects:
        joined_shape_keys = ", ".join(target_shape_keys)
        Log.raise_error(
            f"No object containing configured shape keys was found: {joined_shape_keys}",
            Exception,
        )

    return found_objects


def clear_shape_key_keyframes_in_range(obj, shape_key_name, start_frame, end_frame):
    """清除指定对象在帧范围内的形态键关键帧。"""
    if not obj or obj.type != "MESH":
        return

    shape_keys = obj.data.shape_keys
    if not shape_keys or shape_key_name not in shape_keys.key_blocks:
        return

    shape_key = shape_keys.key_blocks[shape_key_name]
    for frame in range(start_frame, end_frame + 1):
        try:
            shape_key.keyframe_delete(data_path="value", frame=frame)
        except RuntimeError:
            pass


def _collect_meshes_with_shape_keys(obj, shape_key_names, found_objects, seen):
    if obj.type == "MESH" and obj.data.shape_keys:
        existing_shape_keys = {key.name for key in obj.data.shape_keys.key_blocks}
        if any(name in existing_shape_keys for name in shape_key_names):
            object_id = obj.as_pointer()
            if object_id not in seen:
                seen.add(object_id)
                found_objects.append(obj)

    for child in obj.children:
        _collect_meshes_with_shape_keys(child, shape_key_names, found_objects, seen)
