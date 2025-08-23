# py-p-audio-native 詳細使用方法

## デバイス選択と録音設定

### 1. 利用可能なデバイス一覧取得

```python
import py_p_audio_native as ppa

# すべての音声デバイス取得
devices = ppa.list_devices()
for device in devices:
    print(f"デバイス {device.index}: {device.name}")
    print(f"  API: {device.api_name}")
    print(f"  入力チャンネル: {device.max_input_channels}")
    print(f"  出力チャンネル: {device.max_output_channels}")
    print(f"  デフォルト入力: {device.is_default_input}")
    print(f"  デフォルト出力: {device.is_default_output}")
    print(f"  デフォルトサンプリング周波数: {device.default_sample_rate} Hz")
    print()
```

### 2. 特定デバイス検索

```python
# デバイス名での検索
usb_mic = ppa.find_device("USB")
if usb_mic:
    print(f"USB マイク見つかった: {usb_mic.name} (index: {usb_mic.index})")

# デバイス番号での検索
device_2 = ppa.get_device_info(2)
if device_2:
    print(f"デバイス 2: {device_2.name}")
```

## デバイス指定録音

### 1. シンプルな録音 (デバイス指定)

```python
# デバイス番号 0 を使って 5秒間録音
ppa.record(
    duration=5.0,           # 録音時間(秒)
    output_file="test.wav", # 出力ファイル
    device_index=0,         # デバイス番号
    sample_rate=44100,      # サンプリング周波数
    channels=2,             # チャンネル数 (1=モノラル, 2=ステレオ)
    bit_depth=16            # ビット深度 (16, 24, 32)
)
```

### 2. 高音質録音設定

```python
# ASIO デバイスで高音質録音
devices = ppa.list_devices()
asio_device = None
for device in devices:
    if "ASIO" in device.api_name:
        asio_device = device
        break

if asio_device:
    ppa.record(
        duration=10.0,
        output_file="high_quality.wav",
        device_index=asio_device.index,
        sample_rate=96000,      # 高サンプリング周波数
        channels=8,             # マルチチャンネル
        bit_depth=32            # 32ビット高音質
    )
```

### 3. クラスベースの詳細制御

```python
# Recorder クラスで詳細制御
recorder = ppa.Recorder(
    device_index=1,         # 入力デバイス指定
    sample_rate=48000,      # 48kHz
    channels=1,             # モノラル録音
    bit_depth=24,           # 24ビット
    buffer_size=512         # バッファサイズ (低レイテンシ用)
)

# セットアップ
recorder.setup()

# 継続録音開始
recorder.start_recording("continuous.wav")

# 録音状態監視
while recorder.is_recording():
    time = recorder.get_recording_time()
    level = recorder.get_peak_level()
    print(f"録音時間: {time:.1f}秒, ピークレベル: {level:.2f}")
    
    # 10秒で停止
    if time >= 10.0:
        recorder.stop_recording()
        break
    
    time.sleep(0.1)

print("録音完了")
```

## プログレスコールバック付き録音

```python
def progress_callback(progress, status):
    """録音進捗コールバック"""
    print(f"進捗: {progress:.1f}%, ステータス: {status}")

# コールバック付き録音
recorder = ppa.Recorder(device_index=0, sample_rate=44100, channels=2)
recorder.set_progress_callback(progress_callback)
recorder.record(duration=5.0, output_file="with_callback.wav")
```

## システム音声録音 (WASAPI ループバック)

### 1. デフォルト出力デバイスの録音

```python
# システムの音声出力を録音
ppa.record_loopback(
    duration=10.0,
    output_file="system_audio.wav",
    device_index=None,      # デフォルト出力デバイス
    sample_rate=44100,
    channels=2,
    bit_depth=16
)
```

### 2. 特定出力デバイスのループバック録音

```python
# 出力デバイス一覧から選択
devices = ppa.list_devices()
for device in devices:
    if device.max_output_channels > 0 and "Speakers" in device.name:
        print(f"スピーカーデバイス: {device.index} - {device.name}")
        
        # このデバイスの出力をループバック録音
        loopback = ppa.LoopbackRecorder(
            device_index=device.index,
            sample_rate=48000,
            channels=2,
            bit_depth=24
        )
        
        # サイレンス検出設定
        loopback.setup()
        loopback.set_silence_threshold(0.01)  # 1% 未満をサイレンス
        
        loopback.start_recording("speaker_output.wav")
        
        # 録音監視
        while loopback.is_recording():
            silence_time = loopback.get_silence_duration()
            peak = loopback.get_peak_level()
            
            print(f"サイレンス時間: {silence_time:.1f}秒, ピーク: {peak:.2f}")
            
            # 5秒間サイレンスで自動停止
            if silence_time >= 5.0:
                loopback.stop_recording()
                print("サイレンス検出により録音停止")
                break
                
            time.sleep(0.5)
        break
```

