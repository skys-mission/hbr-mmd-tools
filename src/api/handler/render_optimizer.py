# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
MMD Render Optimizer — Operators
"""
from bpy.types import Operator  # pylint: disable=import-error

from ...services.render_optimizer_service import (
    apply_render_optimizer,
    reset_render_optimizer,
)
from ...util.logger import Log


class RenderOptimizerApplyOperator(Operator):  # pylint: disable=too-few-public-methods
    """Apply MMD render optimization"""
    bl_idname = "hbr_mmd.render_optimizer_apply"
    bl_label = "Apply Optimization"
    bl_description = "Automatically optimize scene rendering based on current settings"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        """Require at least one selected object."""
        return len(context.selected_objects) > 0

    def execute(self, context):
        """Apply render optimization and report results."""
        context.window_manager.progress_begin(0, 100)
        context.window.cursor_modal_set('WAIT')
        context.window_manager.progress_update(50)

        try:
            result = apply_render_optimizer(context)
            mat_stats = result['mat_stats']
            outline_info = result['outline_info']

            report = (
                f"Optimized {mat_stats['total']} materials, "
                f"classified: {mat_stats['classified']}, "
                f"fallback: {mat_stats['fallback']}"
            )
            if outline_info.get('enabled'):
                report += f" | Outline: {outline_info['strategy']}"
            report += f" | Tone: {result['tone']}, Brightness: {result['brightness']}"

            self.report({'INFO'}, report)
        except Exception as e:  # pylint: disable=broad-exception-caught
            context.window_manager.progress_end()
            context.window.cursor_modal_restore()
            Log.raise_error(str(e), type(e))

        context.window_manager.progress_end()
        context.window.cursor_modal_restore()
        return {'FINISHED'}


class RenderOptimizerResetOperator(Operator):  # pylint: disable=too-few-public-methods
    """Reset render optimizer changes"""
    bl_idname = "hbr_mmd.render_optimizer_reset"
    bl_label = "Reset"
    bl_description = "Delete auto-created lights, reset World, disable Compositor and Freestyle"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, _context):
        """Reset all auto-created render objects."""
        try:
            reset_render_optimizer()
            self.report({'INFO'}, "Scene reset completed")
        except Exception as e:  # pylint: disable=broad-exception-caught
            Log.raise_error(str(e), type(e))
        return {'FINISHED'}
