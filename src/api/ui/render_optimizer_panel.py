# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
MMD Render Optimizer — UI Panels
"""
import bpy  # pylint: disable=import-error


class RenderOptimizerPanel(bpy.types.Panel):  # pylint: disable=too-few-public-methods
    """主面板"""
    bl_label = "MMD Render Optimizer (Experimental)"
    bl_idname = "OBJECT_PT_RENDER_OPTIMIZER"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HBR MMD Tools'
    bl_order = 4

    def draw(self, context):
        """Draw the main render optimizer panel."""
        layout = self.layout
        scene = context.scene

        layout.label(text="Select target model, then apply", icon='INFO')

        layout.separator()

        # 渲染预设
        layout.prop(scene, "render_opt_preset")

        layout.separator()

        # 执行按钮
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator(
            "hbr_mmd.render_optimizer_apply",
            text="Apply Optimization",
            icon="RENDER_STILL",
        )

        row = layout.row(align=True)
        row.operator("hbr_mmd.render_optimizer_reset", text="Reset", icon="TRASH")


class RenderOptimizerAdvancedPanel(bpy.types.Panel):  # pylint: disable=too-few-public-methods
    """高级参数面板"""
    bl_label = "Advanced"
    bl_idname = "OBJECT_PT_RENDER_OPTIMIZER_ADVANCED"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HBR MMD Tools'
    bl_parent_id = "OBJECT_PT_RENDER_OPTIMIZER"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        """Draw the advanced render optimizer panel."""
        layout = self.layout
        scene = context.scene

        # 亮度倾向
        layout.prop(scene, "render_opt_brightness_override")

        layout.separator()

        # 开关选项
        layout.prop(scene, "render_opt_use_compositor")
        layout.prop(scene, "render_opt_outline_strategy")

        layout.separator()

        # 渲染引擎
        layout.prop(scene, "render_opt_engine")
