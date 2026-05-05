# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
Blender 版本兼容相关工具。
"""

import os
import sys

import bpy  # pylint: disable=import-error


MIN_SUPPORTED_BLENDER_VERSION = (4, 2, 0)
UNSUPPORTED_FROM_VERSION = (5, 1, 0)
FIXED_BUNDLED_PYTHON_VERSION = (3, 11)


def get_blender_version():
    """返回当前 Blender 版本元组。"""
    return tuple(bpy.app.version)


def is_blender_version_at_least(version):
    """判断当前 Blender 版本是否不低于目标版本。"""
    return get_blender_version() >= tuple(version)


def ensure_supported_blender_version(
    min_version=MIN_SUPPORTED_BLENDER_VERSION,
    unsupported_from=UNSUPPORTED_FROM_VERSION,
):
    """在版本不在支持范围内时抛出异常。"""
    current_version = get_blender_version()
    if current_version < tuple(min_version):
        required = ".".join(str(part) for part in min_version)
        current = ".".join(str(part) for part in current_version)
        raise RuntimeError(
            f"HBR MMD Tools requires Blender {required} or newer, current version is {current}."
        )
    if current_version >= tuple(unsupported_from):
        threshold = ".".join(str(part) for part in unsupported_from)
        current = ".".join(str(part) for part in current_version)
        raise RuntimeError(
            f"HBR MMD Tools supports Blender 4.2 - 5.0 only, "
            f"current version is {current}. "
            f"Blender {threshold}+ uses a newer Python version that is not yet compatible."
        )


def get_bundled_python_lib_path(base_dir):
    """返回固定的 bundled 依赖目录。"""
    runtime_version = (sys.version_info.major, sys.version_info.minor)
    if runtime_version != FIXED_BUNDLED_PYTHON_VERSION:
        expected = ".".join(str(part) for part in FIXED_BUNDLED_PYTHON_VERSION)
        current = ".".join(str(part) for part in runtime_version)
        raise RuntimeError(
            f"HBR MMD Tools bundled audio dependencies require Python {expected}, "
            f"current runtime is {current}."
        )

    return os.path.join(
        base_dir,
        f"plib{FIXED_BUNDLED_PYTHON_VERSION[0]}{FIXED_BUNDLED_PYTHON_VERSION[1]}",
    )
