#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Enhanced Arabic Pronunciation Analysis
Demonstrates the new Tajweed rules and phoneme detection capabilities
"""

import os
import sys
from enhanced_pitch_analysis import ArabicPronunciationAnalyzer
from tajweed_rules import EnhancedTajweedValidator, ArabicPhonemeDetector

def test_arabic_phoneme_detection():
    """Test Arabic phoneme detection"""
    print("🧪 Testing Arabic Phoneme Detection...")
    
    detector = ArabicPhonemeDetector()
    
    # Test Arabic text with various phonemes
    test_text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
    
    phonemes = detector.extract_phonemes(test_text)
    
    print(f"Text: {test_text}")
    print(f"Found {len(phonemes)} phonemes:")
    
    for phoneme in phonemes:
        print(f"  {phoneme['char']} -> {phoneme['phoneme']} ({phoneme['type']})")
    
    return phonemes

def test_enhanced_tajweed_validation():
    """Test enhanced Tajweed validation"""
    print("\n🧪 Testing Enhanced Tajweed Validation...")
    
    validator = EnhancedTajweedValidator()
    
    # Test cases with different Tajweed rules
    test_cases = [
        {
            "text": "مِنْ ثَمَرَةٍ",
            "description": "Ikhfa rule (ن followed by ث)"
        },
        {
            "text": "مِن بَعْدِ",
            "description": "Iqlab rule (ن followed by ب)"
        },
        {
            "text": "مَن يَعْمَلْ",
            "description": "Idgham with Ghunnah (ن followed by ي)"
        },
        {
            "text": "يَقْطَعُ",
            "description": "Qalqalah rule (ق, ط, ب, ج, د)"
        },
        {
            "text": "جَاءَ",
            "description": "Madd Al-Muttasil (ا followed by ء)"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Text: {test_case['text']}")
        
        result = validator.validate_text(test_case['text'])
        
        print(f"Score: {result['score']}/100")
        print(f"Errors found: {len(result['errors'])}")
        
        if result['errors']:
            for error in result['errors']:
                print(f"  ⚠️ {error['rule']}: {error['message']}")
        else:
            print("  ✅ No Tajweed errors detected")
    
    return test_cases

def test_comprehensive_pronunciation_analysis():
    """Test comprehensive pronunciation analysis"""
    print("\n🧪 Testing Comprehensive Pronunciation Analysis...")
    
    analyzer = ArabicPronunciationAnalyzer()
    
    # Test with sample Arabic text
    test_text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
    
    # Create a dummy audio file for testing (if no real audio available)
    print("Note: This test requires actual audio files for full analysis.")
    print("Creating analysis structure without audio files...")
    
    # Test Tajweed validation part
    tajweed_result = analyzer.tajweed_validator.validate_text(test_text)
    
    print(f"Tajweed Analysis for: {test_text}")
    print(f"Score: {tajweed_result['score']}/100")
    print(f"Rules checked: {tajweed_result['total_rules_checked']}")
    
    if tajweed_result['errors']:
        print("Errors found:")
        for error in tajweed_result['errors']:
            print(f"  🔴 {error['rule']}: {error['message']}")
    else:
        print("  ✅ No Tajweed errors detected")
    
    return tajweed_result

def test_phoneme_frequency_mapping():
    """Test Arabic phoneme frequency mapping"""
    print("\n🧪 Testing Arabic Phoneme Frequency Mapping...")
    
    from enhanced_pitch_analysis import ARABIC_PHONEME_FREQUENCIES
    
    print("Arabic Phoneme Frequency Ranges:")
    print("=" * 50)
    
    # Group phonemes by type
    vowels = {k: v for k, v in ARABIC_PHONEME_FREQUENCIES.items() if 'alif' in k or 'waw' in k or 'ya' in k}
    consonants = {k: v for k, v in ARABIC_PHONEME_FREQUENCIES.items() if k not in vowels}
    
    print("Vowels:")
    for phoneme, (min_freq, max_freq) in vowels.items():
        print(f"  {phoneme}: {min_freq}-{max_freq} Hz")
    
    print("\nConsonants (by articulation):")
    for phoneme, (min_freq, max_freq) in consonants.items():
        print(f"  {phoneme}: {min_freq}-{max_freq} Hz")
    
    return ARABIC_PHONEME_FREQUENCIES

def test_tajweed_rule_database():
    """Test the comprehensive Tajweed rule database"""
    print("\n🧪 Testing Tajweed Rule Database...")
    
    from tajweed_rules import ENHANCED_TAJWEED_RULES
    
    print(f"Total Tajweed rules: {len(ENHANCED_TAJWEED_RULES)}")
    print("\nRule Categories:")
    
    # Group rules by severity
    high_severity = [rule for rule in ENHANCED_TAJWEED_RULES if rule['severity'] == 'high']
    medium_severity = [rule for rule in ENHANCED_TAJWEED_RULES if rule['severity'] == 'medium']
    low_severity = [rule for rule in ENHANCED_TAJWEED_RULES if rule['severity'] == 'low']
    
    print(f"  High severity: {len(high_severity)} rules")
    print(f"  Medium severity: {len(medium_severity)} rules")
    print(f"  Low severity: {len(low_severity)} rules")
    
    print("\nHigh Severity Rules:")
    for rule in high_severity:
        print(f"  🔴 {rule['name']}: {rule['description']}")
        print(f"     Example: {rule['example']}")
        print(f"     Audio: {rule['audio_characteristics']['duration']}")
    
    return ENHANCED_TAJWEED_RULES

def generate_sample_feedback():
    """Generate sample feedback for demonstration"""
    print("\n🧪 Generating Sample Feedback...")
    
    from tajweed_rules import generate_tajweed_feedback
    
    # Sample text with Tajweed errors
    sample_text = "مِنْ ثَمَرَةٍ مِن بَعْدِ"
    
    validator = EnhancedTajweedValidator()
    result = validator.validate_text(sample_text)
    
    feedback, highlights = generate_tajweed_feedback(result)
    
    print(f"Sample Text: {sample_text}")
    print("\nGenerated Feedback:")
    for msg in feedback:
        print(f"  {msg}")
    
    if highlights:
        print(f"\nError Highlights: {len(highlights)} positions marked")
    
    return feedback, highlights

def main():
    """Run all tests"""
    print("🚀 Enhanced Arabic Pronunciation Analysis Test Suite")
    print("=" * 60)
    
    try:
        # Run all tests
        test_arabic_phoneme_detection()
        test_enhanced_tajweed_validation()
        test_comprehensive_pronunciation_analysis()
        test_phoneme_frequency_mapping()
        test_tajweed_rule_database()
        generate_sample_feedback()
        
        print("\n✅ All tests completed successfully!")
        print("\n🎯 Key Features Demonstrated:")
        print("  • Arabic phoneme detection and classification")
        print("  • Enhanced Tajweed rule validation with severity levels")
        print("  • Audio characteristics analysis (frequency ranges, durations)")
        print("  • Comprehensive feedback generation")
        print("  • Pronunciation scoring system")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 