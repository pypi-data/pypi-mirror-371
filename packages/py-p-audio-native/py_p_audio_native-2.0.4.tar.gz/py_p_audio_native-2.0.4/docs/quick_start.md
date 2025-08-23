# py-p-audio-native クイックスタート

## インストール

```bash
pip install py-p-audio-native
```

## 基本使用方法

### デバイス一覧取得

```python
import py_p_audio_native as ppa

# 利用可能な音声デバイス一覧
devices = ppa.list_devices()
for device in devices:
    print(f"[{device.index}] {device.name} ({device.api_name})")
    if device.max_input_channels > 0:
        print(f"  → 入力: {device.max_input_channels}ch")
    if device.max_output_channels > 0:
        print(f"  → 出力: {device.max_output_channels}ch")
```

### シンプル録音

```python
# デフォルトデバイスで5秒間録音
ppa.record(duration=5.0, output_file="recording.wav")

# デバイス指定録音
ppa.record(
    duration=10.0,
    output_file="recording.wav", 
    device_index=1,      # デバイス番号指定
    sample_rate=48000,   # 48kHz
    channels=2,          # ステレオ
    bit_depth=24         # 24ビット
)
```

### システム音声録音 (WASAPI ループバック)

```python
# コンピュータの音声出力を録音
ppa.record_loopback(duration=10.0, output_file="system_audio.wav")
```

### 音声再生

```python
# デフォルトデバイスで再生
ppa.play("recording.wav")

# デバイス指定再生
ppa.play("recording.wav", device_index=2)
```

## 詳細制御

### 高度な録音制御

```python
# Recorderクラスで詳細制御
recorder = ppa.Recorder(
    device_index=0,
    sample_rate=44100,
    channels=2,
    bit_depth=16,
    buffer_size=1024
)

# セットアップして録音開始
recorder.setup()
recorder.start_recording("continuous.wav")

# 録音状態監視
import time
while recorder.is_recording():
    time_elapsed = recorder.get_recording_time()
    peak_level = recorder.get_peak_level()
    print(f"録音時間: {time_elapsed:.1f}s, ピークレベル: {peak_level:.2f}")
    
    if time_elapsed >= 10.0:  # 10秒で停止
        recorder.stop_recording()
        break
    time.sleep(0.5)
```

### プログレスコールバック

```python
def progress_callback(progress, status):
    print(f"進捗: {progress:.1f}%, ステータス: {status}")

recorder = ppa.Recorder()
recorder.set_progress_callback(progress_callback)
recorder.record(duration=5.0, output_file="with_callback.wav")
```

## サンプルコード集

### 1. USB マイクを見つけて録音

```python
# USB マイクデバイスを検索
usb_device = ppa.find_device("USB")
if usb_device:
    print(f"USB マイク検出: {usb_device.name}")
    ppa.record(
        duration=5.0,
        output_file="usb_recording.wav",
        device_index=usb_device.index
    )
else:
    print("USB マイクが見つかりません")
```

### 2. ASIO デバイスで高音質録音

```python
devices = ppa.list_devices()
asio_devices = [d for d in devices if "ASIO" in d.api_name]

if asio_devices:
    device = asio_devices[0]
    print(f"ASIO デバイス使用: {device.name}")
    
    ppa.record(
        duration=10.0,
        output_file="asio_recording.wav",
        device_index=device.index,
        sample_rate=96000,      # 高サンプリング周波数
        channels=device.max_input_channels,  # 最大チャンネル数
        bit_depth=32            # 32ビット高音質
    )
```

### 3. 特定スピーカーのループバック録音

```python
devices = ppa.list_devices()
for device in devices:
    if device.max_output_channels > 0 and "Speakers" in device.name:
        print(f"スピーカー録音: {device.name}")
        
        ppa.record_loopback(
            duration=15.0,
            output_file="speaker_capture.wav",
            device_index=device.index,
            sample_rate=48000,
            channels=2,
            bit_depth=24
        )
        break
```

### 4. リアルタイム録音監視

```python
recorder = ppa.Recorder(device_index=0)
recorder.setup()
recorder.start_recording("monitored.wav")

print("録音中... (Ctrl+C で停止)")
try:
    while recorder.is_recording():
        level = recorder.get_peak_level()
        time_elapsed = recorder.get_recording_time()
        
        # ピークレベルを視覚化
        bar_length = int(level * 50)
        bar = "█" * bar_length + "░" * (50 - bar_length)
        print(f"\r時間: {time_elapsed:6.1f}s |{bar}| {level:.2f}", end="")
        
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n録音停止中...")
    recorder.stop_recording()
    print("録音完了")
```

### 5. 音声ファイル再生制御

```python
player = ppa.Player(device_index=1)  # 特定デバイス指定
player.play("music.wav")

# 再生制御
while player.is_playing():
    position = player.get_position()
    duration = player.get_duration()
    volume = player.get_volume()
    
    print(f"再生位置: {position:.1f}/{duration:.1f}s, 音量: {volume:.2f}")
    
    # 3秒後に一時停止
    if position >= 3.0 and not player.is_paused():
        player.pause()
        print("一時停止")
        time.sleep(2.0)
        player.play()  # 再開
        print("再開")
    
    time.sleep(0.5)
```

## エラーハンドリング

```python
try:
    ppa.record(duration=5.0, output_file="test.wav", device_index=999)
except ppa.DeviceError:
    print("指定されたデバイスが見つかりません")
except ppa.RecordingError:
    print("録音に失敗しました")
except ppa.FileError:
    print("ファイル操作でエラーが発生しました")
```

詳細な使用方法は `advanced_usage.md` を参照してください。