# -*- coding: utf-8 -*-
# Copyright (c) 2024, https://github.com/skys-mission and Half-Bottled Reverie
"""
vosk
"""
import os
import subprocess
import sys

def run_vosk(audio_path):
    """
    调用 gout-vosk.exe 处理音频文件，生成 JSON 输出。

    参数:
        audio_path (str): 输入的音频文件路径。

    返回:
        None: 输出结果保存到指定的 JSON 文件路径。
    """
    # 确保音频文件存在
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # gout-vosk.exe 的路径
    vosk_exe = os.path.join(script_dir, "lib", "gout-vosk.exe")
    if not os.path.isfile(vosk_exe):
        raise FileNotFoundError(f"Executable not found: {vosk_exe}")

    # Vosk 模型的路径
    model_path = os.path.join(script_dir, "lib", "models", "vosk-model")
    if not os.path.isdir(model_path):
        raise FileNotFoundError(f"Model directory not found: {model_path}")

    # 输出路径，在原目录的基础上添加前缀 "processed_"
    audio_dir, audio_filename = os.path.split(audio_path)
    output_filename = f"processed_{audio_filename.rsplit('.', 1)[0]}.json"
    output_path = os.path.join(audio_dir, output_filename)

    # 构造命令
    command = [
        vosk_exe,
        "-audio", audio_path,
        "-model", model_path,
        "-out", output_path,
        "-rate", "16000"
    ]

    # 打印命令以供调试（可选）
    print(f"Running command: {' '.join(command)}")

    # 执行命令
    try:
        result = subprocess.run(command, check=True)
        if result.returncode!=0:
            raise RuntimeError(f"Command failed with exit code {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr.decode('utf-8')}", file=sys.stderr)
        raise

    return output_path

# 示例使用
# run_vosk("F:\\OBS_Video\\test_audio_16000.wav")
