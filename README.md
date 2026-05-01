# Audio Surveillance System

## Introduction

This project implements an audio surveillance system that monitors audio input in real-time, detects speech and classifies sounds to identify potential security threats. It uses speech recognition to detect distress keywords and sound classification to identify suspicious audio events, triggering alerts and actions accordingly.

## Solution Approach

The system employs a multi-threaded architecture to process audio streams concurrently. It captures audio from a microphone, processes it in chunks, and applies two AI models: Vosk for speech-to-text recognition and YAMNet for sound classification. Detected events are evaluated against predefined rules to decide on alerts.

Key features:
- Real-time audio processing
- Multi-language speech recognition support
- Sound event detection
- Configurable alert thresholds
- Modular design for easy extension

## Architecture

The system consists of the following components:

1. **Audio Capture**: Uses `sounddevice` to capture raw audio from the microphone in real-time.
2. **Audio Processing Queue**: A thread-safe queue to buffer audio chunks for processing.
3. **Speech Recognition (Vosk)**: Recognizes spoken words and detects keywords indicating distress.
4. **Sound Classification (YAMNet)**: Classifies audio into sound categories and identifies suspicious events.
5. **Decision Engine**: Evaluates detections against rules to trigger alerts.
6. **Action Trigger**: Simulates or executes responses like alarms or notifications.

### Data Flow
1. Audio input → Queue
2. Worker thread processes queue:
   - Sends chunks to Vosk for text recognition
   - Sends chunks to YAMNet for sound classification
3. Detections → Decision Engine → Actions

## Components

### main.py
- Main script that initializes models, starts audio stream, and manages threads.
- Configurable language selection for speech recognition.
- Defines alert keywords and confidence thresholds.

### vosklib.py
- Wrapper for Vosk speech recognition.
- Supports multiple languages via model paths.
- Processes audio bytes and returns recognized text.

### yamnet.py
- Interface for YAMNet sound classification.
- Loads the TensorFlow Hub model.
- Classifies audio and returns class ID with confidence.

### Models
- **Vosk Models**: Language-specific models stored in `model/` directory.
- **YAMNet Model**: Pre-trained sound classification model from TensorFlow Hub.

## Setup

1. **Environment**:
   - Python 3.8+
   - Virtual environment: `audio_env/`

2. **Dependencies**:
   - Install required packages: `pip install sounddevice vosk tensorflow tensorflow-hub numpy`

3. **Models**:
   - Download Vosk models from https://alphacephei.com/vosk/models
   - Place in `model/` folder (e.g., `vosk-model-small-en-us-0.15` for English)
   - YAMNet model is downloaded automatically via TensorFlow Hub

4. **Run**:
   - Activate environment: `audio_env\Scripts\activate`
   - Run: `python main.py --device-ip <ip>`

## Usage

- Start the system; it will begin monitoring audio.
- Speak keywords like "help", "fire", "stop", "danger" to trigger speech alerts.
- Play sounds above confidence threshold (0.6) to trigger sound alerts.
- Alerts are printed to console; extend `trigger_action()` for real actions.

### Configuration
- Change `LANGUAGE` in `main.py` to switch languages (requires corresponding model).
- Adjust `keywords` and `confidence > 0.6` in `decision_engine()` for custom rules.

## Key Outcomes and Impact

### Outcomes
- **Real-Time Detection**: Enables immediate response to potential threats through continuous audio monitoring.
- **Multi-Modal Analysis**: Combines speech and sound detection for comprehensive surveillance.
- **Scalability**: Modular architecture allows easy addition of new languages, models, and detection rules.
- **Accuracy**: Leverages state-of-the-art AI models (Vosk and YAMNet) for reliable recognition and classification.
- **Cost-Effectiveness**: Uses open-source tools and runs on standard hardware, reducing deployment costs.

### Impact
- **Enhanced Security**: Provides an additional layer of protection in surveillance scenarios, such as homes, offices, or public spaces.
- **Rapid Response**: Reduces response time to incidents by automating detection and alerting.
- **Accessibility**: Supports multiple languages, making it usable in diverse environments.
- **Data-Driven Insights**: Can be extended to log and analyze audio data for pattern recognition and predictive analytics.
- **Societal Benefits**: Contributes to safer communities by enabling proactive monitoring without constant human oversight.

## License

This project uses open-source models and libraries. Ensure compliance with their licenses (Apache 2.0 for Vosk and YAMNet).
