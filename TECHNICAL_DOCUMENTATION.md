# QIRAT AI: Technical Documentation

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Core Algorithms](#core-algorithms)
3. [API Reference](#api-reference)
4. [Data Flow](#data-flow)
5. [Performance Considerations](#performance-considerations)
6. [Development Guidelines](#development-guidelines)
7. [Testing Strategy](#testing-strategy)

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │    │  Audio Capture  │    │  File Upload    │
│   (CLI/Web)     │───▶│   (Real-time)   │    │   (WAV/MP3)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Audio Processing Pipeline                    │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│  Audio Loading  │  Pitch Analysis │  Auto-tuning    │ Feedback  │
│  (librosa)      │  (piptrack)     │  (pitch_shift)  │ Generation│
└─────────────────┴─────────────────┴─────────────────┴───────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Output Generation                           │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│  Aligned Audio  │  Auto-tuned     │  Pitch Plots    │ Feedback  │
│  Files          │  Audio          │  (matplotlib)   │ Reports   │
└─────────────────┴─────────────────┴─────────────────┴───────────┘
```

### Module Dependencies

```
main.py
├── record_audio.py
├── analyze_pitch.py
│   ├── librosa
│   ├── numpy
│   └── matplotlib
├── feedback.py
└── streamlit (for web interface)
```

## 🧮 Core Algorithms

### 1. Pitch Extraction Algorithm

**Algorithm**: Probabilistic YIN (Piptrack)
**Implementation**: `librosa.piptrack()`

#### Mathematical Foundation
The pitch extraction uses the Probabilistic YIN algorithm, which:

1. **Computes autocorrelation** for each frame
2. **Applies cumulative mean normalization**
3. **Finds pitch candidates** using peak detection
4. **Selects optimal pitch** based on probability distribution

#### Code Implementation
```python
def extract_pitch_contour(audio_file, hop_length=512):
    y, sr = librosa.load(audio_file)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr, hop_length=hop_length)
    
    pitch_contour = []
    for i in range(pitches.shape[1]):
        index = magnitudes[:, i].argmax()
        pitch = pitches[index, i]
        pitch_contour.append(pitch)
    
    return np.array(pitch_contour), sr, hop_length
```

#### Parameters
- **hop_length**: Frame hop size (default: 512 samples)
- **frame_length**: Analysis frame length (default: 2048 samples)
- **fmin**: Minimum frequency (default: 50 Hz)
- **fmax**: Maximum frequency (default: 8000 Hz)

### 2. Audio Alignment Algorithm

**Algorithm**: Energy-based onset detection
**Implementation**: Custom alignment function

#### Process
1. **Compute energy envelope** of both audio signals
2. **Detect first non-silent frame** using threshold
3. **Calculate offset** between user and reference start points
4. **Align reference audio** to user start point

#### Code Implementation
```python
def align_by_first_word(user_file, ref_file, threshold=0.02):
    user_y, user_sr = librosa.load(user_file)
    ref_y, ref_sr = librosa.load(ref_file)
    
    # Find first non-silent frame in user
    user_energy = np.abs(user_y)
    user_start = int(np.argmax(user_energy > threshold))
    
    # Find first non-silent frame in reference
    ref_energy = np.abs(ref_y)
    ref_start = int(np.argmax(ref_energy > threshold))
    
    # Align reference to user start
    offset = max(0, ref_start - user_start)
    aligned_ref_y = ref_y[offset:offset+len(user_y)]
    
    return user_y, user_sr, aligned_ref_y, ref_sr
```

### 3. Auto-Tuning Algorithm

**Algorithm**: Frame-based pitch shifting
**Implementation**: `librosa.effects.pitch_shift()`

#### Process
1. **Extract pitch** from each frame
2. **Calculate pitch difference** between user and target
3. **Convert to semitones** using MIDI conversion
4. **Apply pitch shift** to each frame
5. **Reconstruct audio** with corrected pitch

#### Code Implementation
```python
def auto_tune_audio(audio_file, target_pitch_contour, hop_length=512):
    y, sr = librosa.load(audio_file)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr, hop_length=hop_length)
    
    corrected_audio = np.zeros_like(y)
    frame_length = hop_length
    
    for i in range(pitches.shape[1]):
        index = magnitudes[:, i].argmax()
        user_pitch = pitches[index, i]
        
        if user_pitch > 0 and target_pitch_contour[i] > 0:
            # Calculate pitch difference in semitones
            n_steps = librosa.hz_to_midi(target_pitch_contour[i]) - \
                     librosa.hz_to_midi(user_pitch)
            
            # Apply pitch shift to current frame
            start = i * hop_length
            end = min(len(y), start + frame_length)
            shifted = librosa.effects.pitch_shift(y[start:end], sr=sr, n_steps=n_steps)
            corrected_audio[start:end] += shifted
        else:
            # Keep original audio if no pitch detected
            start = i * hop_length
            end = min(len(y), start + frame_length)
            corrected_audio[start:end] += y[start:end]
    
    return corrected_audio, sr
```

## 📚 API Reference

### analyze_pitch.py

#### `extract_pitch_contour(audio_file, hop_length=512)`
Extracts pitch contour from audio file using librosa's piptrack.

**Parameters:**
- `audio_file` (str): Path to audio file
- `hop_length` (int): Frame hop size in samples

**Returns:**
- `pitch_contour` (np.ndarray): Array of pitch values in Hz
- `sr` (int): Sample rate
- `hop_length` (int): Hop length used

**Example:**
```python
pitch_contour, sr, hop = extract_pitch_contour("audio.wav", hop_length=512)
```

#### `plot_pitch_contours(user_pitch, orig_pitch, hop_length, sr)`
Plots pitch contours for comparison.

**Parameters:**
- `user_pitch` (np.ndarray): User pitch contour
- `orig_pitch` (np.ndarray): Reference pitch contour
- `hop_length` (int): Frame hop size
- `sr` (int): Sample rate

#### `compare_pitch_contours(user_pitch, orig_pitch)`
Compares two pitch contours and returns difference.

**Parameters:**
- `user_pitch` (np.ndarray): User pitch contour
- `orig_pitch` (np.ndarray): Reference pitch contour

**Returns:**
- `diff` (np.ndarray): Pitch difference array

#### `auto_tune_audio(audio_file, target_pitch_contour, hop_length=512)`
Auto-tunes audio to match target pitch contour.

**Parameters:**
- `audio_file` (str): Path to audio file
- `target_pitch_contour` (np.ndarray): Target pitch values
- `hop_length` (int): Frame hop size

**Returns:**
- `corrected_audio` (np.ndarray): Auto-tuned audio
- `sr` (int): Sample rate

#### `align_by_first_word(user_file, ref_file, threshold=0.02)`
Aligns reference audio to user audio by first word detection.

**Parameters:**
- `user_file` (str): Path to user audio
- `ref_file` (str): Path to reference audio
- `threshold` (float): Energy threshold for onset detection

**Returns:**
- `user_y` (np.ndarray): User audio
- `user_sr` (int): User sample rate
- `aligned_ref_y` (np.ndarray): Aligned reference audio
- `ref_sr` (int): Reference sample rate

### feedback.py

#### `generate_feedback(diff, hop_length, sr, threshold=50)`
Generates feedback based on pitch differences.

**Parameters:**
- `diff` (np.ndarray): Pitch difference array
- `hop_length` (int): Frame hop size
- `sr` (int): Sample rate
- `threshold` (float): Feedback threshold in Hz

**Returns:**
- `feedback` (list): List of (timestamp, message) tuples

### record_audio.py

#### `record_audio(filename, duration=10, fs=44100, channels=1)`
Records audio from microphone.

**Parameters:**
- `filename` (str): Output file path
- `duration` (int): Recording duration in seconds
- `fs` (int): Sample rate in Hz
- `channels` (int): Number of audio channels

## 🔄 Data Flow

### 1. Audio Input Flow

```
User Input (CLI/Web) → Audio Capture → File Storage → Audio Loading
```

### 2. Processing Flow

```
Audio Loading → Pitch Extraction → Pitch Comparison → Feedback Generation
     ↓              ↓                    ↓                    ↓
Alignment ←─── Auto-tuning ←─── Pitch Analysis ←─── Deviation Detection
```

### 3. Output Flow

```
Processed Audio → File Generation → Playback/Display → User Feedback
```

## ⚡ Performance Considerations

### Computational Complexity

#### Pitch Extraction
- **Time Complexity**: O(n × log(n)) per frame
- **Space Complexity**: O(n) where n is frame length
- **Optimization**: Use smaller hop_length for real-time processing

#### Auto-tuning
- **Time Complexity**: O(m × n) where m is number of frames, n is frame length
- **Space Complexity**: O(n) for audio buffer
- **Optimization**: Process frames in batches

### Memory Management

#### Audio Buffering
```python
# Efficient audio processing with chunking
chunk_size = 1024 * 512  # 512 frames
for i in range(0, len(audio), chunk_size):
    chunk = audio[i:i+chunk_size]
    # Process chunk
```

#### File I/O Optimization
- Use `soundfile` for efficient WAV reading/writing
- Implement streaming for large files
- Use temporary files for intermediate processing

### Real-time Processing

#### WebRTC Integration
```python
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []
        self.buffer_size = 1024
    
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray()
        self.frames.append(pcm)
        return frame
```

## 🧪 Development Guidelines

### Code Style

#### Python Conventions
- Follow PEP 8 style guide
- Use type hints for function parameters
- Add comprehensive docstrings
- Use meaningful variable names

#### Example
```python
def extract_pitch_contour(
    audio_file: str, 
    hop_length: int = 512
) -> Tuple[np.ndarray, int, int]:
    """
    Extract pitch contour from audio file using librosa's piptrack.
    
    Args:
        audio_file: Path to the audio file
        hop_length: Frame hop size in samples
        
    Returns:
        Tuple containing (pitch_contour, sample_rate, hop_length)
        
    Raises:
        FileNotFoundError: If audio file doesn't exist
        ValueError: If audio file is corrupted
    """
    # Implementation
```

### Error Handling

#### Robust Error Handling
```python
def safe_audio_processing(audio_file: str) -> Optional[np.ndarray]:
    try:
        y, sr = librosa.load(audio_file)
        return y
    except FileNotFoundError:
        logger.error(f"Audio file not found: {audio_file}")
        return None
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        return None
```

### Logging

#### Structured Logging
```python
import logging

logger = logging.getLogger(__name__)

def process_audio(audio_file: str):
    logger.info(f"Starting audio processing: {audio_file}")
    try:
        # Processing logic
        logger.info("Audio processing completed successfully")
    except Exception as e:
        logger.error(f"Audio processing failed: {e}")
        raise
```

## 🧪 Testing Strategy

### Unit Testing

#### Test Structure
```
tests/
├── test_analyze_pitch.py
├── test_feedback.py
├── test_record_audio.py
└── test_integration.py
```

#### Example Test
```python
import unittest
import numpy as np
from analyze_pitch import extract_pitch_contour

class TestPitchExtraction(unittest.TestCase):
    def test_extract_pitch_contour(self):
        # Create synthetic audio with known pitch
        sr = 44100
        duration = 1.0
        frequency = 440.0  # A4 note
        
        t = np.linspace(0, duration, int(sr * duration))
        audio = np.sin(2 * np.pi * frequency * t)
        
        # Save temporary audio file
        sf.write("test_audio.wav", audio, sr)
        
        # Extract pitch
        pitch_contour, extracted_sr, hop_length = extract_pitch_contour("test_audio.wav")
        
        # Assertions
        self.assertEqual(extracted_sr, sr)
        self.assertGreater(len(pitch_contour), 0)
        self.assertAlmostEqual(np.mean(pitch_contour), frequency, delta=50)
```

### Integration Testing

#### End-to-End Testing
```python
def test_complete_pipeline():
    # Test complete audio processing pipeline
    ref_file = "test_reference.wav"
    user_file = "test_user.wav"
    
    # Run complete pipeline
    result = run_pipeline(ref_file, user_file)
    
    # Verify outputs
    assert result['feedback'] is not None
    assert result['auto_tuned_audio'] is not None
    assert os.path.exists(result['output_file'])
```

### Performance Testing

#### Benchmark Testing
```python
import time

def benchmark_pitch_extraction():
    start_time = time.time()
    pitch_contour, sr, hop = extract_pitch_contour("large_audio.wav")
    end_time = time.time()
    
    processing_time = end_time - start_time
    assert processing_time < 5.0  # Should complete within 5 seconds
```

## 📊 Monitoring and Metrics

### Key Performance Indicators

#### Processing Metrics
- **Pitch extraction time**: Target < 1 second per minute of audio
- **Auto-tuning accuracy**: Pitch correction within ±5 Hz
- **Memory usage**: < 500MB for 10-minute audio files
- **CPU usage**: < 80% during processing

#### Quality Metrics
- **Pitch detection accuracy**: > 95% for clean audio
- **Alignment precision**: < 100ms offset
- **Feedback relevance**: > 90% user satisfaction

### Logging and Monitoring

#### Structured Logging
```python
import logging
import json

def log_processing_metrics(operation: str, duration: float, success: bool):
    log_entry = {
        "timestamp": time.time(),
        "operation": operation,
        "duration": duration,
        "success": success,
        "version": "1.0.0"
    }
    
    logger.info(json.dumps(log_entry))
```

---

This technical documentation provides comprehensive information for developers working with the QIRAT AI system. For additional details, refer to the source code comments and inline documentation. 