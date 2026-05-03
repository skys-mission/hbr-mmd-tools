# -*- coding: utf-8 -*-
# Copyright (c) 2025, https://github.com/skys-mission and Half-Bottled Reverie
"""
Log封装库
"""
import logging
import traceback

class Log:
    """
    日志工具类，提供日志记录功能，包括info, warning和error级别的日志。
    该类使用单例模式管理日志记录器，确保日志记录的一致性和效率。
    """
    _logger = None

    @staticmethod
    def _get_logger():
        """
        获取日志记录器实例。
        如果日志记录器尚未初始化，则进行初始化配置。
        """
        if Log._logger is None:
            # 配置日志记录器
            Log._logger = logging.getLogger('hbr_mmd_tools')
            Log._logger.setLevel(logging.INFO)
            Log._logger.propagate = False

            if not Log._logger.handlers:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)

                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                console_handler.setFormatter(formatter)

                Log._logger.addHandler(console_handler)

        return Log._logger

    @staticmethod
    def _get_caller_info():
        """
        获取调用日志方法的调用者信息。

        栈布局：当前 _get_caller_info -> info/warning/error/raise_error -> 真实调用者。
        """
        stack = traceback.extract_stack()
        if len(stack) >= 3:
            caller_frame = stack[-3]
            return f"{caller_frame.filename}:{caller_frame.lineno}"
        return None

    @staticmethod
    def info(message):
        """
        记录info级别的日志信息。
        包含日志消息和调用者信息。
        """
        logger = Log._get_logger()
        caller_info = Log._get_caller_info()
        logger.info(f"{message} ({caller_info})")

    @staticmethod
    def warning(message):
        """
        记录warning级别的日志信息。
        包含日志消息和调用者信息。
        """
        logger = Log._get_logger()
        caller_info = Log._get_caller_info()
        logger.warning(f"{message} ({caller_info})")

    @staticmethod
    def error(message):
        """
        记录error级别的日志信息。
        包含日志消息和当前调用栈信息。
        """
        logger = Log._get_logger()
        stack = traceback.format_stack()
        logger.error(f"{message}\n{''.join(stack)}")

    @staticmethod
    def raise_error(message, exception_type=RuntimeError):
        """
        记录error级别的日志信息并抛出指定类型的异常。
        包含日志消息和调用者信息。
        """
        logger = Log._get_logger()
        caller_info = Log._get_caller_info()
        error_message = f"{message} ({caller_info})"
        logger.error(error_message)
        raise exception_type(error_message)
