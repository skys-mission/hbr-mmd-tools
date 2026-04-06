# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and SoyMilkWhisky
"""
口型处理代码
"""
import math

from ..audio.rosa import rosa
from ..audio.ffmpeg import convert_to_wav_16000


# from ..audio.phoneme import Phoneme
# from ..audio.vosk import run_vosk


class Lips:  # pylint: disable=too-few-public-methods
    """
    ...
    """

    @staticmethod
    def _clamp(value, min_value, max_value):
        """钳制值在最小值和最大值之间"""
        return max(min(value, max_value), min_value)

    @staticmethod
    def _symmetric_sigmoid_transition(t, start, end, peak_value, approach_speed):
        """使用对称的 Sigmoid 函数进行平滑过渡"""
        duration = end - start
        # mid_time = (start + end) / 2
        if t < start or t > end:
            return 0.0
        # 归一化时间 t 到 [0, 1]
        normalized_time = (t - start) / duration
        # 左半部分 (从 0 到 1)
        if normalized_time <= 0.5:
            value = peak_value / (1 + math.exp(-approach_speed * (normalized_time - 0.25) * 4))
        # 右半部分 (从 1 到 0)
        else:
            value = peak_value / (1 + math.exp(-approach_speed * (0.75 - normalized_time) * 4))
        return Lips._clamp(value, 0.0, peak_value)

    @staticmethod
    def lips_gen(phoneme_data, buffer=0.05, approach_speed=3.0, max_morph_value=1.0):
        """
        生成口型关键帧。

        根据音素数据生成口型关键帧，用于动画或游戏角色的口型同步。
        关键帧包括开始、中间、结束和缓冲阶段，以实现平滑的口型变化效果。

        参数:
        - phoneme_data: 音素数据列表，每个元素包含音素的开始时间、结束时间和音素本身。
        - buffer: 缓冲时间，用于在口型变化前后添加缓冲关键帧，默认为0.05秒。
        - approach_speed: 趋近速度，控制口型趋近于完全打开的速度，默认为3.0。

        返回:
        - lips: 口型关键帧列表，每个关键帧包含时间、口型、值和关键帧类型。
        """

        # 缓冲参数控制口型边缘缓冲时间
        buffer = max(0.0, min(buffer, 0.1))

        # 趋近速度控制参数，控制趋近1的速度
        approach_speed = max(0.0, min(approach_speed, 10.0))

        lips = []

        for start, end, morph in phoneme_data:
            if morph:
                # 添加起始关键帧
                lips.append({
                    "time": round(start, 3),  # 起始时间
                    "morph": morph,  # 口型
                    "value": 0.0,  # 起始时关闭口型
                    "frame_type": "start",  # 标记为开始帧
                })

                # 添加中间关键帧
                mid_time = (start + end) / 2
                lips.append({
                    "time": round(mid_time, 3),  # 中间时间
                    "morph": morph,  # 口型
                    "value": max_morph_value,  # 中间时完全打开口型
                    "frame_type": "middle",  # 标记为中间帧
                })

                # 添加结束关键帧
                lips.append({
                    "time": round(end, 3),  # 结束时间
                    "morph": morph,  # 口型
                    "value": 0.0,  # 结束时关闭口型
                    "frame_type": "end",  # 标记为结束帧
                })

                # 添加缓冲关键帧
                if buffer > 0:
                    buffer_start = start + buffer
                    buffer_end = end - buffer
                    if buffer_start < buffer_end:
                        # 缓冲开始
                        lips.append({
                            "time": round(buffer_start, 3),
                            "morph": morph,
                            "value": Lips._symmetric_sigmoid_transition(
                                buffer_start,
                                start,
                                end,
                                max_morph_value,
                                approach_speed
                            ),
                            "frame_type": "buffer_start",  # 标记为缓冲开始帧
                        })
                        # 缓冲结束
                        lips.append({
                            "time": round(buffer_end, 3),
                            "morph": morph,
                            "value": Lips._symmetric_sigmoid_transition(
                                buffer_end,
                                start,
                                end,
                                max_morph_value,
                                approach_speed
                            ),
                            "frame_type": "buffer_end",  # 标记为缓冲结束帧
                        })

        # 对关键帧按时间排序
        lips.sort(key=lambda x: x["time"])

        return lips

    @staticmethod
    def morph_split(lips):
        """
        根据特定的 morph 值对 lips 数据进行分割和分类。

        该函数接收一个包含 lips 信息的列表，每个元素是一个字典，其中包含一个 'morph' 键。
        函数将根据 morph 值对这些元素进行分类，只保留具有特定 morph 值的元素，并将它们
        分别存储在以 morph 值命名的列表中，最终返回一个字典，其中包含这些列表。

        参数:
        lips (list): 包含 lips 信息的列表，每个元素是一个包含 'morph' 键的字典。

        返回:
        dict: 一个字典，包含根据 morph 值分类后的 lips 元素列表。
        """
        # 定义需要的 morph 值集合，这些是嘴唇形态的元音值
        target_morphs = {'a', 'e', 'i', 'o', 'u', 'n'}

        # 初始化结果字典，为每个目标 morph 值创建一个空列表
        result = {morph: [] for morph in target_morphs}

        # 遍历输入的 lips 列表
        for item in lips:
            # 检查当前元素的 morph 值是否在目标集合中
            if item['morph'] in target_morphs:
                # 如果是，将其添加到对应 morph 值的列表中
                result[item['morph']].append(item)

        # 返回分类后的结果
        return result

    @staticmethod
    def convert_timing_to_frames(morph_data, start_frame=1, fps=24):
        """
        将给定的形态时间数据转换为帧数据。

        此函数根据帧速率将时间戳转换为帧号，主要用于动画制作或类似领域。

        参数:
        morph_data (dict): 包含形态及其对应时间数据的字典。
        start_frame (int): 起始帧号，默认为1。
        fps (int): 帧速率，默认为24帧/秒。

        返回:
        dict: 包含形态及其对应帧数据的字典。
        """

        # 初始化结果字典
        result = {}

        # 遍历形态数据
        for morph, frames in morph_data.items():
            # 初始化帧数据列表
            frame_data = []

            # 遍历每个时间帧
            for f in frames:
                # 新增时间戳校验
                if f['time'] < 0:
                    continue  # 跳过负时间戳
                frame_num = int(round(f['time'] * fps)) + start_frame
                frame_num = max(frame_num, start_frame)

                # 将转换后的帧数据添加到列表中
                frame_data.append({
                    'frame': frame_num,
                    'value': round(f['value'], 2),
                    'frame_type': f['frame_type']
                })

            # 将形态及其对应的帧数据添加到结果字典中
            result[morph] = frame_data

        # 返回结果字典
        return result

    @staticmethod
    def mmd_lips_gen(wav_path, buffer=0.05, approach_speed=3.0,
                     # pylint: disable=too-many-arguments,too-many-positional-arguments
                     db_threshold=-50, rms_threshold=0.01, max_morph_value=1.0, start_frame=1,
                     fps=24):
        """
        ...
        """
        wav_path_16 = convert_to_wav_16000(wav_path)

        # json_path = run_vosk(wav_path_16)
        #
        # phoneme_data_res1 = Phoneme.gen(json_path)
        # pprint(phoneme_data_res1)
        phoneme_data_res = rosa(wav_path_16, db_threshold=db_threshold, rms_threshold=rms_threshold)

        keyframes_res = Lips.lips_gen(
            phoneme_data_res,
            buffer=buffer,
            approach_speed=approach_speed,
            max_morph_value=max_morph_value
        )

        res = Lips.morph_split(keyframes_res)

        frames_res = Lips.convert_timing_to_frames(
            res,
            start_frame=start_frame,
            fps=fps
        )

        return frames_res

# from pprint import pprint
# lips_res = Lips.mmd_lips_gen("F:\\OBS_Video\\test2.wav")
# pprint(lips_res)
#
#
