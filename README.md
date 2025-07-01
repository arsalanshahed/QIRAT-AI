# QIRAT AI: Audio Comparison & Auto-Tune System

## 📖 Overview

QIRAT AI is an advanced audio processing and analysis system designed for real-time pitch comparison, feedback generation, and auto-tuning capabilities. The system is particularly useful for vocal training, Quranic recitation practice, and any application requiring precise pitch matching against reference audio.

## 🎯 Purpose

The primary goal of QIRAT AI is to:
- **Compare user audio recordings** against reference audio files
- **Analyze pitch accuracy** and provide detailed feedback
- **Auto-tune user recordings** to match reference pitch contours
- **Provide real-time feedback** for vocal training and improvement
- **Support both command-line and web-based interfaces**

## ✨ Key Features

### 🎤 Audio Recording & Processing
- **Real-time audio recording** with configurable duration
- **Multiple input methods**: Direct recording, file upload, or web-based recording
- **High-quality audio processing** with support for various formats (WAV, MP3)
- **Automatic audio alignment** by detecting first words/sounds

### 🎵 Pitch Analysis & Comparison
- **Advanced pitch extraction** using librosa's piptrack algorithm
- **Real-time pitch contour analysis** with configurable hop length
- **Precise pitch difference calculation** between user and reference audio
- **Visual pitch contour plotting** for easy comparison

### 🎛️ Auto-Tuning Capabilities
- **Real-time pitch correction** using librosa's pitch_shift
- **Frame-by-frame pitch adjustment** for precise tuning
- **Preservation of audio quality** during correction process
- **Configurable correction parameters**

### 📊 Feedback System
- **Detailed pitch deviation feedback** with timestamps
- **Threshold-based feedback generation** (configurable sensitivity)
- **Segment-by-segment analysis** (5-second intervals)
- **Audio playback comparison** for problematic segments

### 🌐 Web Interface
- **Streamlit-based web application** for easy access
- **Real-time web-based recording** using WebRTC
- **Device selection capabilities** for multiple microphones
- **Interactive audio playback** and comparison

## 🏗️ System Architecture

### Core Components

```
QIRAT AI/
├── main.py              # Main command-line interface
├── frontend.py          # Streamlit web interface
├── analyze_pitch.py     # Core pitch analysis engine
├── feedback.py          # Feedback generation system
├── record_audio.py      # Audio recording utilities
└── requirements.txt     # Python dependencies
```

### Module Responsibilities

#### `main.py` - Command Line Interface
- **Entry point** for command-line usage
- **Orchestrates** the complete audio processing pipeline
- **Handles user input** for file paths and recording duration
- **Manages the workflow** from recording to feedback

#### `frontend.py` - Web Interface
- **Streamlit web application** for browser-based access
- **Real-time audio recording** using WebRTC
- **File upload capabilities** for reference and user audio
- **Interactive playback** of original, reference, and auto-tuned audio

#### `analyze_pitch.py` - Core Analysis Engine
- **Pitch extraction** using librosa's piptrack
- **Audio alignment** by first word detection
- **Auto-tuning implementation** with pitch shifting
- **Audio segmentation** for detailed analysis
- **Audio playback** and file management utilities

#### `feedback.py` - Feedback Generation
- **Pitch deviation analysis** with configurable thresholds
- **Timestamp-based feedback** generation
- **Customizable sensitivity** for feedback triggers

#### `record_audio.py` - Audio Recording
- **Real-time audio capture** using PyAudio
- **Configurable recording parameters** (duration, sample rate, channels)
- **WAV file output** with proper formatting

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Microphone access (for recording features)
- Internet connection (for web interface)

### Step 1: Clone the Repository
```bash
git clone https://github.com/arsalanshahed/QIRAT-AI.git
cd QIRAT-AI
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation
```bash
python -c "import librosa, streamlit, pyaudio; print('Installation successful!')"
```

## 📖 Usage Guide

### Command Line Interface

#### Basic Usage
```bash
python main.py
```

#### Interactive Workflow
1. **Enter reference file path** when prompted
2. **Specify recording duration** in seconds
3. **Record your audio** when the system starts recording
4. **Review feedback** and pitch analysis
5. **Listen to auto-tuned version** (optional)

#### Example Session
```
Enter path to reference file (e.g., C:/Users/ashah/Downloads/azan15.mp3): azan15.mp3
Enter recording duration in seconds (e.g., 120): 30
Recording for 30 seconds...
Recording finished.

