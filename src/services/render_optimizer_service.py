# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
MMD 渲染优化服务层。
组合调用各核心模块完成一键渲染优化。
"""

from ..core.render_optimizer.utils import (
    collect_objects_from_selection,
    find_primary_mesh,
    find_armature_for_meshes,
    calc_character_metrics,
    analyze_model_tone,
    cleanup_auto_objects,
)
from ..core.render_optimizer.material import enhance_materials
from ..core.render_optimizer.lighting import setup_lights
from ..core.render_optimizer.world_env import setup_world
from ..core.render_optimizer.compositor import setup_compositor, setup_render
from ..core.render_optimizer.outline import setup_outline
from ..core.render_optimizer.presets import ENGINE_EEVEE_ID, ENGINE_CYCLES_ID
from ..util.logger import Log


def apply_render_optimizer(context):
    """
    执行 MMD 渲染优化。
    根据当前场景属性自动配置材质、灯光、World、合成器和渲染参数。
    """
    scene = context.scene

    # 1. 收集目标对象
    meshes, armatures = collect_objects_from_selection(context)
    if not meshes:
        raise ValueError("No valid mesh found in the selected object tree.")

    primary_mesh = find_primary_mesh(meshes)
    arm = find_armature_for_meshes(meshes, armatures)

    # 2. 计算角色指标
    root_obj = context.active_object or meshes[0]
    H, fx, fy, fz, cz, es = calc_character_metrics(root_obj, arm, primary_mesh)

    # 3. 分析色调
    tone, brightness = analyze_model_tone(meshes)
    if scene.render_opt_brightness_override != 'AUTO':
        brightness = scene.render_opt_brightness_override.lower()

    # 4. 解析预设
    preset = scene.render_opt_preset
    is_pbr = preset in ('PBR', 'PBR_AGGRESSIVE')
    aggressive = preset == 'PBR_AGGRESSIVE'
    is_npr = preset == 'NPR'

    # 5. 清理旧对象
    cleanup_auto_objects()

    # 6. 材质优化（仅处理主 mesh，和 demo 一致）
    mat_stats = {'total': 0, 'classified': 0, 'fallback': 0}
    if is_pbr and primary_mesh:
        mat_stats = enhance_materials([primary_mesh], aggressive=aggressive)

    # 7. 灯光
    light_info = setup_lights(
        H, fx, fy, fz, cz, es,
        aggressive=aggressive,
        tone=tone,
    )

    # 8. World
    setup_world(
        brightness=brightness,
        tone=tone,
    )

    # 9. Compositor
    setup_compositor(
        aggressive=aggressive,
        enabled=scene.render_opt_use_compositor,
    )

    # 10. 描边
    outline_strategy = scene.render_opt_outline_strategy
    if is_npr and outline_strategy == 'freestyle_auto':
        pass  # 保持用户选择
    elif not is_npr and outline_strategy != 'none':
        outline_strategy = 'none'
    outline_info = setup_outline(
        primary_mesh,
        strategy=outline_strategy,
    )

    # 11. 渲染设置
    engine = ENGINE_EEVEE_ID if scene.render_opt_engine == 'EEVEE' else ENGINE_CYCLES_ID
    setup_render(engine=engine, aggressive=aggressive)

    # 12. 曝光自适应
    if brightness == 'light':
        scene.view_settings.exposure = -0.30 if aggressive else -0.25
    elif brightness == 'dark':
        scene.view_settings.exposure = 0.10 if aggressive else 0.15
    else:
        scene.view_settings.exposure = -0.05 if aggressive else 0.0

    Log.info(
        f"Render optimizer applied: preset={preset}, "
        f"materials={mat_stats['total']}, "
        f"classified={mat_stats['classified']}, "
        f"tone={tone}, brightness={brightness}"
    )

    return {
        'preset': preset,
        'mat_stats': mat_stats,
        'light_info': light_info,
        'outline_info': outline_info,
        'tone': tone,
        'brightness': brightness,
    }


def reset_render_optimizer():
    """
    重置渲染优化器创建的所有自动对象和设置。
    """
    import bpy  # pylint: disable=import-outside-toplevel,import-error

    scene = bpy.context.scene

    cleanup_auto_objects()

    # 关闭 Freestyle
    scene.render.use_freestyle = False
    vl = scene.view_layers[0]
    fs = vl.freestyle_settings
    while fs.linesets:
        fs.linesets.remove(fs.linesets[0])

    # 关闭 Compositor
    scene.use_nodes = False
    if scene.node_tree:
        scene.node_tree.nodes.clear()

    # 恢复默认 World
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    wnt = world.node_tree
    wnt.nodes.clear()
    out = wnt.nodes.new('ShaderNodeOutputWorld')
    out.location = (200, 0)
    bg = wnt.nodes.new('ShaderNodeBackground')
    bg.location = (0, 0)
    bg.inputs['Color'].default_value = (0.05, 0.05, 0.06, 1.0)
    bg.inputs['Strength'].default_value = 0.3
    wnt.links.new(bg.outputs['Background'], out.inputs['Surface'])

    # 恢复默认渲染设置
    scene.view_settings.exposure = 0.0
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'

    Log.info("Render optimizer reset completed.")
