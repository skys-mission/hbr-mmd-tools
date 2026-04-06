# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and Half-Bottled Reverie
"""
ffmpeg
"""
import subprocess
import os
import platform
import random
from pathlib import Path


def convert_to_wav_16000(audio_path):
    """
    Returns:
    - str: Path of the converted audio file (.wav) in the same directory as input file.
    """
    # Ensure the input file exists
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Input file does not exist: {audio_path}")

    # Retrieve file name and target file path
    base_name = Path(audio_path).stem  # 获取文件名（不含扩展）

    # 在路径中拼接随机数
    output_path = (Path(audio_path).parent /
                   f"{base_name}_hbr16khz_{random.randint(100, 999)}.wav")

    # Get the current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Check the operating system type and set the ffmpeg path
    if platform.system() == "Windows":
        ffmpeg_filename = "ffmpeg.exe"
    else:
        ffmpeg_filename = "ffmpeg"
    ffmpeg_path = os.path.join(script_dir, "lib", ffmpeg_filename)

    # Check if the ffmpeg executable exists
    if not os.path.isfile(ffmpeg_path):
        raise FileNotFoundError(
            f"'ffmpeg' executable not found: {ffmpeg_path}. "
            f"Please ensure the file exists and is executable."
        )

    # 自动处理执行权限（仅非Windows系统）
    if platform.system() != "Windows" and not os.access(ffmpeg_path, os.X_OK):
        try:
            os.chmod(ffmpeg_path, 0o755)  # 赋予可执行权限
        except Exception as e:
            raise PermissionError(
                f"Failed to make FFmpeg executable at {ffmpeg_path}. "
                f"Please run manually: chmod +x {ffmpeg_path}"
            ) from e

    command = [
        ffmpeg_path,
        "-i", audio_path,
        "-max_muxing_queue_size", "1024",  # 处理复杂流时防止阻塞
        "-buffer_size", "4096K",  # 设置解码器缓冲区大小
        "-threads", str(os.cpu_count() or 2),  # 使用所有可用CPU核心
        "-af", "loudnorm=I=-14:LRA=11:TP=-1.5",  # 使用 loudnorm 滤镜，设置到 YouTube 推荐标准
        "-ar", "16000",  # 采样率 16000Hz
        "-ac", "1",  # 单声道
        "-y",  # 覆盖输出文件
        output_path  # 输出文件路径
    ]

    # Call ffmpeg
    try:
        subprocess.run(command, check=True, timeout=1800)  # 直接捕获异常
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg failed: {e.stderr.decode()}") from e

    # Return the generated file path
    return output_path

# 示例用法
# if __name__ == "__main__":
#     input_audio_path = "F:\OBS_Video\\test.wav"  # 替换为你的音频文件路径
#     try:
#         output = convert_to_wav_16000(input_audio_path)
#         print(f"转换成功！输出文件路径: {output}")
#     except Exception as e:
#         print(f"转换失败: {e}")
