# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
MMD Render Optimizer — 灯光系统。
6点自适应布光（Key / Fill / Rim / Hair / Back / Front）。
"""

import bpy  # pylint: disable=import-error

from .presets import (
    LIGHT_KEY_ENERGY, LIGHT_FILL_ENERGY, LIGHT_RIM_ENERGY,
    LIGHT_HAIR_ENERGY, LIGHT_BACK_ENERGY, LIGHT_FRONT_ENERGY,
    LIGHT_KEY_COLOR, LIGHT_FILL_COLOR, LIGHT_RIM_COLOR,
    LIGHT_HAIR_COLOR, LIGHT_BACK_COLOR, LIGHT_FRONT_COLOR,
)


def _resolve_key_color(tone):
    """根据色调解析主光颜色。"""
    if tone == 'cool':
        return (0.88, 0.92, 1.0)
    if tone == 'warm':
        return (1.0, 0.95, 0.88)
    return LIGHT_KEY_COLOR


def _resolve_light_multipliers(aggressive):
    """返回 aggressive 模式下的灯光能量倍数。"""
    return {
        'key': 1.45 if aggressive else 1.0,
        'fill': 0.65 if aggressive else 1.0,
        'rim': 2.0 if aggressive else 1.3,
        'hair': 1.4 if aggressive else 1.0,
        'back': 1.2 if aggressive else 1.0,
        'front': 1.1 if aggressive else 1.0,
    }


def _create_area_light(scene, name, spec):
    """创建 AREA 灯光并添加到场景。spec: (loc, energy, color, (sx, sy))"""
    loc, energy, color, size = spec
    sx, sy = size
    ld = bpy.data.lights.new(name, 'AREA')
    ld.shape = 'RECTANGLE'
    ld.size = sx
    ld.size_y = sy
    ld.energy = energy
    ld.color = color
    obj = bpy.data.objects.new(name, ld)
    obj.location = loc
    scene.collection.objects.link(obj)
    return obj


def setup_lights(metrics, *, aggressive=False, tone='neutral'):
    """
    创建6点自适应布光。不创建相机和地面。

    参数:
        metrics: (height, fx, fy, fz, cz, es)
        aggressive: 激进模式增强对比
        tone: 'cool' / 'warm' / 'neutral'
    """
    height, fx, fy, fz, cz, es = metrics
    scene = bpy.context.scene
    key_color = _resolve_key_color(tone)
    muls = _resolve_light_multipliers(aggressive)

    key = _create_area_light(
        scene, 'AutoKey',
        ((fx + height * 1.4, fy - height * 1.2, cz + height * 1.55),
         LIGHT_KEY_ENERGY * muls['key'] * es,
         key_color,
         (height * 1.4, height * 1.4)),
    )

    _create_area_light(
        scene, 'AutoFill',
        ((fx - height * 1.5, fy - height * 1.0, cz + height * 0.85),
         LIGHT_FILL_ENERGY * muls['fill'] * es,
         LIGHT_FILL_COLOR,
         (height * 2.0, height * 2.0)),
    )

    _create_area_light(
        scene, 'AutoRim',
        ((fx - height * 1.1, fy + height * 1.6, cz + height * 0.50),
         LIGHT_RIM_ENERGY * muls['rim'] * es,
         LIGHT_RIM_COLOR,
         (height * 0.5, height * 1.4)),
    )

    _create_area_light(
        scene, 'AutoHair',
        ((fx + height * 0.3, fy + height * 0.2, cz + height * 1.80),
         LIGHT_HAIR_ENERGY * muls['hair'] * es,
         LIGHT_HAIR_COLOR,
         (height * 0.6, height * 0.6)),
    )

    _create_area_light(
        scene, 'AutoBack',
        ((fx, fy + height * 2.5, cz + height * 0.3),
         LIGHT_BACK_ENERGY * muls['back'] * es,
         LIGHT_BACK_COLOR,
         (height * 3.0, height * 3.0)),
    )

    _create_area_light(
        scene, 'AutoFront',
        ((fx + height * 0.35, fy - height * 1.0, fz + height * 0.05),
         LIGHT_FRONT_ENERGY * muls['front'] * es,
         LIGHT_FRONT_COLOR,
         (height * 1.2, height * 1.2)),
    )

    key.rotation_euler = (1.2, 0.0, 0.3)

    return {**muls, 'tone': tone}
