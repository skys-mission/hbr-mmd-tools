# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
MMD Render Optimizer 核心工具函数。
模型检测、语义分类、拓扑检查、色调分析、清理工具。
"""

import re

import bpy  # pylint: disable=import-error
import bmesh  # pylint: disable=import-error
from mathutils import Vector  # pylint: disable=import-error

from .presets import (
    HEAD_BONE_NAMES, SEMANTIC_RULES, PINYIN_RULES,
    _COOL_KEYWORDS, _WARM_KEYWORDS,
)


# ------------------------------------------------------------------
# 模型检测（基于选择对象递归查找）
# ------------------------------------------------------------------

def collect_objects_from_selection(context):
    """
    从当前选中的对象出发，递归收集子树中的所有 MESH 和 ARMATURE 对象。
    返回 (meshes, armatures) 两个列表。
    """
    selected = list(context.selected_objects)
    if not selected:
        return [], []

    meshes = []
    armatures = []
    seen = set()

    for obj in selected:
        _collect_recursive(obj, meshes, armatures, seen)

    return meshes, armatures


def _collect_recursive(obj, meshes, armatures, seen):
    """递归收集对象及其子对象。"""
    obj_id = obj.as_pointer()
    if obj_id in seen:
        return
    seen.add(obj_id)

    if obj.type == 'MESH' and not _is_rigid_dummy(obj):
        meshes.append(obj)
    elif obj.type == 'ARMATURE':
        armatures.append(obj)

    for child in obj.children:
        _collect_recursive(child, meshes, armatures, seen)


def find_primary_mesh(meshes):
    """从 mesh 列表中返回顶点数最多的主 mesh。"""
    if not meshes:
        return None
    return max(meshes, key=lambda m: len(m.data.vertices))


def find_armature_for_meshes(meshes, armatures):
    """
    尝试为 mesh 列表找到对应的 armature。
    优先返回与主 mesh 同父级或同层的 armature。
    """
    if not armatures:
        return None
    if len(armatures) == 1:
        return armatures[0]

    primary = find_primary_mesh(meshes)
    if not primary:
        return armatures[0]

    # 尝试找到与主 mesh 同父级的 armature
    parent = primary.parent
    for arm in armatures:
        if arm.parent == parent or arm == parent:
            return arm
    return armatures[0]


def _is_rigid_dummy(obj):
    """识别 MMD 物理刚体伪 mesh（000_xxx 命名格式）。"""
    if obj.type != 'MESH':
        return False
    n = obj.name
    return len(n) > 3 and n[:3].isdigit() and n[3] == '_'


# ------------------------------------------------------------------
# 角色尺寸计算
# ------------------------------------------------------------------

def head_bone_world_loc(arm):
    """从 armature 找头部骨骼世界坐标。"""
    if not arm or not arm.data:
        return None
    for b in arm.pose.bones:
        if b.name in HEAD_BONE_NAMES:
            return arm.matrix_world @ b.head
    for b in arm.pose.bones:
        n = b.name.lower()
        if 'head' in n or '頭' in b.name or '头' in b.name:
            return arm.matrix_world @ b.head
    return None


def calc_character_metrics(root_obj, arm, mesh):
    """
    计算角色的参考高度和焦点位置。
    返回 (H, fx, fy, fz, cz, es)。
    """
    hl = head_bone_world_loc(arm)
    if hl:
        H = hl.z * 1.08
        fx, fy, fz = hl.x, hl.y, hl.z + H * 0.04
    else:
        coords = [mesh.matrix_world @ Vector(c) for c in mesh.bound_box]
        zs = [c.z for c in coords]
        H = max(zs) - min(zs)
        fx = (max([c.x for c in coords]) + min([c.x for c in coords])) / 2
        fy = (max([c.y for c in coords]) + min([c.y for c in coords])) / 2
        fz = min(zs) + H * 0.92

    es = (H / 1.7) ** 2
    cz = fz - H * 0.92
    return H, fx, fy, fz, cz, es


# ------------------------------------------------------------------
# 材质语义分类
# ------------------------------------------------------------------

def classify_material(mat_name):
    """多语言材质语义分类，返回 (category, is_overlay)。"""
    is_overlay = (
        mat_name.endswith('+')
        or mat_name.endswith('+.001')
        or mat_name.endswith('++')
    )
    name_lower = mat_name.lower()

    for cat, kws in SEMANTIC_RULES:
        for kw in kws:
            if kw.lower() in name_lower:
                return cat, is_overlay

    tokens = [t for t in re.split(r'[._\-+\s]+|\d+', name_lower) if t]
    for cat, kws in PINYIN_RULES:
        for kw in kws:
            if kw in tokens:
                return cat, is_overlay

    return 'fallback', is_overlay


# ------------------------------------------------------------------
# 色调分析
# ------------------------------------------------------------------

def analyze_model_tone(meshes):
    """
    分析模型整体色调和明暗。
    返回 (tone, brightness)：
        tone: 'cool' / 'warm' / 'neutral'
        brightness: 'light' / 'medium' / 'dark'
    """
    total_rgb = [0.0, 0.0, 0.0]
    color_count = 0
    name_cool = 0
    name_warm = 0
    name_count = 0

    for mesh in meshes:
        for slot in mesh.material_slots:
            mat = slot.material
            if not mat:
                continue

            name_lower = mat.name.lower()
            has_cool = any(kw.lower() in name_lower for kw in _COOL_KEYWORDS)
            has_warm = any(kw.lower() in name_lower for kw in _WARM_KEYWORDS)
            if has_cool and not has_warm:
                name_cool += 1
                name_count += 1
            elif has_warm and not has_cool:
                name_warm += 1
                name_count += 1

            if not mat.use_nodes:
                continue
            p = None
            for n in mat.node_tree.nodes:
                if n.bl_idname == 'ShaderNodeBsdfPrincipled':
                    p = n
                    break
            if not p:
                continue
            col = p.inputs.get('Base Color')
            if col is None:
                continue
            rgb = col.default_value[:3]
            s = sum(rgb)
            if s < 0.1 or s > 2.9:
                continue
            total_rgb[0] += rgb[0]
            total_rgb[1] += rgb[1]
            total_rgb[2] += rgb[2]
            color_count += 1

    color_weight = min(1.0, color_count / 5.0)
    name_weight = 1.0 - color_weight if name_count > 0 else 0.0

    color_score = 0.0
    if color_count > 0:
        avg = [c / color_count for c in total_rgb]
        if avg[2] > avg[0] * 1.15:
            color_score = 1.0
        elif avg[0] > avg[2] * 1.15:
            color_score = -1.0

    name_score = 0.0
    if name_count > 0:
        name_score = (name_cool - name_warm) / name_count

    final_score = color_score * color_weight + name_score * name_weight

    if final_score > 0.25:
        tone = 'cool'
    elif final_score < -0.25:
        tone = 'warm'
    else:
        tone = 'neutral'

    if color_count > 0:
        avg = [c / color_count for c in total_rgb]
        v = max(avg)
    else:
        v = 0.45

    if v > 0.55:
        brightness = 'light'
    elif v < 0.35:
        brightness = 'dark'
    else:
        brightness = 'medium'

    return tone, brightness


# ------------------------------------------------------------------
# 拓扑检查
# ------------------------------------------------------------------

def check_mesh_topology(mesh):
    """
    检查网格拓扑质量，返回 (quality, info_dict)。
    quality: 'clean', 'degraded', 'bad'
    """
    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bm.edges.ensure_lookup_table()

    total = len(bm.edges)
    if total == 0:
        bm.free()
        return 'clean', {'total_edges': 0, 'border_edges': 0, 'border_ratio': 0.0}

    border = sum(1 for e in bm.edges if e.is_boundary)
    non_manifold = sum(1 for e in bm.edges if not e.is_manifold)

    bm.free()

    border_ratio = border / total

    if border_ratio < 0.01 and non_manifold < 10:
        quality = 'clean'
    elif border_ratio < 0.05:
        quality = 'degraded'
    else:
        quality = 'bad'

    return quality, {
        'total_edges': total,
        'border_edges': border,
        'non_manifold_edges': non_manifold,
        'border_ratio': round(border_ratio, 4),
    }


# ------------------------------------------------------------------
# 清理自动对象
# ------------------------------------------------------------------

def cleanup_auto_objects():
    """删除之前自动生成的灯光和辅助对象。"""
    auto_names = [
        'AutoKey', 'AutoFill', 'AutoRim', 'AutoHair', 'AutoBack',
        'AutoFront', 'AutoGround', 'AutoBounce', 'AutoBackdrop', 'AutoDome',
    ]
    for name in auto_names:
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
    for name in ['AutoBackdropMat', 'AutoDomeMat', 'AutoGroundMat']:
        mat = bpy.data.materials.get(name)
        if mat:
            bpy.data.materials.remove(mat)
