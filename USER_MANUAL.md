# QIRAT AI: User Manual

## 📖 Welcome to QIRAT AI

QIRAT AI is your personal audio analysis and vocal training assistant. Whether you're practicing Quranic recitation, learning to sing, or improving your vocal skills, QIRAT AI provides real-time feedback and auto-tuning to help you achieve perfect pitch.

## 🎯 What QIRAT AI Can Do For You

- **🎤 Record your voice** and compare it to reference audio
- **📊 Analyze pitch accuracy** with detailed visual feedback
- **🎛️ Auto-tune your recordings** to match reference pitch
- **📈 Track your progress** with segment-by-segment analysis
- **🌐 Use anywhere** with our web interface

## 🚀 Getting Started

### Prerequisites
- A computer with a microphone
- Internet connection (for web interface)
- Python 3.7 or higher (for command-line version)

### Installation

#### Option 1: Web Interface (Recommended for Beginners)
1. **Visit the QIRAT AI website** (provided by your administrator)
2. **No installation required** - just open your web browser
3. **Allow microphone access** when prompted

#### Option 2: Command Line Interface
1. **Download the software** from GitHub
2. **Install Python** if not already installed
3. **Open terminal/command prompt** in the QIRAT AI folder
4. **Install dependencies**: `pip install -r requirements.txt`

## 📱 Using the Web Interface

### Step 1: Access the Application
1. **Open your web browser** (Chrome, Firefox, or Edge recommended)
2. **Navigate to** the QIRAT AI web address
3. **Wait for the page to load** completely

### Step 2: Upload Reference Audio
1. **Click "Upload Reference Audio"**
2. **Select your reference file** (WAV or MP3 format)
3. **Wait for upload to complete**
4. **Verify the file appears** in the interface

**💡 Tip**: Use high-quality reference audio (44.1 kHz, 16-bit or higher) for best results.

### Step 3: Choose Your Input Method

#### Option A: Record Audio (Real-time)
1. **Select "Record"** from the input options
2. **Click "Start Recording"** when ready
3. **Speak or sing** into your microphone
4. **Click "Stop Recording"** when finished
5. **Wait for processing** to complete

#### Option B: Upload Audio File
1. **Select "Upload"** from the input options
2. **Click "Upload Your Audio"**
3. **Choose your audio file** (WAV or MP3 format)
4. **Wait for upload and processing**

### Step 4: Review Results
After processing, you'll see three audio players:

1. **🎤 User Recording (Aligned)** - Your original recording
2. **🎵 Reference Audio (Aligned)** - The reference you're comparing against
3. **🎛️ User Audio (Auto-Tuned)** - Your recording with pitch corrections

**Listen to each version** to hear the differences and improvements.

## 💻 Using the Command Line Interface

### Step 1: Prepare Your Files
1. **Place your reference audio** in the QIRAT AI folder
2. **Note the filename** (e.g., `azan15.mp3`)

### Step 2: Run the Application
```bash
python main.py
```

### Step 3: Follow the Prompts
```
Enter path to reference file (e.g., C:/Users/ashah/Downloads/azan15.mp3): azan15.mp3
Enter recording duration in seconds (e.g., 120): 30
```

### Step 4: Record Your Audio
- **The system will start recording** automatically
- **Speak or sing** into your microphone
- **Wait for the recording to finish**

### Step 5: Review Feedback
The system will display:
- **Pitch analysis results**
- **Specific feedback** with timestamps
- **Option to hear auto-tuned version**

## 📊 Understanding Your Results

### Pitch Analysis Feedback

#### What the Numbers Mean
- **Pitch off by X Hz at Y sec**: Your pitch was X Hz higher/lower than the reference at Y seconds
- **Positive numbers**: You sang/recited higher than the reference
- **Negative numbers**: You sang/recited lower than the reference

#### Feedback Examples
```
Pitch off by 65.2 Hz at 2.34 sec    # You were 65 Hz too high at 2.34 seconds
Pitch off by -78.1 Hz at 5.67 sec  # You were 78 Hz too low at 5.67 seconds
```

### Audio Quality Indicators

#### Good Quality Recording
- ✅ Clear, consistent audio levels
- ✅ Minimal background noise
- ✅ Proper microphone positioning
- ✅ Appropriate recording distance

#### Poor Quality Recording
- ❌ Muffled or distorted audio
- ❌ Excessive background noise
- ❌ Microphone too close or far
- ❌ Audio clipping or distortion

## 🎛️ Advanced Features

### Device Selection (Web Interface)
If you have multiple microphones:

1. **Look for the device selector** in the recording section
2. **Enter the device ID** if you know it
3. **Leave blank** for automatic device selection
4. **Test different devices** to find the best quality

### Customizing Feedback Sensitivity
For developers or advanced users:

1. **Open `feedback.py`** in a text editor
2. **Find the threshold parameter** (default: 50 Hz)
3. **Adjust the value**:
   - **Lower values** (e.g., 25 Hz): More sensitive feedback
   - **Higher values** (e.g., 100 Hz): Less sensitive feedback
