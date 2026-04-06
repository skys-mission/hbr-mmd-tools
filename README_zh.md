# HBR MMD Tools

[![Pylint](https://github.com/skys-mission/hbr_mmd_tools/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/skys-mission/hbr_mmd_tools/actions/workflows/pylint.yml)
[![CodeQL Advanced](https://github.com/skys-mission/hbr_mmd_tools/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/skys-mission/hbr_mmd_tools/actions/workflows/codeql.yml)
[![Bandit](https://github.com/skys-mission/hbr_mmd_tools/actions/workflows/bandit.yml/badge.svg)](https://github.com/skys-mission/hbr_mmd_tools/actions/workflows/bandit.yml)

其它语言：[English](README.md), [日本語](README_ja.md)

一个面向 MMD 工作流的 Blender 插件，提供 MMD 口型生成、随机眨眼、形态键辅助和面向 MikuMikuDance 风格角色的 Blender 工作流工具。

本项目现更名为 `HBR MMD Tools`，此前以另一个插件名发布。

`HBR` 来自 `Half-Bottled Reverie`，`MMD Tools` 也更直接地说明了插件当前的功能定位。

> 当前状态
>
> `v0.5.0` 即将发布，并会带来大量更新。
>
> 如果当前更需要相对成熟的版本，可以先使用 `v0.3.2`。

<!-- TOC -->
* [HBR MMD Tools](#hbr-mmd-tools)
  * [Download](#download)
  * [功能](#功能)
    * [MMD口型生成](#mmd口型生成)
      * [使用方法](#使用方法)
      * [参数介绍](#参数介绍)
      * [如何适配其它模型](#如何适配其它模型)
    * [随机眨眼](#随机眨眼)
    * [其它功能](#其它功能)
  * [支持](#支持)
    * [Blender版本适配](#blender版本适配)
    * [操作系统适配](#操作系统适配)
  * [高版本如何安装Blender插件](#高版本如何安装blender插件)
  * [关于开发本插件](#关于开发本插件)
    * [注意事项](#注意事项)
  * [开源引用](#开源引用)
<!-- TOC -->

## Download

https://github.com/skys-mission/hbr_mmd_tools/releases

中国大陆用户：

链接: https://pan.baidu.com/s/17ubgxZvXVs6goKBjtBFzXA?pwd=gmuv 提取码: gmuv 

## 功能

### MMD口型生成

通过Vosk 音频模型识别出音素口型，添加到MMD标准模型上

本插件识别的MMD模型的口型形态键名：あ，い，う，え，お, ん。除了あ以外没有的全部改到あ上，如果没有あ则报错。

警告：该功能会破坏音频时间范围内的あ，い，う，え，お, ん形态键关键帧


#### 使用方法

![lips_gen2.0f.webp](.img/lips_gen2.0f.webp)

1. 在Audio Path中选择一个音频文件（常规的音频文件大概率都可以用包括mp4）
2. 选中一个mmd模型的任意层父级（注意，如果对象下有多个网格体包含这些形态键，则所有网格体的形态键均会被修改）
3. 建议打开系统控制台观察进度，Mac版Blender没有此功能。（Blender菜单栏->windows->Toggle System Console）
4. 设置参数，点击生成（~~注意当前版本会在音频文件同级目录生成一些可读的缓存文件，不会清除~~）
5. 等待鼠标指针从数字恢复成正常

#### 参数介绍

![lips3.0.webp](.img/lips3.0.webp)

- Start Frame: 音频从那一帧往后
- DB Threshold: DB降噪，如果识别不准则调高，如果识别不到则调低
- RMS Threshold: RMS降噪，如果识别不准则调高，如果识别不到则调低
- Delayed Opening: 延时张嘴比例
- Speed Up Opening: 识别开始到延时张嘴的曲线速度调整参数
- Max Morph Value: 形态键的最大阈值

#### 如何适配其它模型

比如vrm，你需要找到你的模型或者自己设置A，E，I，O，U, N的形态键，复制并改为MMD标准形态键名

**至少要拥有あ，才能使用本功能**

- あ = A
- い = I
- う = U
- え = E
- お = O
- ん = N

如果你不会复制，可以参考：[copy_shape_key.md](docs/copy_shape_key.md)

![lip_sync.webp](.img/lip_sync.webp)
模型来源：KissshotSusu

### 随机眨眼

随机眨眼识别的是：まばたき ，这个形态键，如果没有你需要自己转化或制作该形态键

警告：该功能会破坏帧数范围内まばたき形态键关键帧

1. 选中一个mmd模型的任意层父级（注意，如果对象下有多个网格体包含这些形态键，则所有网格体的形态键均会被修改）
2. 建议打开系统控制台观察进度。（Blender菜单栏->windows->Toggle System Console）
3. 设置参数，点击生成
4. 等待鼠标指针从数字恢复成正常

![blink_args.webp](.img/blink_args.webp)

- blink interval: 眨眼间隔，单位秒
- blinking wave ratio: 随机比例0.01-1可调整

### 其它功能

文档编写中...

## 支持

### Blender版本适配

- 主要支持的版本（本人会进行测试）
    - 3.6 ，4.2
- 或许可以运行的版本
    - 大于等于3.6
- 计划支持的版本
    - 下一个Blender LTS版本
- 不计划适配
    - 小于3.6

### 操作系统适配

- 当前支持
    - windows-x64
- 可能支持
    - macos-arm64
- 不计划支持
    - linux（除非出现重大变故，否则不计划支持）

## 高版本如何安装Blender插件

参考：https://docs.blender.org/manual/zh-hans/4.2/editors/preferences/addons.html#prefs-extensions-install-legacy-addon

## 关于开发本插件

### 注意事项

- blender3.6-4.4可能需要numba库：版本<=0.60.0（其它版本Blender暂不确定）

## 开源引用

| 项目                         | 链接                                               | 协议                                     |
|----------------------------|--------------------------------------------------|----------------------------------------|
| FFmpeg                     | https://github.com/FFmpeg/FFmpeg                 | GPLv3（Releases中内嵌的工具采用协议，仓库中无ffmpeg代码） |
| ~~Vosk-API和Vosk AI Model~~ | ~~https://github.com/alphacep/vosk-api~~         | Apache-2.0                             |
| ~~CMU Dict~~               | ~~http://www.speech.cs.cmu.edu/cgi-bin/cmudict~~ | 2-Clause BSD License                   |
| ~~gout-vosk tool~~         | ~~https://github.com/skys-mission/gout~~         | GPLv3                                  |
