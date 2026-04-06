# HBR MMD Tools

[![Pylint](https://github.com/skys-mission/hbr-mmd-tools/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/skys-mission/hbr-mmd-tools/actions/workflows/pylint.yml)
[![CodeQL Advanced](https://github.com/skys-mission/hbr-mmd-tools/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/skys-mission/hbr-mmd-tools/actions/workflows/codeql.yml)
[![Bandit](https://github.com/skys-mission/hbr-mmd-tools/actions/workflows/bandit.yml/badge.svg)](https://github.com/skys-mission/hbr-mmd-tools/actions/workflows/bandit.yml)

Other languages: [简体中文](README_zh.md), [日本語](README_ja.md)

A Blender add-on for MMD workflows. Main features include MMD lip-sync generation, random blinking, and related utility tools.

This project is renamed to `HBR MMD Tools`. The previous name was `whisky_helper_for_blender`.

`HBR` comes from `Half-Bottled Reverie`, and `MMD Tools` reflects the add-on's current focus more directly.

<!-- TOC -->
* [HBR MMD Tools](#hbr-mmd-tools)
  * [Download](#download)
  * [Features](#features)
    * [MMD Lip-Sync Generation](#mmd-lip-sync-generation)
      * [Usage](#usage)
      * [Parameter Introduction](#parameter-introduction)
      * [How to Adapt to Other Models](#how-to-adapt-to-other-models)
    * [Random Blinking](#random-blinking)
    * [Other Features](#other-features)
  * [Support](#support)
    * [Blender Version Compatibility](#blender-version-compatibility)
    * [Operating System Compatibility](#operating-system-compatibility)
  * [How to Install Blender Plugins in Newer Versions](#how-to-install-blender-plugins-in-newer-versions)
  * [About Developing This Plugin](#about-developing-this-plugin)
    * [Notes](#notes)
  * [Open Source References](#open-source-references)
<!-- TOC -->

## Download

https://github.com/skys-mission/hbr-mmd-tools/releases

## Features

### MMD Lip-Sync Generation

Recognizes phoneme mouth shapes through the Vosk audio model and applies them to MMD standard models.

MMD model mouth shape morph keys recognized by this plugin: あ, い, う, え, お, ん. All except あ will be mapped to あ if they don't exist, and an error will occur if あ doesn't exist.

Warning: This function will overwrite the morph keyframes for あ, い, う, え, お, ん within the audio time range.

#### Usage

![lips_gen2.0f.webp](.img/lips_gen2.0f.webp)

1. Select an audio file in Audio Path (most common audio formats are likely to work, including mp4)
2. Select any parent level of an MMD model (note: if there are multiple meshes under the object containing these morph keys, all mesh morph keys will be modified)
3. It is recommended to open the system console to observe progress. Mac Blender does not have this feature. (Blender menu bar -> windows -> Toggle System Console)
4. Set parameters and click Generate (~~note that the current version will generate some readable cache files in the same directory as the audio file, which will not be cleared~~)
5. Wait for the mouse pointer to change from a number back to normal

#### Parameter Introduction

![lips3.0.webp](.img/lips3.0.webp)

- Start Frame: Which frame the audio starts from
- DB Threshold: DB noise reduction, increase if recognition is inaccurate, decrease if not recognized
- RMS Threshold: RMS noise reduction, increase if recognition is inaccurate, decrease if not recognized
- Delayed Opening: Delayed mouth opening ratio
- Speed Up Opening: Curve speed adjustment parameter from recognition start to delayed mouth opening
- Max Morph Value: Maximum threshold for morph keys

#### How to Adapt to Other Models

For example, with VRM, you need to find or set up A, E, I, O, U, N morph keys for your model, and copy and change them to MMD standard morph key names.

**At least あ is required to use this function**

- あ = A
- い = I
- う = U
- え = E
- お = O
- ん = N

If you don't know how to copy, refer to: [copy_shape_key.md](docs/copy_shape_key.md)

![lip_sync.webp](.img/lip_sync.webp)
Model source: KissshotSusu

### Random Blinking

Random blinking recognizes the まばたき morph key. If it doesn't exist, you need to convert or create this morph key yourself.

Warning: This function will overwrite the まばたき morph keyframes within the frame range.

1. Select any parent level of an MMD model (note: if there are multiple meshes under the object containing these morph keys, all mesh morph keys will be modified)
2. It is recommended to open the system console to observe progress. (Blender menu bar -> windows -> Toggle System Console)
3. Set parameters and click Generate
4. Wait for the mouse pointer to change from a number back to normal

![blink_args.webp](.img/blink_args.webp)

- blink interval: Blinking interval, unit seconds
- blinking wave ratio: Random ratio adjustable from 0.01-1

### Other Features

Documentation in progress...

## Support

### Blender Version Compatibility

- Mainly supported versions (I will test them)
    - 3.6, 4.2
- Versions that might work
    - Greater than or equal to 3.6
- Planned supported versions
    - Next Blender LTS version
- Not planned to support
    - Less than 3.6

### Operating System Compatibility

- Currently supported
    - windows-x64
- Possibly supported
    - macos-arm64
- Not planned to support
    - linux (unless major changes occur, not planned to support)

## How to Install Blender Plugins in Newer Versions

Reference: https://docs.blender.org/manual/en/4.2/editors/preferences/addons.html#prefs-extensions-install-legacy-addon

## About Developing This Plugin

### Notes

- blender 3.6-4.4 may require numba library: version <= 0.60.0 (other Blender versions not yet confirmed)

## Open Source References

| Project | Link | License |
|----------------------------|--------------------------------------------------|----------------------------------------|
| FFmpeg | https://github.com/FFmpeg/FFmpeg | GPLv3 (tools embedded in Releases use this license, no ffmpeg code in repository) |
| ~~Vosk-API and Vosk AI Model~~ | ~~https://github.com/alphacep/vosk-api~~ | Apache-2.0 |
| ~~CMU Dict~~ | ~~http://www.speech.cs.cmu.edu/cgi-bin/cmudict~~ | 2-Clause BSD License |
| ~~gout-vosk tool~~ | ~~https://github.com/skys-mission/gout~~ | GPLv3 |
