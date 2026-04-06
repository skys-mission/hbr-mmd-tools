# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and Half-Bottled Reverie
"""
...
"""
import os
import sys
import bpy  # pylint: disable=import-error
from ..core.compat import get_bundled_python_lib_path


def unload_pkg():
    """
    ...
    """
    py_file_dir = os.path.abspath(os.path.dirname(__file__))
    _ = bpy.app.version
    plib_path = get_bundled_python_lib_path(py_file_dir)

    if plib_path in sys.path:
        sys.path.remove(plib_path)
