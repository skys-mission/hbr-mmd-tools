# -*- coding: utf-8 -*-
"""
定义了一个名为Bridge的类，用于在Blender环境中执行特定操作。
该类提供了一系列静态方法，包括获取Blender版本信息、注册和注销类、注册和注销翻译，
以及在Blender主线程中调用函数。

Copyright (c) 2025, https://github.com/skys-mission and SoyWhisky
"""

import bpy  # pylint: disable=import-error

from ..core.compat import get_blender_version, is_blender_version_at_least
from .data.local import LOCAL_CH_40, LOCAL_CH_36
from .data.translation_dict import get_translation_zh_dict


class Bridge:  # pylint: disable=too-few-public-methods
    """
    Blender桥接类，提供静态方法以在Blender环境中执行特定操作。
    """

    class App:
        """
        App类提供了静态方法来获取Blender应用程序信息，注册和注销翻译，
        以及在主线程中调用函数。
        """
        bl_version = (0, 0, 0)

        @staticmethod
        def get_bl_version():
            """
            获取当前Blender版本信息。

            Returns:
                tuple: 包含主要版本号、次要版本号和补丁号的元组。
            """
            return get_blender_version()

        @staticmethod
        def register_translations(addon_name):
            """
            注册翻译字典。

            Args:
                addon_name (str): 插件名称。
            """
            translation_dict = get_translation_zh_dict(LOCAL_CH_36)
            if is_blender_version_at_least((4, 0, 0)):
                translation_dict = get_translation_zh_dict(LOCAL_CH_40)
            bpy.app.translations.register(addon_name, translation_dict)

        @staticmethod
        def unregister_translations(addon_name):
            """
            注销翻译。

            Args:
                addon_name (str): 插件名称。
            """
            bpy.app.translations.unregister(addon_name)

        @staticmethod
        def call_blender_main_thread(function):
            """
            在Blender主线程中调用函数。

            Args:
                function (callable): 要调用的函数。
            """
            bpy.app.timers.register(function)

    class Utils:
        """
        Utils类提供了静态方法来注册和注销类。
        """

        @staticmethod
        def register_class(bl_cls):
            """
            注册一个Blender类。

            Args:
                bl_cls (type): 要注册的类。
            """
            bpy.utils.register_class(bl_cls)

        @staticmethod
        def unregister_class(bl_cls):
            """
            注销一个Blender类。

            Args:
                bl_cls (type): 要注销的类。
            """
            bpy.utils.unregister_class(bl_cls)

    class Types:
        """
        Types类提供了一个静态方法来获取场景类型。
        """

        @staticmethod
        def get_scene():
            """
            获取Blender场景类型。

            返回:
                bpy.types.Scene: Blender场景类型。
            """
            return bpy.types.Scene

    class Props:
        """
        Props类提供了一个静态方法来获取指针属性类型。
        """

        @staticmethod
        def get_pointer_property():
            """
            获取Blender指针属性类型。

            返回:
                bpy.props.PointerProperty: Blender指针属性类型。
            """
            return bpy.props.PointerProperty


def initialize():
    """
    初始化Bridge类，设置Blender版本信息。
    """
    Bridge.App.bl_version = Bridge.App.get_bl_version()


initialize()
