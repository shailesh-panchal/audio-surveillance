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

