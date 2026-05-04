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


def setup_lights(H, fx, fy, fz, cz, es, aggressive=False, tone='neutral'):
    """
    创建6点自适应布光。不创建相机和地面。

    参数:
        H: 角色参考高度
        fx, fy, fz: 焦点位置（角色头部区域）
        cz: 角色底部 z 坐标
        es: 灯光能量缩放系数
        aggressive: 激进模式增强对比
        tone: 'cool' / 'warm' / 'neutral'
    """
    scene = bpy.context.scene

    # 色温自适应
    if tone == 'cool':
        key_color = (0.88, 0.92, 1.0)
    elif tone == 'warm':
        key_color = (1.0, 0.95, 0.88)
    else:
        key_color = LIGHT_KEY_COLOR

    # aggressive 模式能量调整
    key_mul = 1.45 if aggressive else 1.0
    fill_mul = 0.65 if aggressive else 1.0
    rim_mul = 2.0 if aggressive else 1.3
    hair_mul = 1.4 if aggressive else 1.0
    back_mul = 1.2 if aggressive else 1.0
    front_mul = 1.1 if aggressive else 1.0

    def add_light(name, loc, energy, color, sx, sy):
        ld = bpy.data.lights.new(name, 'AREA')
        ld.shape = 'RECTANGLE'
        ld.size = sx
        ld.size_y = sy
        ld.energy = energy * es
        ld.color = color
        obj = bpy.data.objects.new(name, ld)
        obj.location = loc
        scene.collection.objects.link(obj)
        return obj

    # Key: 主光，暖白
    key = add_light(
        'AutoKey',
        (fx + H * 1.4, fy - H * 1.2, cz + H * 1.55),
        LIGHT_KEY_ENERGY * key_mul,
        key_color,
        H * 1.4, H * 1.4,
    )

    # Fill: 补光，冷蓝（aggressive 降低以增加对比）
    add_light(
        'AutoFill',
        (fx - H * 1.5, fy - H * 1.0, cz + H * 0.85),
        LIGHT_FILL_ENERGY * fill_mul,
        LIGHT_FILL_COLOR,
        H * 2.0, H * 2.0,
    )

    # Rim: 轮廓光，暖橙
    add_light(
        'AutoRim',
        (fx - H * 1.1, fy + H * 1.6, cz + H * 0.50),
        LIGHT_RIM_ENERGY * rim_mul,
        LIGHT_RIM_COLOR,
        H * 0.5, H * 1.4,
    )

    # Hair: 顶光
    add_light(
        'AutoHair',
        (fx + H * 0.3, fy + H * 0.2, cz + H * 1.80),
        LIGHT_HAIR_ENERGY * hair_mul,
        LIGHT_HAIR_COLOR,
        H * 0.6, H * 0.6,
    )

    # Back: 背景光
    add_light(
        'AutoBack',
        (fx, fy + H * 2.5, cz + H * 0.3),
        LIGHT_BACK_ENERGY * back_mul,
        LIGHT_BACK_COLOR,
        H * 3.0, H * 3.0,
    )

    # Front: 正面弱补光
    add_light(
        'AutoFront',
        (fx + H * 0.35, fy - H * 1.0, fz + H * 0.05),
        LIGHT_FRONT_ENERGY * front_mul,
        LIGHT_FRONT_COLOR,
        H * 1.2, H * 1.2,
    )

    # 让 Key 灯指向角色中心
    key.rotation_euler = (1.2, 0.0, 0.3)

    return {
        'key': key_mul, 'fill': fill_mul, 'rim': rim_mul,
        'hair': hair_mul, 'back': back_mul, 'front': front_mul,
        'tone': tone,
    }
