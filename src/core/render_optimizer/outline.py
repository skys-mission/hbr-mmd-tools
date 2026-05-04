# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
MMD Render Optimizer — NPR 描边。
支持多种描边预设策略。
"""

import bpy  # pylint: disable=import-error

from .utils import check_mesh_topology


OUTLINE_STRATEGIES = {
    'none': 'No outline',
    'freestyle_silhouette': 'Freestyle Silhouette Only',
    'freestyle_auto': 'Freestyle Auto (Topology-aware)',
}


def setup_outline(mesh, strategy='freestyle_auto'):
    """
    根据策略设置描边。

    参数:
        mesh: 主 mesh 对象
        strategy: 'none' / 'freestyle_silhouette' / 'freestyle_auto'

    返回:
        dict 包含 enabled, strategy, quality, topo_info 等信息
    """
    scene = bpy.context.scene

    if strategy == 'none' or not mesh:
        disable_freestyle(scene)
        return {'enabled': False, 'strategy': 'none'}

    if strategy in ('freestyle_silhouette', 'freestyle_auto'):
        return _setup_freestyle(scene, mesh, strategy)

    disable_freestyle(scene)
    return {'enabled': False, 'strategy': 'none'}


def disable_freestyle(scene):
    """关闭 Freestyle。"""
    scene.render.use_freestyle = False
    vl = scene.view_layers[0]
    fs = vl.freestyle_settings
    while fs.linesets:
        fs.linesets.remove(fs.linesets[0])


def _setup_freestyle(scene, mesh, strategy):
    """设置 Freestyle 描边。"""
    quality, topo_info = check_mesh_topology(mesh)

    if strategy == 'freestyle_auto':
        use_material_boundary = quality == 'clean'
    else:
        use_material_boundary = False

    scene.render.use_freestyle = True
    vl = scene.view_layers[0]
    fs = vl.freestyle_settings
    fs.use_smoothness = True

    while fs.linesets:
        fs.linesets.remove(fs.linesets[0])

    ls = fs.linesets.new("Outline")
    ls.select_silhouette = True
    ls.select_crease = False
    ls.select_border = False
    ls.select_edge_mark = False
    ls.select_material_boundary = use_material_boundary

    linestyle = bpy.data.linestyles.get("NPR_Outline")
    if not linestyle:
        linestyle = bpy.data.linestyles.new("NPR_Outline")
    linestyle.thickness = 1.5
    linestyle.color = (0.0, 0.0, 0.0)
    ls.linestyle = linestyle

    return {
        'enabled': True,
        'quality': quality,
        'topo_info': topo_info,
        'strategy': 'silhouette+material_boundary'
        if use_material_boundary else 'silhouette_only',
    }