4. **Save the file** and restart the application

### Batch Processing
For processing multiple files:

1. **Create a script** using the API functions
2. **Loop through your audio files**
3. **Save results** to a log file
4. **Generate summary reports**

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Microphone Not Working

**Problem**: "Requested device not found" error
**Solutions**:
1. **Check microphone connection** and drivers
2. **Allow microphone access** in browser settings
3. **Try a different browser** (Chrome, Firefox, Edge)
4. **Restart your computer** and try again
5. **Use the upload option** instead of recording

#### Poor Audio Quality

**Problem**: Feedback seems inaccurate or unclear
**Solutions**:
1. **Use a better microphone** or headset
2. **Reduce background noise** in your environment
3. **Position microphone** 6-12 inches from your mouth
4. **Check audio levels** - avoid clipping
5. **Use high-quality reference audio**

#### Web Interface Not Loading

**Problem**: Page doesn't load or shows errors
**Solutions**:
1. **Clear browser cache** and cookies
2. **Try a different browser**
3. **Check internet connection**
4. **Contact administrator** if the service is down

#### Processing Takes Too Long

**Problem**: Audio processing is slow
**Solutions**:
1. **Use shorter audio files** (under 5 minutes)
2. **Close other applications** to free up resources
3. **Check your computer's performance**
4. **Use lower quality audio** for faster processing

### Getting Help

#### Self-Help Resources
- **Check this manual** for common solutions
- **Review the troubleshooting section** above
- **Test with different audio files** to isolate issues

#### Contact Support
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check the technical documentation
- **Community**: Join user forums and discussions

## 📈 Best Practices

### For Best Results

#### Recording Tips
1. **Use a quiet environment** with minimal background noise
2. **Position your microphone** 6-12 inches from your mouth
3. **Speak/sing clearly** and at consistent volume
4. **Practice good posture** for better breath control
5. **Warm up your voice** before recording

#### Reference Audio Selection
1. **Choose high-quality reference** (44.1 kHz, 16-bit or higher)
2. **Use clear, well-recorded audio** without distortion
3. **Match your style** to the reference (same language, style, etc.)
4. **Keep reference files** organized and labeled

#### Practice Strategy
1. **Start with short segments** (30 seconds to 2 minutes)
2. **Focus on one aspect** at a time (pitch, timing, etc.)
3. **Review feedback carefully** and practice problem areas
4. **Record multiple takes** and compare improvements
5. **Track your progress** over time

### Performance Optimization

#### For Faster Processing
1. **Use shorter audio files** for quick feedback
2. **Close unnecessary applications** during processing
3. **Use SSD storage** for faster file access
4. **Optimize your computer** for audio processing

#### For Better Accuracy
1. **Use high-quality equipment** (microphone, audio interface)
2. **Ensure proper audio levels** (avoid clipping)
3. **Minimize background noise** and echo
4. **Use consistent recording setup** for comparisons

## 📋 Quick Reference

### Keyboard Shortcuts (Web Interface)
- **Spacebar**: Play/pause audio
- **Ctrl+R**: Refresh page
- **F5**: Reload application

### File Formats Supported
- **Input**: WAV, MP3
- **Output**: WAV
- **Recommended**: WAV (44.1 kHz, 16-bit)

### Recording Parameters
- **Sample Rate**: 44.1 kHz (web), 44.1 kHz (CLI)
- **Channels**: Mono (1 channel)
- **Duration**: Configurable (1 second to 10 minutes)

### Feedback Thresholds
- **Default**: 50 Hz deviation
- **Sensitive**: 25 Hz deviation
- **Less Sensitive**: 100 Hz deviation

## 🎓 Learning Resources

### Understanding Pitch
- **Frequency**: Measured in Hertz (Hz)
- **Musical Notes**: A4 = 440 Hz, C4 = 261.63 Hz
- **Semitones**: 12 semitones per octave
- **Cents**: 100 cents per semitone

### Vocal Training Concepts
- **Pitch Accuracy**: How close you are to the target pitch
- **Intonation**: The rise and fall of pitch in speech/song
- **Vibrato**: Natural pitch variation in sustained notes
- **Breath Control**: Managing airflow for consistent pitch

### Technical Terms
- **Hop Length**: Analysis frame step size
- **Frame**: Short audio segment for analysis
- **Pitch Contour**: Graph showing pitch over time
- **Auto-tuning**: Automatic pitch correction

## 📞 Support and Feedback

### Getting Help
- **Check this manual** first for solutions
- **Review troubleshooting** section for common issues
- **Contact support** through GitHub Issues
- **Join community** discussions and forums

### Providing Feedback
- **Report bugs** with detailed descriptions
- **Suggest features** for future improvements
- **Share success stories** and use cases
- **Contribute** to documentation and testing

### Staying Updated
- **Follow the project** on GitHub
- **Check for updates** regularly
- **Read release notes** for new features
- **Join mailing lists** for announcements

---

**Thank you for using QIRAT AI!** We hope this tool helps you achieve your vocal training goals. For the latest updates and support, visit our GitHub repository or contact our support team. 