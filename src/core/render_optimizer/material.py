# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
MMD Render Optimizer — 材质增强。
"""

from .presets import MATERIAL_PRESETS
from .utils import classify_material


def _get_principled(mat):
    """获取材质 Principled BSDF 节点。"""
    if not mat or not mat.use_nodes:
        return None
    for n in mat.node_tree.nodes:
        if n.bl_idname == 'ShaderNodeBsdfPrincipled':
            return n
    return None


def _safe_set_input(node, input_name, value):
    """仅当输入未连接时才设置值。"""
    inp = node.inputs.get(input_name)
    if inp is None or inp.is_linked:
        return
    if isinstance(value, tuple):
        try:
            if len(value) == 3 and len(inp.default_value) == 3:
                inp.default_value = value
            elif len(value) == 3 and len(inp.default_value) == 4:
                inp.default_value = (*value, 1.0)
            elif len(value) == 4 and len(inp.default_value) == 4:
                inp.default_value = value
        except (TypeError, AttributeError):
            pass
    else:
        try:
            inp.default_value = value
        except Exception:  # pylint: disable=broad-exception-caught
            pass


def make_aggressive_preset(base_preset, cat):
    """基于基础预设生成激进版参数。"""
    preset = dict(base_preset)

    if cat in ('face', 'skin'):
        preset['Subsurface Weight'] = min(
            0.8, preset.get('Subsurface Weight', 0) * 1.2 + 0.05,
        )
        preset['Coat Weight'] = min(
            0.5, preset.get('Coat Weight', 0) * 1.3 + 0.05,
        )
        preset['Roughness'] = max(0.28, preset.get('Roughness', 0.5) * 0.82)
        preset['Specular IOR Level'] = min(
            0.8, preset.get('Specular IOR Level', 0.5) * 1.10,
        )
        preset['Subsurface Scale'] = preset.get('Subsurface Scale', 0.08) * 1.15
    elif cat == 'hair':
        preset['Anisotropic'] = min(
            1.0, preset.get('Anisotropic', 0) * 1.8 + 0.15,
        )
        preset['Anisotropic Rotation'] = 0.0
        preset['Coat Weight'] = min(
            0.5, preset.get('Coat Weight', 0) * 4.0 + 0.15,
        )
        preset['Roughness'] = max(0.22, preset.get('Roughness', 0.5) * 0.65)
        preset['Specular IOR Level'] = min(
            1.0, preset.get('Specular IOR Level', 0.5) * 1.2,
        )
    elif cat == 'metal':
        preset['Metallic'] = 1.0
        preset['Roughness'] = max(0.06, preset.get('Roughness', 0.3) * 0.35)
        preset['Anisotropic'] = min(
            1.0, preset.get('Anisotropic', 0) + 0.25,
        )
        preset['Specular IOR Level'] = min(
            1.0, preset.get('Specular IOR Level', 0.5) * 1.3,
        )
    elif cat == 'jewelry':
        preset['Coat Weight'] = 1.0
        preset['Roughness'] = max(0.06, preset.get('Roughness', 0.25) * 0.4)
        preset['IOR'] = max(1.6, preset.get('IOR', 1.5) + 0.25)
        preset['Specular IOR Level'] = min(
            1.0, preset.get('Specular IOR Level', 0.5) * 1.3,
        )
    elif cat in ('cloth', 'shoes', 'bag', 'wing_tail'):
        preset['Roughness'] = max(0.28, preset.get('Roughness', 0.6) * 0.58)
        preset['Sheen Weight'] = min(
            1.0, preset.get('Sheen Weight', 0) * 5.0 + 0.25,
        )
        preset['Sheen Roughness'] = 0.35
        preset['Coat Weight'] = min(
            0.35, preset.get('Coat Weight', 0) + 0.15,
        )
    elif cat in ('eye_iris', 'eye_pupil', 'eye_highlight'):
        preset['Coat Weight'] = min(
            1.0, preset.get('Coat Weight', 0) * 1.8 + 0.1,
        )
        preset['Roughness'] = max(0.04, preset.get('Roughness', 0.18) * 0.5)
        preset['IOR'] = max(1.5, preset.get('IOR', 1.45) + 0.1)
    elif cat == 'mouth':
        preset['Subsurface Weight'] = min(
            1.0, preset.get('Subsurface Weight', 0) * 1.4,
        )
        preset['Coat Weight'] = min(
            0.8, preset.get('Coat Weight', 0) + 0.35,
        )
        preset['Roughness'] = max(0.25, preset.get('Roughness', 0.38) * 0.75)
    elif cat == 'eye_white':
        preset['Subsurface Weight'] = min(
            0.15, preset.get('Subsurface Weight', 0) * 2.0,
        )
        preset['Coat Weight'] = min(
            0.6, preset.get('Coat Weight', 0) + 0.3,
        )
    elif cat == 'teeth':
        preset['Coat Weight'] = min(
            0.8, preset.get('Coat Weight', 0) + 0.4,
        )
        preset['Roughness'] = max(0.08, preset.get('Roughness', 0.2) * 0.6)
    elif cat in ('accessory', 'ear'):
        preset['Metallic'] = min(1.0, preset.get('Metallic', 0) + 0.35)
        preset['Roughness'] = max(0.15, preset.get('Roughness', 0.45) * 0.65)
        preset['Coat Weight'] = min(
            0.6, preset.get('Coat Weight', 0) + 0.25,
        )

    return preset


def enhance_materials(meshes, aggressive=False):
    """
    批量优化材质。aggressive=True 时显著增强质感差异。
    返回统计字典 {'total', 'classified', 'fallback'}。
    """
    stats = {'total': 0, 'classified': 0, 'fallback': 0}

    for mesh in meshes:
        for slot in mesh.material_slots:
            mat = slot.material
            if not mat:
                continue
            stats['total'] += 1
            cat, _ = classify_material(mat.name)
            p = _get_principled(mat)
            if not p:
                continue

            preset = MATERIAL_PRESETS.get(cat, MATERIAL_PRESETS['fallback'])
            if aggressive:
                preset = make_aggressive_preset(preset, cat)

            for k, v in preset.items():
                _safe_set_input(p, k, v)

            # 自动金属度检测 fallback
            if cat in ('fallback', 'accessory', 'cloth', 'shoes', 'bag'):
                name_lower = mat.name.lower()
                metal_hints = {
                    '金', '银', '銀', '铁', '鉄', '钢', '鋼', '铜', '銅',
                    '链', '鎖', '锁', '扣', '醣', '钉', '釘', '铆',
                    'metal', 'gold', 'silver', 'iron', 'steel', 'copper',
                    'chain', 'buckle', 'rivet', 'gear', 'mech',
                }
                if any(h in name_lower for h in metal_hints):
                    _safe_set_input(p, 'Metallic', 0.95 if aggressive else 0.85)
                    _safe_set_input(p, 'Roughness', 0.18 if aggressive else 0.35)

            if cat == 'fallback':
                stats['fallback'] += 1
            else:
                stats['classified'] += 1

    return stats
