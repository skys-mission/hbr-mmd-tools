# HBR MMD Tools

[![Pylint](https://github.com/skys-mission/hbr-mmd-tools/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/skys-mission/hbr-mmd-tools/actions/workflows/pylint.yml)
[![CodeQL Advanced](https://github.com/skys-mission/hbr-mmd-tools/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/skys-mission/hbr-mmd-tools/actions/workflows/codeql.yml)
[![Bandit](https://github.com/skys-mission/hbr-mmd-tools/actions/workflows/bandit.yml/badge.svg)](https://github.com/skys-mission/hbr-mmd-tools/actions/workflows/bandit.yml)

他の言語：[English](README.md), [简体中文](README_zh.md)

MMD ワークフロー向けの Blender アドオンです。主な機能は MMD 口形生成、ランダムまばたき、関連補助ツールです。

このプロジェクトは `HBR MMD Tools` に改名しました。旧名は `whisky_helper_for_blender` です。

`HBR` は `Half-Bottled Reverie` に由来し、`MMD Tools` は現在の機能と用途をより直接的に表しています。

<!-- TOC -->
* [HBR MMD Tools](#hbr-mmd-tools)
  * [ダウンロード](#ダウンロード)
  * [機能](#機能)
    * [MMD口形生成](#mmd口形生成)
      * [使用方法](#使用方法)
      * [パラメータ説明](#パラメータ説明)
      * [他のモデルへの適応方法](#他のモデルへの適応方法)
    * [ランダムまばたき](#ランダムまばたき)
    * [その他の機能](#その他の機能)
  * [サポート](#サポート)
    * [Blenderバージョン互換性](#blenderバージョン互換性)
    * [オペレーティングシステム互換性](#オペレーティングシステム互換性)
  * [新バージョンでのBlenderプラグインのインストール方法](#新バージョンでのblenderプラグインのインストール方法)
  * [このプラグインの開発について](#このプラグインの開発について)
    * [注意事項](#注意事項)
  * [オープンソースリファレンス](#オープンソースリファレンス)
<!-- TOC -->

## ダウンロード

https://github.com/skys-mission/hbr-mmd-tools/releases

## 機能

### MMD口形生成

Vosk音声モデルを通じて音素の口形を認識し、MMD標準モデルに追加します。

本プラグインが認識するMMDモデルの口形モーフキー名：あ、い、う、え、お、ん。あ以外がない場合はすべてあに変更され、あがない場合はエラーになります。

警告：この機能は音声時間範囲内のあ、い、う、え、お、んモーフキーフレームを上書きします。

#### 使用方法

![lips_gen2.0f.webp](.img/lips_gen2.0f.webp)

1. Audio Pathで音声ファイルを選択（一般的な音声ファイルは大概使用可能、mp4を含む）
2. MMDモデルの任意の階層の親を選択（注意：オブジェクト下にこれらのモーフキーを含む複数のメッシュがある場合、すべてのメッシュのモーフキーが変更されます）
3. システムコンソールを開いて進捗を確認することを推奨します。Mac版Blenderにはこの機能がありません。（Blenderメニューバー->windows->Toggle System Console）
4. パラメータを設定し、生成をクリック（~~現在のバージョンでは音声ファイルと同じディレクトリに読み取り可能なキャッシュファイルが生成され、クリアされないことに注意してください~~）
5. マウスポインタが数字から通常に戻るまで待機

#### パラメータ説明

![lips3.0.webp](.img/lips3.0.webp)

- Start Frame: 音声がどのフレームから始まるか
- DB Threshold: DBノイズリダクション、認識が不正確な場合は上げる、認識できない場合は下げる
- RMS Threshold: RMSノイズリダクション、認識が不正確な場合は上げる、認識できない場合は下げる
- Delayed Opening: 遅延口開き比率
- Speed Up Opening: 認識開始から遅延口開きまでのカーブ速度調整パラメータ
- Max Morph Value: モーフキーの最大閾値

#### 他のモデルへの適応方法

例えばVRMの場合、モデルのA、E、I、O、U、Nのモーフキーを見つけるか設定し、MMD標準モーフキー名にコピーして変更する必要があります。

**本機能を使用するには少なくともあが必要です**

- あ = A
- い = I
- う = U
- え = E
- お = O
- ん = N

コピー方法が分からない場合は参考：[copy_shape_key.md](docs/copy_shape_key.md)

![lip_sync.webp](.img/lip_sync.webp)
モデル出典：KissshotSusu

### ランダムまばたき

ランダムまばたきはまばたきのモーフキーを認識します。存在しない場合は自分でこのモーフキーを変換または作成する必要があります。

警告：この機能はフレーム範囲内のまばたきモーフキーフレームを破壊します。

1. MMDモデルの任意の階層の親を選択（注意：オブジェクト下にこれらのモーフキーを含む複数のメッシュがある場合、すべてのメッシュのモーフキーが変更されます）
2. システムコンソールを開いて進捗を確認することを推奨します。（Blenderメニューバー->windows->Toggle System Console）
3. パラメータを設定し、生成をクリック
4. マウスポインタが数字から通常に戻るまで待機

![blink_args.webp](.img/blink_args.webp)

- blink interval: まばたき間隔、単位秒
- blinking wave ratio: ランダム比率0.01-1で調整可能

### その他の機能

ドキュメント作成中...

## サポート

### Blenderバージョン互換性

- 主要サポートバージョン（本人がテスト実施）
    - 3.6、4.2
- 動作可能性のあるバージョン
    - 3.6以上
- サポート予定のバージョン
    - 次のBlender LTSバージョン
- サポート予定なし
    - 3.6未満

### オペレーティングシステム互換性

- 現在サポート
    - windows-x64
- サポート可能性あり
    - macos-arm64
- サポート予定なし
    - linux（重大な変更がない限りサポート予定なし）

## 新バージョンでのBlenderプラグインのインストール方法

参考：https://docs.blender.org/manual/ja/4.2/editors/preferences/addons.html#prefs-extensions-install-legacy-addon

## このプラグインの開発について

### 注意事項

- blender3.6-4.4ではnumbaライブラリが必要な場合があります：バージョン<=0.60.0（その他のBlenderバージョンは未確認）

## オープンソースリファレンス

| プロジェクト | リンク | ライセンス |
|----------------------------|--------------------------------------------------|----------------------------------------|
| FFmpeg | https://github.com/FFmpeg/FFmpeg | GPLv3（Releasesに埋め込まれたツールはこのライセンスを使用、リポジトリにはffmpegコードなし） |
| ~~Vosk-APIとVosk AI Model~~ | ~~https://github.com/alphacep/vosk-api~~ | Apache-2.0 |
| ~~CMU Dict~~ | ~~http://www.speech.cs.cmu.edu/cgi-bin/cmudict~~ | 2-Clause BSD License |
| ~~gout-vosk tool~~ | ~~https://github.com/skys-mission/gout~~ | GPLv3 |
