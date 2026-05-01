# Audio Surveillance System - Key Points

## System Architecture

### Core Components
- **Speech Recognition (Vosk)**: Detects distress keywords in multiple languages
- **Sound Classification (YAMNet)**: Identifies suspicious environmental sounds
- **RTSP/Microphone Input**: Processes audio from streaming sources or local microphone
- **Device Control**: Sends alerts/commands to IP-based devices (cameras, alarms)

---

## Key Features

### 1. Multi-Language Support
- **Supported Languages**: English, Hindi, English-India, Gujarati
- **Distress Keywords**:
  - English: "help", "fire", "stop", "danger"
  - Hindi: "मदद", "आग", "रुको", "खतरा"
  - Gujarati: "મદદ", "આગ", "બંધ કરો", "ખતરો"
- **Detection**: Real-time speech analysis with language identification

### 2. Sound Event Detection
- **YAMNet Classifier**: Identifies suspicious sounds with confidence scores
- **Filtering**:
  - Ignores speech-detected audio
  - Ignores silence/quiet environments
  - Triggers on suspicious sounds (confidence > 0.6)

### 3. Audio Input Modes
- **Microphone Mode**: Real-time local audio capture
- **RTSP Streaming**: Remote audio stream analysis from IP cameras
- **Configurable Parameters**:
  - Sample Rate: 16,000 Hz
  - Block Size: 8,000 samples

### 4. Device Integration
- **IP-Based Control**: Takes device IP as command-line argument
- **Credentials**: Supports digest authentication (configurable)
- **Action**: PTZ control commands (pan/tilt/zoom operations)

---

## Command-Line Usage

### Basic Help
```bash
python main.py --help
```

### Microphone Mode with Device Control
```bash
python main.py --device-ip 192.168.111.55
```

### RTSP Stream with Device Control
```bash
python main.py --rtsp-url rtsp://stream_address:port --device-ip 192.168.111.55
```

---

## Alert Triggering Conditions

### Speech-Based Alerts
✓ Distress keyword detected in supported language
✓ Normalized text matching (handles special characters, accents)
✓ Language-specific keyword set

### Sound-Based Alerts
✓ Environmental sound with confidence > 0.6
✓ Excludes speech and silence classes
✓ Triggers camera/alarm actions

---

## Action Flow

1. **Audio Capture** → Queue audio data
2. **Speech Processing** → Vosk recognition (all configured languages)
3. **Sound Classification** → YAMNet analysis
4. **Decision Engine** → Evaluate keywords & sound events
5. **Action Trigger** → Send HTTP command to device IP

---

## Configuration Options

- `RUN_ALL_LANGUAGES`: Process all languages simultaneously (True/False)
- `LANGUAGE`: Single language mode if RUN_ALL_LANGUAGES=False
- `LISTEN_LANGUAGES`: Dynamically configured list of active languages
- `DEVICE_IP`: Set via `--device-ip` argument (required for device control)
- `RTSP_URL`: Set via `--rtsp-url` argument (optional, defaults to microphone)

---

## System Benefits

✅ Real-time multi-language distress detection
✅ Environmental threat identification
✅ Remote audio streaming capability
✅ IP-based device integration
✅ Configurable sensitivity & filtering
✅ Low resource footprint (small models)
✅ Modular architecture (easy to extend)

---

# NPU Deployment Guide

## What is NPU (Neural Processing Unit)?
NPU is specialized hardware optimized for AI/ML inference tasks. Running your audio surveillance on NPU provides:
- **10-100x faster inference** compared to CPU
- **Significantly lower power consumption** (critical for edge devices)
- **Reduced CPU utilization** (frees CPU for other tasks)
- **Better thermal efficiency**

---

## NPU Platforms Supported

### Intel Neural Accelerator
- **Devices**: Intel Core Ultra (with AI Boost NPU)
- **Framework**: Intel OpenVINO Toolkit
- **Estimated Speedup**: 5-10x faster

