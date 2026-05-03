# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
配置导入与打开配置目录的共享逻辑。
"""

import os
import subprocess
import sys

from ...core.config_manager import get_config_manager


def import_user_config(
    operator,
    context,
    config_type,
    source_path_attr,
    selection_attr,
):
    """导入用户自定义配置并更新场景属性。

    返回 ``{'FINISHED'}`` 或 ``{'CANCELLED'}``，由调用方原样返回给 Blender。
    """
    scene = context.scene
    source_path = getattr(scene, source_path_attr, "")

    if not source_path:
        operator.report({'ERROR'}, "Please select a custom config file")
        return {'CANCELLED'}

    config_manager = get_config_manager()
    config_name = os.path.splitext(os.path.basename(source_path))[0]

    imported_entry = config_manager.import_config(
        config_type,
        source_path,
        config_name,
    )
    if not imported_entry:
        operator.report({'ERROR'}, "Failed to import config")
        return {'CANCELLED'}

    operator.report({'INFO'}, f"Successfully imported config: {config_name}")
    setattr(scene, selection_attr, imported_entry['id'])
    setattr(scene, source_path_attr, "")
    if context.area is not None:
        context.area.tag_redraw()
    return {'FINISHED'}


def open_user_config_folder(operator, config_type, success_message_prefix):
    """跨平台打开用户配置目录。"""
    config_manager = get_config_manager()
    config_dir = config_manager.get_user_config_dir(config_type)
    os.makedirs(config_dir, exist_ok=True)

    try:
        if os.name == 'nt':
            startfile = getattr(os, "startfile", None)
            if not callable(startfile):
                raise OSError("os.startfile is unavailable on this platform")
            startfile(config_dir)  # pylint: disable=not-callable
        elif os.name == 'posix':
            command = (
                ['open', config_dir]
                if sys.platform == 'darwin'
                else ['xdg-open', config_dir]
            )
            subprocess.run(command, check=True)

        operator.report({'INFO'}, f"{success_message_prefix}: {config_dir}")
    except (OSError, subprocess.SubprocessError) as exc:
        operator.report({'ERROR'}, f"Failed to open folder: {str(exc)}")
        return {'CANCELLED'}

    return {'FINISHED'}
