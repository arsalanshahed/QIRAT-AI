#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Arabic ASR functionality
"""

import os
import sys
from arabic_asr import ArabicASR

def test_arabic_asr_basic():
    """Test basic Arabic ASR functionality"""
    print("🧪 Testing Arabic ASR Basic Functionality")
    print("=" * 50)
    
    # Initialize ASR
    try:
        asr = ArabicASR(model_size="base")
        print("✅ ASR initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize ASR: {e}")
        return False
    
    # Test Arabic text processing
    test_text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
    print(f"\n📝 Testing Arabic text processing:")
    print(f"Original: {test_text}")
    
    try:
        cleaned_text = asr.clean_arabic_text(test_text)
        print(f"Cleaned: {cleaned_text}")
        
        phonemes = asr.extract_phonemes(test_text)
        print(f"Phonemes: {phonemes[:5]}...")  # Show first 5 phonemes
        
        print("✅ Arabic text processing successful")
    except Exception as e:
        print(f"❌ Arabic text processing failed: {e}")
        return False
    
    return True

def test_audio_transcription():
    """Test audio transcription with available files"""
    print("\n🎵 Testing Audio Transcription")
    print("=" * 50)
    
    # Find available audio files
    audio_files = []
    for file in os.listdir('.'):
        if file.endswith(('.mp3', '.wav', '.m4a')):
            audio_files.append(file)
    
    if not audio_files:
        print("❌ No audio files found for testing")
        return False
    
    print(f"Found {len(audio_files)} audio files: {audio_files}")
    
    # Initialize ASR
    try:
        asr = ArabicASR(model_size="base")
    except Exception as e:
        print(f"❌ Failed to initialize ASR: {e}")
        return False
    
    # Test with first available file
    test_file = audio_files[0]
    print(f"\n🎤 Testing transcription with: {test_file}")
    
    try:
        # Test transcription
        result = asr.transcribe_audio(test_file)
        
        if result["success"]:
            print(f"✅ Transcription successful!")
            print(f"Language detected: {result['language']}")
            print(f"Text: {result['text'][:100]}...")
            print(f"Segments: {len(result['segments'])}")
        else:
            print(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Test audio features
        features = asr.extract_audio_features(test_file)
        if features["success"]:
            print(f"\n📊 Audio Features:")
            print(f"Duration: {features['features']['duration']:.2f}s")
            print(f"Sample Rate: {features['features']['sample_rate']} Hz")
            print(f"RMS Energy: {features['features']['rms_energy']:.4f}")
            print("✅ Audio feature extraction successful")
        else:
            print(f"❌ Audio feature extraction failed: {features.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_text_audio_alignment():
    """Test text-audio alignment"""
    print("\n🔗 Testing Text-Audio Alignment")
    print("=" * 50)
    
    # Find available audio files
    audio_files = []
    for file in os.listdir('.'):
        if file.endswith(('.mp3', '.wav', '.m4a')):
            audio_files.append(file)
    
    if not audio_files:
        print("❌ No audio files found for testing")
        return False
    
    # Initialize ASR
    try:
        asr = ArabicASR(model_size="base")
    except Exception as e:
        print(f"❌ Failed to initialize ASR: {e}")
        return False
    
    # Test with first available file
    test_file = audio_files[0]
    reference_text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
    
    print(f"🎤 Testing alignment with: {test_file}")
    print(f"📝 Reference text: {reference_text}")
    
    try:
        # Test alignment
        alignment_result = asr.align_text_audio(test_file, reference_text)
        
        if alignment_result["success"]:
            print(f"✅ Alignment successful!")
            print(f"Transcription: {alignment_result['transcription'][:100]}...")
            print(f"Reference: {alignment_result['reference']}")
            print(f"Accuracy: {alignment_result['accuracy']:.1f}%")
            print(f"Alignment items: {len(alignment_result['alignment'])}")
        else:
            print(f"❌ Alignment failed: {alignment_result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_pronunciation_detection():
    """Test pronunciation error detection"""
    print("\n🎯 Testing Pronunciation Error Detection")
    print("=" * 50)
    
    # Find available audio files
    audio_files = []
    for file in os.listdir('.'):
        if file.endswith(('.mp3', '.wav', '.m4a')):
            audio_files.append(file)
    
    if not audio_files:
        print("❌ No audio files found for testing")
        return False
    
    # Initialize ASR
    try:
        asr = ArabicASR(model_size="base")
    except Exception as e:
        print(f"❌ Failed to initialize ASR: {e}")
        return False
    
    # Test with first available file
    test_file = audio_files[0]
    reference_text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
    
    print(f"🎤 Testing pronunciation detection with: {test_file}")
    
    try:
        # Test pronunciation detection
        result = asr.detect_pronunciation_errors(test_file, reference_text)
        
        if result["success"]:
            print(f"✅ Pronunciation detection successful!")
            print(f"Total errors detected: {result['total_errors']}")
            print(f"Accuracy: {result['accuracy']:.1f}%")
            
            if result['errors']:
                print(f"\n🚨 Pronunciation Errors:")
                for i, error in enumerate(result['errors'][:3]):  # Show first 3 errors
                    print(f"  {i+1}. {error['message']} (at {error['start_time']:.2f}s)")
            else:
                print("✅ No pronunciation errors detected!")
        else:
            print(f"❌ Pronunciation detection failed: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Arabic ASR Testing Suite")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_arabic_asr_basic),
        ("Audio Transcription", test_audio_transcription),
        ("Text-Audio Alignment", test_text_audio_alignment),
        ("Pronunciation Detection", test_pronunciation_detection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Arabic ASR is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 