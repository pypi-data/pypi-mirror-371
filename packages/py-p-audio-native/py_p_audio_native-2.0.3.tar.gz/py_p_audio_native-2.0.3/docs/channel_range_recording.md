# チャンネル範囲指定録音

py-p-audio-native では、特定のチャンネル範囲を指定した録音が可能です。

## 基本的な使い方

### 1. チャンネル範囲指定録音

```python
import py_p_audio_native as ppa

# 1-6チャンネル（1〜6ch の合計6チャンネル）を録音
ppa.record(
    duration=10.0,
    output_file="channels_1_to_6.wav",
    device_index=2,           # ASIO デバイスなど
    start_channel=1,          # 開始チャンネル（1ベース）
    end_channel=6,            # 終了チャンネル（1ベース）
    sample_rate=48000,
    bit_depth=24
)

# 3-8チャンネル（3〜8ch の合計6チャンネル）を録音
ppa.record(
    duration=5.0,
    output_file="channels_3_to_8.wav",
    device_index=2,
    start_channel=3,          # チャンネル3から
    end_channel=8,            # チャンネル8まで
    sample_rate=44100,
    bit_depth=16
)
```

### 2. Recorder クラスでの詳細制御

```python
# 4-7チャンネル録音用のレコーダー作成
recorder = ppa.Recorder(
    device_index=2,           # マルチチャンネル対応デバイス
    sample_rate=96000,
    start_channel=4,          # 4chから
    end_channel=7,            # 7chまで（合計4チャンネル）
    bit_depth=32,
    buffer_size=512
)

recorder.setup()
recorder.start_recording("multi_channel_range.wav")

# 録音監視
import time
while recorder.is_recording():
    time_elapsed = recorder.get_recording_time()
    peak_level = recorder.get_peak_level()
    print(f"録音時間: {time_elapsed:.1f}s, ピークレベル: {peak_level:.2f}")
    
    if time_elapsed >= 30.0:  # 30秒で停止
        recorder.stop_recording()
        break
    time.sleep(0.5)

print("チャンネル範囲録音完了")
```

## 使用例

### 楽器別チャンネル録音

```python
# ASIO オーディオインターフェースでの楽器別録音
devices = ppa.list_devices()
asio_device = None
for device in devices:
    if "ASIO" in device.api_name and device.max_input_channels >= 8:
        asio_device = device
        break

if asio_device:
    print(f"使用デバイス: {asio_device.name} ({asio_device.max_input_channels}ch)")
    
    # ドラム (チャンネル 1-4)
    ppa.record(
        duration=60.0,
        output_file="drums_ch1_4.wav",
        device_index=asio_device.index,
        start_channel=1,
        end_channel=4,
        sample_rate=48000,
        bit_depth=24
    )
    
    # ギター・ベース (チャンネル 5-6)
    ppa.record(
        duration=60.0,
        output_file="guitar_bass_ch5_6.wav",
        device_index=asio_device.index,
        start_channel=5,
        end_channel=6,
        sample_rate=48000,
        bit_depth=24
    )
    
    # キーボード (チャンネル 7-8)
    ppa.record(
        duration=60.0,
        output_file="keyboard_ch7_8.wav",
        device_index=asio_device.index,
        start_channel=7,
        end_channel=8,
        sample_rate=48000,
        bit_depth=24
    )
```

### 同時録音（スレッド使用）