## マルチデバイス同時録音

```python
import threading
import time

def record_device(device_index, filename, duration=10.0):
    """デバイス別録音関数"""
    try:
        recorder = ppa.Recorder(
            device_index=device_index,
            sample_rate=44100,
            channels=2,
            bit_depth=16
        )
        recorder.record(duration, filename)
        print(f"デバイス {device_index} 録音完了: {filename}")
    except Exception as e:
        print(f"デバイス {device_index} エラー: {e}")

# 複数デバイス同時録音
devices = ppa.list_devices()
input_devices = [d for d in devices if d.max_input_channels > 0]

threads = []
for i, device in enumerate(input_devices[:3]):  # 最大3デバイス
    filename = f"device_{device.index}_recording.wav"
    thread = threading.Thread(
        target=record_device,
        args=(device.index, filename, 5.0)
    )
    threads.append(thread)
    thread.start()
    print(f"デバイス {device.index} 録音開始")

# 全デバイス録音完了待機
for thread in threads:
    thread.join()

print("全デバイス録音完了")
```

## 音声再生とデバイス指定

```python
# 特定の出力デバイスで再生
devices = ppa.list_devices()
for device in devices:
    if device.max_output_channels > 0 and "Headphones" in device.name:
        print(f"ヘッドホンで再生: {device.name}")
        
        player = ppa.Player(device_index=device.index)
        player.play("test.wav")
        
        # 再生監視
        while player.is_playing():
            pos = player.get_position()
            duration = player.get_duration()
            print(f"再生位置: {pos:.1f}/{duration:.1f} 秒")
            time.sleep(1.0)
        
        break
```

## エラーハンドリング

```python
try:
    # 存在しないデバイスでの録音試行
    ppa.record(
        duration=5.0,
        output_file="test.wav",
        device_index=999  # 存在しないデバイス
    )
except ppa.RecordingError as e:
    print(f"録音エラー: {e}")
except ppa.DeviceError as e:
    print(f"デバイスエラー: {e}")
except Exception as e:
    print(f"予期しないエラー: {e}")
```

## パフォーマンス最適化

```python
# 低レイテンシ設定
recorder = ppa.Recorder(
    device_index=0,
    sample_rate=44100,
    channels=2,
    bit_depth=16,
    buffer_size=128     # 小さなバッファで低レイテンシ
)

# ASIO デバイス使用時の最適化
asio_devices = [d for d in ppa.list_devices() if "ASIO" in d.api_name]
if asio_devices:
    recorder = ppa.Recorder(
        device_index=asio_devices[0].index,
        sample_rate=int(asio_devices[0].default_sample_rate),
        channels=asio_devices[0].max_input_channels,
        bit_depth=32,
        buffer_size=64      # ASIO は非常に小さなバッファが可能
    )
```

## デバイス情報の詳細表示

```python
def show_device_details():
    """全デバイス情報の詳細表示"""
    devices = ppa.list_devices()
    
    print("=== 音声デバイス一覧 ===")
    print()
    
    input_devices = [d for d in devices if d.max_input_channels > 0]
    output_devices = [d for d in devices if d.max_output_channels > 0]
    
    print(f"入力デバイス ({len(input_devices)} 個):")
    for device in input_devices:
        marker = "★" if device.is_default_input else "  "
        print(f"{marker} [{device.index}] {device.name}")
        print(f"     API: {device.api_name}")
        print(f"     チャンネル数: {device.max_input_channels}")
        print(f"     推奨サンプリング周波数: {device.default_sample_rate} Hz")
        print()
    
    print(f"出力デバイス ({len(output_devices)} 個):")
    for device in output_devices:
        marker = "★" if device.is_default_output else "  "
        print(f"{marker} [{device.index}] {device.name}")
        print(f"     API: {device.api_name}")
        print(f"     チャンネル数: {device.max_output_channels}")
        print(f"     推奨サンプリング周波数: {device.default_sample_rate} Hz")
        print()

show_device_details()
```

これで、デバイスとチャンネルを詳細に指定した録音が可能です。WASAPI と ASIO の両方に対応し、マルチチャンネル、高音質録音、リアルタイム監視まで実装されています。