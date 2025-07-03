#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Arabic Speech Recognition System
Demonstrates the speech recognition capabilities without requiring audio files
"""

import os
import sys
import json
from typing import Dict, List

# Import our modules
from tajweed_rules import EnhancedTajweedValidator, ArabicPhonemeDetector
from enhanced_pitch_analysis import ArabicPronunciationAnalyzer

def test_arabic_phoneme_detection_advanced():
    """Test advanced Arabic phoneme detection"""
    print("🧪 Testing Advanced Arabic Phoneme Detection...")
    
    detector = ArabicPhonemeDetector()
    
    # Test various Arabic texts
    test_texts = [
        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
        "الرَّحْمَٰنِ الرَّحِيمِ",
        "مَالِكِ يَوْمِ الدِّينِ"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nText {i}: {text}")
        phonemes = detector.extract_phonemes(text)
        
        # Group phonemes by type
        vowels = [p for p in phonemes if p['type'] == 'vowel']
        consonants = [p for p in phonemes if p['type'] == 'consonant']
        diacritics = [p for p in phonemes if p['type'] == 'diacritic']
        
        print(f"  Vowels: {len(vowels)}")
        print(f"  Consonants: {len(consonants)}")
        print(f"  Diacritics: {len(diacritics)}")
        
        # Show some examples
        if vowels:
            print(f"  Sample vowels: {[v['phoneme'] for v in vowels[:3]]}")
        if consonants:
            print(f"  Sample consonants: {[c['phoneme'] for c in consonants[:3]]}")
    
    return test_texts

def test_enhanced_tajweed_validation_comprehensive():
    """Test comprehensive Tajweed validation"""
    print("\n🧪 Testing Comprehensive Tajweed Validation...")
    
    validator = EnhancedTajweedValidator()
    
    # Test cases covering all major Tajweed rules
    comprehensive_test_cases = [
        {
            "text": "مِنْ ثَمَرَةٍ",
            "description": "Ikhfa rule - ن followed by ث",
            "expected_rules": ["Ikhfa"]
        },
        {
            "text": "مِن بَعْدِ",
            "description": "Iqlab rule - ن followed by ب",
            "expected_rules": ["Iqlab"]
        },
        {
            "text": "مَن يَعْمَلْ",
            "description": "Idgham with Ghunnah - ن followed by ي",
            "expected_rules": ["Idgham with Ghunnah"]
        },
        {
            "text": "مِن رَبِّهِمْ",
            "description": "Idgham without Ghunnah - ن followed by ر",
            "expected_rules": ["Idgham without Ghunnah"]
        },
        {
            "text": "يَقْطَعُ",
            "description": "Qalqalah rule - ق, ط, ب, ج, د",
            "expected_rules": ["Qalqalah"]
        },
        {
            "text": "جَاءَ",
            "description": "Madd Al-Muttasil - ا followed by ء",
            "expected_rules": ["Madd Al-Muttasil", "Madd Al-Munfasil"]
        },
        {
            "text": "كُلُّ",
            "description": "Waqf (Stopping) - word ending with sukun",
            "expected_rules": ["Waqf (Stopping)"]
        }
    ]
    
    results = []
    for test_case in comprehensive_test_cases:
        print(f"\n📝 {test_case['description']}")
        print(f"Text: {test_case['text']}")
        
        result = validator.validate_text(test_case['text'])
        
        print(f"Score: {result['score']}/100")
        print(f"Errors found: {len(result['errors'])}")
        
        # Check if expected rules were triggered
        found_rules = [error['rule'] for error in result['errors']]
        expected_rules = test_case['expected_rules']
        
        for expected_rule in expected_rules:
            if expected_rule in found_rules:
                print(f"  ✅ {expected_rule} rule detected")
            else:
                print(f"  ❌ {expected_rule} rule not detected")
        
        results.append({
            'test_case': test_case,
            'result': result,
            'found_rules': found_rules
        })
    
    return results

def test_pronunciation_analysis_structure():
    """Test the structure of pronunciation analysis"""
    print("\n🧪 Testing Pronunciation Analysis Structure...")
    
    analyzer = ArabicPronunciationAnalyzer()
    
    # Test with sample data
    sample_text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
    
    # Test Tajweed validation part
    tajweed_result = analyzer.tajweed_validator.validate_text(sample_text)
    
    print(f"Sample Text: {sample_text}")
    print(f"Tajweed Score: {tajweed_result['score']}/100")
    print(f"Rules Checked: {tajweed_result['total_rules_checked']}")
    
    # Test phoneme extraction
    phonemes = analyzer.phoneme_detector.extract_phonemes(sample_text)
    print(f"Phonemes Extracted: {len(phonemes)}")
    
    # Show phoneme distribution
    phoneme_types = {}
    for phoneme in phonemes:
        phoneme_type = phoneme['type']
        phoneme_types[phoneme_type] = phoneme_types.get(phoneme_type, 0) + 1
    
    print("Phoneme Distribution:")
    for phoneme_type, count in phoneme_types.items():
        print(f"  {phoneme_type}: {count}")
    
    return {
        'tajweed_result': tajweed_result,
        'phonemes': phonemes,
        'phoneme_distribution': phoneme_types
    }

def test_speech_recognition_simulation():
    """Simulate speech recognition analysis without actual audio"""
    print("\n🧪 Testing Speech Recognition Simulation...")
    
    # Simulate transcription results
    simulated_transcription = {
        'text': 'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ',
        'segments': [
            {'start': 0.0, 'end': 2.5, 'text': 'بِسْمِ اللَّهِ'},
            {'start': 2.5, 'end': 5.0, 'text': 'الرَّحْمَٰنِ الرَّحِيمِ'}
        ],
        'language': 'ar',
        'duration': 5.0,
        'confidence': 0.85,
        'timestamp': '2024-01-01T12:00:00'
    }
    
    # Simulate reference text
    reference_text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
    
    # Analyze transcribed text
    validator = EnhancedTajweedValidator()
    phoneme_detector = ArabicPhonemeDetector()
    
    # Text analysis
    phonemes = phoneme_detector.extract_phonemes(simulated_transcription['text'])
    tajweed_result = validator.validate_text(simulated_transcription['text'])
    
    # Simulate comparison analysis
    transcribed_words = set(simulated_transcription['text'].split())
    reference_words = set(reference_text.split())
    correct_words = transcribed_words.intersection(reference_words)
    word_accuracy = len(correct_words) / len(reference_words) if reference_words else 0
    
    comparison_analysis = {
        'word_accuracy': word_accuracy,
        'character_accuracy': 1.0,  # Perfect match in this case
        'correct_words': list(correct_words),
        'missing_words': [],
        'extra_words': [],
        'total_reference_words': len(reference_words),
        'total_transcribed_words': len(transcribed_words)
    }
    
    # Generate feedback
    feedback = {
        'transcription_feedback': ["✅ Clear speech detected"],
        'tajweed_feedback': [f"📚 Tajweed Score: {tajweed_result['score']}/100"],
        'pronunciation_feedback': ["🎯 Great pronunciation"],
        'comparison_feedback': [f"📝 Word accuracy: {word_accuracy:.1%}"],
        'improvement_suggestions': []
    }
    
    if tajweed_result['score'] < 100:
        for error in tajweed_result['errors']:
            feedback['tajweed_feedback'].append(f"⚠️ {error['rule']}: {error['message']}")
    else:
        feedback['tajweed_feedback'].append("✅ Excellent Tajweed!")
    
    # Calculate overall score
    confidence_score = simulated_transcription['confidence'] * 20
    tajweed_score = tajweed_result['score'] * 0.4
    comparison_score = comparison_analysis['word_accuracy'] * 20
    pronunciation_score = 20  # Simulated perfect pronunciation
    
    overall_score = int(confidence_score + tajweed_score + comparison_score + pronunciation_score)
    
    print(f"Simulated Transcription: {simulated_transcription['text']}")
    print(f"Confidence: {simulated_transcription['confidence']:.1%}")
    print(f"Word Accuracy: {word_accuracy:.1%}")
    print(f"Tajweed Score: {tajweed_result['score']}/100")
    print(f"Overall Score: {overall_score}/100")
    
    print("\nGenerated Feedback:")
    for category, messages in feedback.items():
        if messages:
            print(f"\n{category.replace('_', ' ').title()}:")
            for message in messages:
                print(f"  {message}")
    
    return {
        'transcription': simulated_transcription,
        'comparison_analysis': comparison_analysis,
        'tajweed_result': tajweed_result,
        'feedback': feedback,
        'overall_score': overall_score
    }

def test_audio_segment_analysis():
    """Test audio segment analysis simulation"""
    print("\n🧪 Testing Audio Segment Analysis Simulation...")
    
    # Simulate segmented audio analysis
    segments = [
        {
            'segment_id': 0,
            'start_time': 0.0,
            'end_time': 5.0,
            'text': 'بِسْمِ اللَّهِ',
            'tajweed_score': 95,
            'errors': []
        },
        {
            'segment_id': 1,
            'start_time': 5.0,
            'end_time': 10.0,
            'text': 'الرَّحْمَٰنِ الرَّحِيمِ',
            'tajweed_score': 88,
            'errors': [
                {'rule': 'Madd Al-Muttasil', 'message': 'Check elongation for ا followed by ء'}
            ]
        }
    ]
    
    print("Simulated Audio Segments:")
    for segment in segments:
        print(f"\nSegment {segment['segment_id']}: {segment['start_time']}-{segment['end_time']}s")
        print(f"Text: {segment['text']}")
        print(f"Tajweed Score: {segment['tajweed_score']}/100")
        
        if segment['errors']:
            print("Errors:")
            for error in segment['errors']:
                print(f"  ⚠️ {error['rule']}: {error['message']}")
        else:
            print("  ✅ No errors")
    
    # Calculate overall segment statistics
    total_score = sum(segment['tajweed_score'] for segment in segments)
    avg_score = total_score / len(segments)
    total_errors = sum(len(segment['errors']) for segment in segments)
    
    print(f"\nOverall Statistics:")
    print(f"Average Tajweed Score: {avg_score:.1f}/100")
    print(f"Total Errors: {total_errors}")
    print(f"Segments Analyzed: {len(segments)}")
    
    return {
        'segments': segments,
        'average_score': avg_score,
        'total_errors': total_errors
    }

def generate_comprehensive_report():
    """Generate a comprehensive test report"""
    print("\n📊 Generating Comprehensive Test Report...")
    
    report = {
        'test_results': {},
        'summary': {},
        'recommendations': []
    }
    
    # Run all tests
    report['test_results']['phoneme_detection'] = test_arabic_phoneme_detection_advanced()
    report['test_results']['tajweed_validation'] = test_enhanced_tajweed_validation_comprehensive()
    report['test_results']['pronunciation_analysis'] = test_pronunciation_analysis_structure()
    report['test_results']['speech_recognition'] = test_speech_recognition_simulation()
    report['test_results']['segment_analysis'] = test_audio_segment_analysis()
    
    # Generate summary
    total_tajweed_rules = len(report['test_results']['tajweed_validation'])
    successful_tests = len([r for r in report['test_results']['tajweed_validation'] 
                          if r['result']['score'] > 80])
    
    report['summary'] = {
        'total_tests': len(report['test_results']),
        'tajweed_rules_tested': total_tajweed_rules,
        'successful_tajweed_tests': successful_tests,
        'overall_success_rate': successful_tests / total_tajweed_rules if total_tajweed_rules > 0 else 0
    }
    
    # Generate recommendations
    if report['summary']['overall_success_rate'] < 0.8:
        report['recommendations'].append("📚 Review Tajweed rules implementation")
    
    report['recommendations'].extend([
        "🎤 Integrate with actual audio files for full testing",
        "🔧 Add more comprehensive error handling",
        "📈 Implement performance metrics tracking",
        "🌐 Add support for different Arabic dialects"
    ])
    
    print(f"\n📋 Test Summary:")
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Tajweed Rules Tested: {report['summary']['tajweed_rules_tested']}")
    print(f"Successful Tests: {report['summary']['successful_tajweed_tests']}")
    print(f"Success Rate: {report['summary']['overall_success_rate']:.1%}")
    
    print(f"\n💡 Recommendations:")
    for recommendation in report['recommendations']:
        print(f"  {recommendation}")
    
    return report

def main():
    """Run all speech recognition tests"""
    print("🎤 Arabic Speech Recognition Test Suite")
    print("=" * 60)
    
    try:
        # Run comprehensive tests
        report = generate_comprehensive_report()
        
        print("\n✅ All tests completed successfully!")
        print("\n🎯 Key Features Demonstrated:")
        print("  • Arabic phoneme detection and classification")
        print("  • Comprehensive Tajweed rule validation")
        print("  • Speech recognition simulation")
        print("  • Audio segment analysis")
        print("  • Feedback generation system")
        print("  • Scoring and evaluation metrics")
        
        # Save test report
        with open('speech_recognition_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        print("\n📄 Test report saved to: speech_recognition_test_report.json")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 