# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
MMD Render Optimizer — World 环境。
渐变背景，颜色自适应。
"""

import bpy  # pylint: disable=import-error


def _build_gradient_nodes(wnt):
    """Create and return gradient, mapping, and tex_coord nodes."""
    grad_tex = wnt.nodes.new('ShaderNodeTexGradient')
    grad_tex.location = (-200, 0)
    grad_tex.gradient_type = 'LINEAR'

    mapping = wnt.nodes.new('ShaderNodeMapping')
    mapping.location = (-400, 0)
    mapping.inputs['Rotation'].default_value = (0, 0, 1.5708)

    tex_coord = wnt.nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)

    return grad_tex, mapping, tex_coord


def reset_world_default(scene, out_loc=(200, 0), bg_loc=(0, 0)):
    """Reset scene world to a simple dark default with nodes."""
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    wnt = world.node_tree
    wnt.nodes.clear()
    out = wnt.nodes.new('ShaderNodeOutputWorld')
    out.location = out_loc
    bg = wnt.nodes.new('ShaderNodeBackground')
    bg.location = bg_loc
    bg.inputs['Color'].default_value = (0.05, 0.05, 0.06, 1.0)
    bg.inputs['Strength'].default_value = 0.3
    wnt.links.new(bg.outputs['Background'], out.inputs['Surface'])


def _resolve_world_colors(brightness, tone):
    """Return (world_top, world_bottom, world_strength) based on brightness and tone."""
    if brightness == 'light':
        world_top = (0.02, 0.02, 0.025, 1.0)
        world_bottom = (0.10, 0.10, 0.12, 1.0)
        world_strength = 0.5
    elif brightness == 'dark':
        world_top = (0.008, 0.008, 0.012, 1.0)
        world_bottom = (0.05, 0.05, 0.06, 1.0)
        world_strength = 0.4
    else:
        world_top = (0.015, 0.015, 0.02, 1.0)
        world_bottom = (0.08, 0.08, 0.10, 1.0)
        world_strength = 0.45

    if tone == 'cool':
        world_top = (
            world_top[0] * 0.9, world_top[1] * 0.95, world_top[2] * 1.1, 1.0,
        )
        world_bottom = (
            world_bottom[0] * 0.9, world_bottom[1] * 0.95, world_bottom[2] * 1.1, 1.0,
        )
    elif tone == 'warm':
        world_top = (
            world_top[0] * 1.1, world_top[1] * 1.05, world_top[2] * 0.9, 1.0,
        )
        world_bottom = (
            world_bottom[0] * 1.1, world_bottom[1] * 1.05, world_bottom[2] * 0.9, 1.0,
        )

    return world_top, world_bottom, world_strength


def setup_world(brightness='medium', tone='neutral', enabled=True):
    """
    设置 World 渐变背景。

    参数:
        brightness: 'light' / 'medium' / 'dark'
        tone: 'cool' / 'warm' / 'neutral'
        enabled: False 时恢复为简单深色背景
    """
    scene = bpy.context.scene
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    wnt = world.node_tree
    wnt.nodes.clear()

    out = wnt.nodes.new('ShaderNodeOutputWorld')
    out.location = (600, 0)

    bg = wnt.nodes.new('ShaderNodeBackground')
    bg.location = (400, 0)

    if not enabled:
        reset_world_default(scene, out_loc=(600, 0), bg_loc=(400, 0))
        return

    grad_tex, mapping, tex_coord = _build_gradient_nodes(wnt)

    color_ramp = wnt.nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (0, 0)

    world_top, world_bottom, world_strength = _resolve_world_colors(brightness, tone)

    color_ramp.color_ramp.elements[0].position = 0.0
    color_ramp.color_ramp.elements[0].color = world_bottom
    color_ramp.color_ramp.elements[1].position = 1.0
    color_ramp.color_ramp.elements[1].color = world_top

    wnt.links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    wnt.links.new(mapping.outputs['Vector'], grad_tex.inputs['Vector'])
    wnt.links.new(grad_tex.outputs['Color'], color_ramp.inputs['Fac'])
    wnt.links.new(color_ramp.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = world_strength
    wnt.links.new(bg.outputs['Background'], out.inputs['Surface'])