### Qualcomm Snapdragon
- **Devices**: Smartphones, edge devices, IoT boards
- **Framework**: Qualcomm QNN (Qualcomm Neural Network)
- **Estimated Speedup**: 10-30x faster

### ARM Mali NPU
- **Devices**: Arm-based processors (MediaTek, Samsung Exynos)
- **Framework**: ARM NN, ONNX Runtime
- **Estimated Speedup**: 8-15x faster

### Google Coral TPU
- **Devices**: Google Coral Dev Board, USB Accelerator
- **Framework**: TensorFlow Lite
- **Estimated Speedup**: 20-50x faster

### Apple Neural Engine
- **Devices**: iPhone, iPad, Mac with M-series chips
- **Framework**: Core ML
- **Estimated Speedup**: 10-30x faster

### Nvidia Jetson
- **Devices**: Jetson Nano, Xavier, Orin
- **Framework**: TensorRT, CUDA
- **Estimated Speedup**: 15-40x faster

---

## Model Conversion Pipeline

### Step 1: Current Architecture
```
Vosk (.fst models) → Python wrapper
YAMNet (SavedModel) → TensorFlow/Keras
```

### Step 2: Conversion Process

#### For Vosk on NPU:
- Vosk uses KALDI models (unlikely direct NPU support)
- **Solution**: Use alternative speech recognition optimized for NPU
  - TensorFlow Lite Speech Recognition
  - Qualcomm Vosk-alternative
  - ONNX Runtime speech models

#### For YAMNet on NPU:
```
1. Export SavedModel → ONNX format
2. ONNX → Framework-specific format:
   - OpenVINO IR (for Intel)
   - TFLite (for Google Coral)
   - ONNX Runtime (universal)
3. Quantize: FP32 → INT8 (4x smaller, faster)
4. Optimize: Prune, fuse operations
```

### Step 3: Framework Selection

| NPU | Framework | Vosk Alternative | YAMNet Path |
|-----|-----------|------------------|------------|
| Intel | OpenVINO | ONNX Speech Model | OpenVINO IR |
| Qualcomm | QNN | QNN Speech Model | QNN converted |
| Google Coral | TFLite | TFLite Speech | TFLite optimized |
| Nvidia | TensorRT | ONNX → TensorRT | TensorRT optimized |
| Apple | Core ML | Core ML Speech | Core ML converted |

---

## Implementation Tips for NPU

### 1. **Quantization Strategy**
```python
# INT8 Quantization (recommended for NPU)
# Reduces model size by 4x, slightly faster on NPU
# Loss: minimal accuracy impact (<2%)

# Example: YAMNet quantization
converter = tf.lite.TFLiteConverter.from_saved_model(yamnet_model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS_INT8
]
quantized_model = converter.convert()
```

### 2. **Model Splitting**
- Deploy **YAMNet on NPU** (heavy inference task)
- Deploy **Vosk on CPU** (lightweight, sequential processing)
- Or use NPU speech alternative for end-to-end acceleration

### 3. **Batch Processing**
```python
# Accumulate audio chunks and process in batches
# More efficient for NPU inference
batch_size = 5  # Process 5 audio frames at once
audio_batch = []

for audio_chunk in audio_stream:
    audio_batch.append(audio_chunk)
    if len(audio_batch) >= batch_size:
        results = npu_engine.process_batch(audio_batch)
        audio_batch = []
```

### 4. **Asynchronous Inference**
```python
# Use threading to avoid blocking audio capture
# While NPU processes, CPU captures next audio chunk
import concurrent.futures

executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

def async_npu_inference(audio_data):
    return npu_engine.process(audio_data)

# Submit to NPU while reading next chunk
future = executor.submit(async_npu_inference, current_chunk)
next_chunk = read_audio()
result = future.result()  # Wait for NPU result
```

### 5. **Memory Optimization**
- Pre-allocate buffers for input/output
- Avoid model reloading (keep in memory)
- Use memory pools for audio buffers
- Expected memory: 50-100 MB (vs 300-400 MB on CPU)

---

## Performance Expectations on NPU

