#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quran AI Platform - Quick Start Script
Helps you set up and test the Quran AI learning platform
"""

import os
import sys
import subprocess
import importlib
import requests
import json

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    
    try:
        # Install basic requirements first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "numpy", "pandas", "matplotlib"])
        print("✅ Basic packages installed")
        
        # Install audio processing packages
        subprocess.check_call([sys.executable, "-m", "pip", "install", "librosa", "soundfile", "sounddevice"])
        print("✅ Audio processing packages installed")
        
        # Install web interface packages
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit-webrtc", "av"])
        print("✅ Web interface packages installed")
        
        # Install AI packages
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper"])
        print("✅ AI packages installed")
        
        # Install Arabic text processing
        subprocess.check_call([sys.executable, "-m", "pip", "install", "arabic-reshaper", "python-bidi"])
        print("✅ Arabic text processing packages installed")
        
        # Install additional utilities
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "yt-dlp"])
        print("✅ Utility packages installed")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def test_imports():
    """Test if all required packages can be imported"""
    print("\n🧪 Testing package imports...")
    
    required_packages = [
        'streamlit',
        'numpy',
        'pandas',
        'matplotlib',
        'librosa',
        'soundfile',
        'sounddevice',
        'streamlit_webrtc',
        'av',
        'whisper',
        'arabic_reshaper',
        'bidi',
        'requests'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n⚠️ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All packages imported successfully")
    return True

def test_quran_api():
    """Test Quran API connectivity"""
    print("\n🌐 Testing Quran API connectivity...")
    
    try:
        response = requests.get("https://api.quran.com/api/v4/chapters/1")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Quran API working - Surah {data['chapter']['id']}: {data['chapter']['name_simple']}")
            return True
        else:
            print(f"❌ Quran API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to Quran API: {e}")
        return False

def test_whisper_model():
    """Test Whisper model loading"""
    print("\n🤖 Testing Whisper model...")
    
    try:
        import whisper
        model = whisper.load_model("tiny")  # Use tiny model for quick test
        print("✅ Whisper model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to load Whisper model: {e}")
        return False

def create_test_files():
    """Create test files for the platform"""
    print("\n📁 Creating test files...")
    
    # Create a simple test audio file (silence)
    try:
        import numpy as np
        import soundfile as sf
        
        # Create 1 second of silence
        sample_rate = 44100
        duration = 1.0
        samples = np.zeros(int(sample_rate * duration))
        
        sf.write("test_audio.wav", samples, sample_rate)
        print("✅ Test audio file created")
        
    except Exception as e:
        print(f"❌ Failed to create test audio file: {e}")

def run_basic_tests():
    """Run basic functionality tests"""
    print("\n🔍 Running basic tests...")
    
    # Test Quran speech recognition
    try:
        from quran_speech_recognition import QuranSpeechRecognition
        qsr = QuranSpeechRecognition(model_size="tiny")
        print("✅ Quran speech recognition initialized")
        
        # Test verse fetching
        verse = qsr.get_quran_verse(1, 1)
        if 'error' not in verse:
            print(f"✅ Verse fetching working - {verse['text'][:50]}...")
        else:
            print(f"❌ Verse fetching failed: {verse['error']}")
            
    except ImportError:
        print("⚠️ Quran speech recognition not available (missing dependencies)")
    except Exception as e:
        print(f"❌ Quran speech recognition test failed: {e}")

def show_next_steps():
    """Show next steps for the user"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Run the enhanced frontend:")
    print("   streamlit run enhanced_frontend.py --server.port 8502")
    
    print("\n2. Run the Quran AI frontend (if available):")
    print("   streamlit run quran_ai_frontend.py --server.port 8503")
    
    print("\n3. Test the original pitch analysis:")
    print("   python main.py")
    
    print("\n4. Install additional packages for full functionality:")
    print("   pip install -r requirements_quran_ai.txt")
    
    print("\n📚 Documentation:")
    print("- Implementation Guide: IMPLEMENTATION_GUIDE.md")
    print("- Roadmap: quran_ai_roadmap.md")
    print("- Requirements: requirements_quran_ai.txt")
    
    print("\n🚀 Features Available:")
    print("✅ Pitch analysis and comparison")
    print("✅ User authentication system")
    print("✅ 5-second segment analysis")
    print("✅ Real-time audio recording")
    print("✅ Progress tracking")
    
    print("\n🔄 Features Coming Soon:")
    print("🔄 Quran speech recognition")
    print("🔄 Tajweed rule detection")
    print("🔄 Memorization system")
    print("🔄 Qirat style comparison")
    print("🔄 Personalized learning")

def main():
    """Main setup function"""
    print("🕌 Quran AI Platform - Quick Start Setup")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed during package installation")
        return
    
    # Test imports
    if not test_imports():
        print("\n❌ Setup failed during import testing")
        return
    
    # Test Quran API
    test_quran_api()
    
    # Test Whisper model
    test_whisper_model()
    
    # Create test files
    create_test_files()
    
    # Run basic tests
    run_basic_tests()
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main() 