--- FEEDBACK ---
Pitch off by 65.2 Hz at 2.34 sec
Pitch off by -78.1 Hz at 5.67 sec

Would you like to hear the auto-tuned version? (y/n): y
Playing auto-tuned audio...
```

### Web Interface

#### Starting the Web App
```bash
streamlit run frontend.py
```

#### Web Interface Workflow
1. **Upload reference audio** (WAV or MP3 format)
2. **Choose input method**:
   - **Record**: Use browser microphone for real-time recording
   - **Upload**: Upload pre-recorded audio file
3. **Process audio** automatically
4. **Compare results**:
   - Original user recording (aligned)
   - Reference audio (aligned)
   - Auto-tuned user audio

#### Device Selection (Advanced)
- If you have multiple microphones, you can specify the device ID
- Leave blank for default device selection

## 🔧 Technical Specifications

### Audio Processing Parameters
- **Sample Rate**: 44.1 kHz (configurable)
- **Hop Length**: 512 samples (default, configurable)
- **Frame Length**: 1024 samples
- **Audio Format**: WAV (16-bit PCM)

### Pitch Analysis Algorithm
- **Method**: librosa.piptrack (Probabilistic YIN)
- **Frequency Range**: 50 Hz - 8000 Hz
- **Resolution**: Frame-based analysis
- **Output**: Pitch contour in Hz

### Auto-Tuning Algorithm
- **Method**: librosa.effects.pitch_shift
- **Correction**: Frame-by-frame pitch adjustment
- **Preservation**: Original audio characteristics
- **Quality**: High-fidelity output

### Feedback System
- **Threshold**: 50 Hz (configurable)
- **Analysis**: Real-time pitch deviation detection
- **Output**: Timestamped feedback messages
- **Segmentation**: 5-second interval analysis

## 🎛️ Configuration Options

### Pitch Analysis Settings
```python
# In analyze_pitch.py
hop_length = 512  # Analysis frame hop length
threshold = 0.02  # Energy threshold for alignment
```

### Feedback Sensitivity
```python
# In feedback.py
threshold = 50  # Hz deviation threshold for feedback
```

### Recording Parameters
```python
# In record_audio.py
duration = 10    # Recording duration in seconds
fs = 44100       # Sample rate in Hz
channels = 1     # Number of audio channels
```

## 📊 Output Files

The system generates several output files during processing:

- `user_recorded.wav` - Original user recording
- `user_aligned.wav` - User audio aligned to reference
- `reference_aligned.wav` - Reference audio aligned to user
- `user_autotuned.wav` - Auto-tuned user audio
- `uploaded_ref.wav` - Uploaded reference file
- `temp_aligned_ref_*.wav` - Temporary alignment files

## 🔍 Troubleshooting

### Common Issues

#### Microphone Not Detected
- **Check system permissions** for microphone access
- **Verify microphone connection** and driver installation
- **Try different browsers** (Chrome, Firefox, Edge)
- **Check device manager** for audio input devices

#### Audio Quality Issues
- **Ensure high-quality reference audio** (44.1 kHz, 16-bit or higher)
- **Check microphone quality** and positioning
- **Minimize background noise** during recording

#### Web Interface Issues
- **Update streamlit**: `pip install --upgrade streamlit`
- **Clear browser cache** and restart browser
- **Check WebRTC support** in your browser

#### Pitch Analysis Errors
- **Verify audio file format** (WAV or MP3)
- **Check file corruption** by playing in media player
- **Ensure sufficient audio length** (minimum 1 second)

### Performance Optimization
- **Use SSD storage** for faster file I/O
- **Close other audio applications** during recording
- **Optimize hop_length** for your use case (smaller = more precise, larger = faster)

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

### Code Style
- Follow PEP 8 Python style guidelines
- Add docstrings for all functions
- Include type hints where appropriate
- Write unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **librosa** - Audio analysis and processing
- **Streamlit** - Web application framework
- **PyAudio** - Audio recording capabilities
- **WebRTC** - Real-time communication

## 📞 Support

For questions, issues, or contributions:
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check this README and code comments
- **Community**: Join our discussion forum

---

**QIRAT AI** - Empowering precise audio analysis and vocal training through advanced pitch processing technology.