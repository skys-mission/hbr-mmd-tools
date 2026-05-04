# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
MMD Render Optimizer — 合成器后期。
bloom + 暗角 + 对比度（激进模式 + 饱和度 + 锐化）。
"""

import bpy  # pylint: disable=import-error

from .presets import (
    BLOOM_STRENGTH, BLOOM_THRESHOLD, VIGNETTE_EDGE,
    TAA_SAMPLES, TAA_SAMPLES_AGGRESSIVE,
    CYCLES_SAMPLES, CYCLES_SAMPLES_AGGRESSIVE,
    ENGINE_EEVEE_ID, ENGINE_CYCLES_ID,
)


def _build_vignette(nt, aggressive):
    """Create vignette mask and return the mask_ramp node."""
    mask = nt.nodes.new('CompositorNodeEllipseMask')
    mask.location = (-600, -300)
    mask.inputs['Size'].default_value = (0.58, 0.58)
    mask.inputs['Value'].default_value = 0.30

    vignette_val = 0.15 if aggressive else VIGNETTE_EDGE
    mask_ramp = nt.nodes.new('CompositorNodeValToRGB')
    mask_ramp.location = (-400, -300)
    mask_ramp.color_ramp.elements[0].position = 0.0
    mask_ramp.color_ramp.elements[0].color = (vignette_val, vignette_val, vignette_val, 1.0)
    mask_ramp.color_ramp.elements[1].position = 1.0
    mask_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(mask.outputs['Mask'], mask_ramp.inputs['Fac'])
    return mask_ramp


def setup_compositor(aggressive=False, enabled=True):
    """
    设置 Compositor 后期节点树。

    参数:
        aggressive: 激进模式（更强效果）
        enabled: False 时关闭 Compositor
    """
    scene = bpy.context.scene

    if not enabled:
        scene.use_nodes = False
        return

    scene.use_nodes = True
    nt = scene.node_tree
    nt.nodes.clear()

    rl = nt.nodes.new('CompositorNodeRLayers')
    rl.location = (-900, 0)

    # 基础对比度调整
    bright = nt.nodes.new('CompositorNodeBrightContrast')
    bright.location = (-600, 200)
    bright.inputs['Bright'].default_value = 0.02 if aggressive else 0.03
    bright.inputs['Contrast'].default_value = 0.38 if aggressive else 0.20

    # Bloom
    glare = nt.nodes.new('CompositorNodeGlare')
    glare.location = (-300, 0)
    glare.glare_type = 'BLOOM'
    glare.quality = 'HIGH'
    glare.inputs['Threshold'].default_value = 2.2 if aggressive else BLOOM_THRESHOLD
    glare.inputs['Size'].default_value = 7.0 if aggressive else 6.0
    glare.inputs['Strength'].default_value = 0.10 if aggressive else BLOOM_STRENGTH

    # 饱和度（仅激进模式）
    sat = None
    if aggressive:
        sat = nt.nodes.new('CompositorNodeHueSat')
        sat.location = (0, 0)
        sat.inputs['Saturation'].default_value = 1.12

    # 锐化（仅激进模式）
    sharp = None
    if aggressive:
        sharp = nt.nodes.new('CompositorNodeFilter')
        sharp.location = (200, 0)
        sharp.filter_type = 'SHARPEN'

    # 暗角
    mask_ramp = _build_vignette(nt, aggressive)

    # 混合暗角
    mix_v = nt.nodes.new('CompositorNodeMixRGB')
    mix_v.location = (600 if aggressive else 400, 0)
    mix_v.blend_type = 'MULTIPLY'
    mix_v.inputs['Fac'].default_value = 1.0

    # 节点连接
    nt.links.new(rl.outputs['Image'], bright.inputs['Image'])
    nt.links.new(bright.outputs['Image'], glare.inputs['Image'])

    last = glare
    if aggressive and sat:
        nt.links.new(last.outputs['Image'], sat.inputs['Image'])
        last = sat
    if aggressive and sharp:
        nt.links.new(last.outputs['Image'], sharp.inputs['Image'])
        last = sharp

    nt.links.new(last.outputs['Image'], mix_v.inputs[1])
    nt.links.new(mask_ramp.outputs['Image'], mix_v.inputs[2])

    comp = nt.nodes.new('CompositorNodeComposite')
    comp.location = (900 if aggressive else 700, 0)
    nt.links.new(mix_v.outputs['Image'], comp.inputs['Image'])


def setup_render(engine=ENGINE_EEVEE_ID, aggressive=False):
    """
    设置渲染参数（不含相机）。

    参数:
        engine: 'BLENDER_EEVEE_NEXT' 或 'CYCLES'
        aggressive: 激进模式提升采样
    """
    scene = bpy.context.scene
    r = scene.render
    r.engine = engine
    r.film_transparent = False

    if engine == ENGINE_CYCLES_ID:
        scene.cycles.samples = (
            CYCLES_SAMPLES_AGGRESSIVE if aggressive else CYCLES_SAMPLES
        )
        scene.cycles.use_denoising = True
    else:
        e = scene.eevee
        e.taa_render_samples = (
            TAA_SAMPLES_AGGRESSIVE if aggressive else TAA_SAMPLES
        )
        e.use_raytracing = True
        e.use_shadows = True
        e.shadow_resolution_scale = 1.0
        e.use_gtao = True
        e.gtao_distance = 0.4
        e.gtao_quality = 0.5
        e.use_fast_gi = True

    v = scene.view_settings
    v.view_transform = 'AgX'
    v.look = 'AgX - Medium High Contrast'
    v.gamma = 1.0