```python
import threading
import time

def record_channel_range(device_index, start_ch, end_ch, filename, duration=10.0):
    """チャンネル範囲録音関数"""
    try:
        recorder = ppa.Recorder(
            device_index=device_index,
            start_channel=start_ch,
            end_channel=end_ch,
            sample_rate=48000,
            bit_depth=24
        )
        recorder.setup()
        recorder.record(duration, filename)
        print(f"チャンネル {start_ch}-{end_ch} 録音完了: {filename}")
    except Exception as e:
        print(f"チャンネル {start_ch}-{end_ch} エラー: {e}")

# 複数チャンネル範囲の同時録音
device_index = 2  # ASIO デバイス

threads = []
recordings = [
    (1, 2, "stereo_ch1_2.wav"),      # ステレオペア1
    (3, 4, "stereo_ch3_4.wav"),      # ステレオペア2  
    (5, 8, "quad_ch5_8.wav"),        # クアッドチャンネル
]

for start_ch, end_ch, filename in recordings:
    thread = threading.Thread(
        target=record_channel_range,
        args=(device_index, start_ch, end_ch, filename, 15.0)
    )
    threads.append(thread)
    thread.start()
    print(f"チャンネル {start_ch}-{end_ch} 録音開始")

# 全録音完了待機
for thread in threads:
    thread.join()

print("全チャンネル範囲録音完了")
```

### プログレスコールバック付き

```python
def progress_callback(progress, status):
    """録音進捗コールバック"""
    print(f"チャンネル範囲録音 進捗: {progress:.1f}%, ステータス: {status}")

# コールバック付きチャンネル範囲録音
recorder = ppa.Recorder(
    device_index=2,
    start_channel=1,
    end_channel=6,
    sample_rate=44100,
    bit_depth=16
)

recorder.set_progress_callback(progress_callback)
recorder.record(duration=20.0, output_file="range_with_callback.wav")
```

## エラーハンドリング

```python
try:
    # 無効なチャンネル範囲
    ppa.record(
        duration=5.0,
        output_file="invalid_range.wav",
        device_index=2,
        start_channel=8,  # 終了チャンネルより大きい
        end_channel=4
    )
except ppa.RecordingError as e:
    print(f"録音エラー: {e}")
except ppa.DeviceError as e:
    print(f"デバイスエラー: {e}")

try:
    # デバイスの最大チャンネル数を超えた指定
    device = ppa.get_device_info(2)
    if device and device.max_input_channels < 8:
        print(f"デバイスの最大入力チャンネル数: {device.max_input_channels}")
        # 8チャンネル録音は不可
        
    ppa.record(
        duration=5.0,
        output_file="over_limit.wav",
        device_index=2,
        start_channel=1,
        end_channel=16  # デバイスの限界を超える
    )
except ppa.RecordingError as e:
    print(f"チャンネル数制限エラー: {e}")
```

## パフォーマンス最適化

### ASIO 使用時の推奨設定

```python
# ASIO デバイスでの高品質チャンネル範囲録音
asio_devices = [d for d in ppa.list_devices() if "ASIO" in d.api_name]

if asio_devices:
    device = asio_devices[0]
    
    recorder = ppa.Recorder(
        device_index=device.index,
        start_channel=1,
        end_channel=6,                    # 1-6チャンネル
        sample_rate=int(device.default_sample_rate),  # デバイス推奨値
        bit_depth=32,                     # 高品質
        buffer_size=64                    # ASIO 低レイテンシ
    )
    
    recorder.setup()
    recorder.start_recording("asio_optimized.wav")
```

### バッファサイズ調整

```python
# 用途別バッファサイズ
buffer_sizes = {
    "低レイテンシ": 64,      # リアルタイム用
    "標準": 512,             # 通常録音用
    "安定性重視": 2048       # 長時間録音用
}

recorder = ppa.Recorder(
    device_index=2,
    start_channel=1,
    end_channel=8,
    buffer_size=buffer_sizes["標準"]
)
```

## 注意事項

1. **チャンネル番号は1ベース**: start_channel=1 が最初のチャンネル
2. **デバイス制限**: 指定範囲がデバイスの最大チャンネル数を超えないよう確認
3. **ASIO推奨**: マルチチャンネル録音には ASIO デバイスが最適
4. **メモリ使用量**: 多チャンネル録音はメモリ消費量が増加
5. **ファイルサイズ**: チャンネル数に比例してファイルサイズが増加

この機能により、オリジナルの C++ 実装と同様の柔軟なチャンネル範囲指定録音が可能になります。