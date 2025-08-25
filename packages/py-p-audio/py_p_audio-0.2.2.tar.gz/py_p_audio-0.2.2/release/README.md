# p-audio - Audio Recording Tool

PortAudio + ASIO対応のオーディオ録音・再生ツール（Windows専用）

## 機能

- **デバイス列挙**: WASAPI・ASIOデバイスの表示
- **オーディオ録音**: WASAPIループバック録音とASIO録音
- **オーディオ再生**: WAVファイル再生
- **Q キー終了**: 録音・再生中にQキーで停止

## 使い方

```cmd
# デバイス一覧表示
p-audio.exe /d

# 音声ファイル再生
p-audio.exe /p "音楽ファイル.wav"

# 録音（デフォルトデバイス）
p-audio.exe /r "録音ファイル.wav"

# 録音（デバイス・チャンネル指定）
p-audio.exe /r "録音ファイル.wav" /dv 2,1-2
```

## チャンネル指定

- 1ベースのインデックス（1-2で1チャンネル目と2チャンネル目）
- ASIO: チャンネル指定可能
- WASAPIループバック: 通常1-2で使用

## 動作要件

- Windows 10/11 (64bit)
- ASIOデバイス使用時: ASIOドライバー（ASIO4ALL等）

## ライセンス

PortAudio License, ASIO SDK License