### Latency Improvements
```
Current (CPU):
- Speech (Vosk): 100-200ms per chunk
- Sound (YAMNet): 150-300ms per chunk
- Total: ~400-500ms per decision

With NPU (YAMNet on NPU):
- Speech (Vosk): 100-200ms per chunk (CPU)
- Sound (YAMNet): 15-50ms per chunk (NPU)
- Total: ~150-250ms per decision
- Improvement: 2-3x faster

With Full NPU (speech + sound):
- Speech (optimized): 10-50ms (NPU)
- Sound (YAMNet): 15-50ms (NPU)
- Total: ~30-100ms per decision
- Improvement: 5-10x faster
```

### Power Consumption
```
CPU Only: ~5-15W (laptop/desktop)
CPU Only: ~1-3W (Raspberry Pi 4)

With NPU: ~2-8W reduction in CPU load
- Google Coral: 2W total
- Jetson Nano: 5W total
- Intel Neural: Minimal additional power
```

---

## Framework-Specific Setup

### **For Google Coral TPU** (Recommended for edge)
```bash
# Install Coral dependencies
pip install tensorflow-lite-runtime
pip install coral-python-adapter

# Convert YAMNet to quantized TFLite
converter = tf.lite.TFLiteConverter.from_saved_model(yamnet_model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS_INT8
]
converter.representative_dataset = calibration_dataset
quantized_tflite = converter.convert()

# Run inference on TPU
interpreter = tf.lite.Interpreter(
    model_path='yamnet_edgetpu.tflite',
    experimental_delegates=[coral.load_delegate('edgetpu.so')]
)
```

### **For Nvidia Jetson**
```bash
# Install Jetson libraries
pip install jetson-inference jetson-utils

# YAMNet with TensorRT
import tensorrt as trt
from tensorrt.parsers import UffParser

engine = trt.infer_engine_from_uff(
    model_data,
    parser=UffParser(),
    precision=trt.infer.DataType.INT8
)
```

### **For Intel OpenVINO**
```bash
# Install OpenVINO toolkit
pip install openvino

# Convert to OpenVINO IR format
from openvino.tools.mo import mo

mo(
    model_name='yamnet',
    input_model='yamnet.pb',
    data_type='int8',
    output_dir='ir_model'
)
```

---

## Potential Challenges & Solutions

| Challenge | Impact | Solution |
|-----------|--------|----------|
| Model incompatibility | Cannot run Vosk directly | Use TFLite/ONNX speech alternative |
| Latency with batching | Delayed alerts | Use single-sample async inference |
| Quantization accuracy | <2% accuracy loss | Test with quantized INT8 vs FP32 |
| Hardware availability | Cost/availability | Start with Google Coral (affordable) |
| Framework learning curve | Setup complexity | Use ONNX Runtime (universal) |
| Power limits | Thermal throttling | Monitor & set NPU frequency limits |

---

## Quick Start: NPU Deployment Checklist

- [ ] Choose NPU platform (Coral, Jetson, etc.)
- [ ] Install framework SDK & libraries
- [ ] Convert YAMNet to target format (TFLite, IR, etc.)
- [ ] Quantize models (INT8)
- [ ] Test inference latency
- [ ] Modify `yamnet.py` to use NPU backend
- [ ] Run full system test
- [ ] Profile power & thermal performance
- [ ] Optimize batch size & threading
- [ ] Deploy & monitor real-world performance

---

## Recommended NPU Setup for Your Project

**Best Value**: Google Coral USB Accelerator
- **Cost**: ~$75-100
- **Performance**: 10-15x faster YAMNet
- **Power**: <2W
- **Compatibility**: Works with any Linux/Windows/Mac
- **Setup Time**: ~30 minutes

**Best Performance**: Nvidia Jetson Nano
- **Cost**: ~$100-150
- **Performance**: 15-30x overall system speedup
- **Power**: 5W sustained
- **Compatibility**: Full TensorFlow/PyTorch support
- **Setup Time**: ~1-2 hours
