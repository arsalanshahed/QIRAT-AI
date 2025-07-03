# tajweed_rules.py
"""
Enhanced Tajweed Rule Engine with Arabic Phoneme Detection
"""

import re
from typing import List, Dict, Tuple, Optional
import numpy as np

# Arabic Phoneme Mapping
ARABIC_PHONEMES = {
    # Consonants
    'ا': 'alif', 'ب': 'ba', 'ت': 'ta', 'ث': 'tha', 'ج': 'jim',
    'ح': 'ha', 'خ': 'kha', 'د': 'dal', 'ذ': 'dhal', 'ر': 'ra',
    'ز': 'zay', 'س': 'sin', 'ش': 'shin', 'ص': 'sad', 'ض': 'dad',
    'ط': 'ta', 'ظ': 'za', 'ع': 'ayn', 'غ': 'ghayn', 'ف': 'fa',
    'ق': 'qaf', 'ك': 'kaf', 'ل': 'lam', 'م': 'mim', 'ن': 'nun',
    'ه': 'ha', 'و': 'waw', 'ي': 'ya',
    
    # Vowels and Marks
    'َ': 'fatha', 'ُ': 'damma', 'ِ': 'kasra', 'ْ': 'sukun',
    'ّ': 'shadda', 'ً': 'tanwin_fatha', 'ٌ': 'tanwin_damma', 'ٍ': 'tanwin_kasra',
    
    # Special Characters
    'ء': 'hamza', 'ة': 'ta_marbuta', 'ى': 'alif_maqsura'
}

# Enhanced Tajweed Rules with Audio Characteristics
ENHANCED_TAJWEED_RULES = [
    {
        "name": "Ghunnah",
        "description": "Nasalization when ن or م is followed by certain letters",
        "example": "مِنْ, أَمَّنْ",
        "trigger": ["ن", "م"],
        "followed_by": ["ي", "و", "م", "ن"],
        "audio_characteristics": {
            "duration": "2 counts",
            "nasal_sound": True,
            "frequency_range": "200-800 Hz"
        },
        "severity": "high"
    },
    {
        "name": "Ikhfa",
        "description": "Concealment of ن when followed by specific letters",
        "example": "مِنْ ثَمَرَةٍ",
        "trigger": ["ن"],
        "followed_by": ["ت", "ث", "ج", "د", "ذ", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ف", "ق", "ك"],
        "audio_characteristics": {
            "duration": "1-2 counts",
            "partial_nasal": True,
            "frequency_range": "150-600 Hz"
        },
        "severity": "medium"
    },
    {
        "name": "Iqlab",
        "description": "Conversion of ن to م when followed by ب",
        "example": "مِن بَعْدِ",
        "trigger": ["ن"],
        "followed_by": ["ب"],
        "audio_characteristics": {
            "duration": "2 counts",
            "bilabial_nasal": True,
            "frequency_range": "250-700 Hz"
        },
        "severity": "high"
    },
    {
        "name": "Idgham with Ghunnah",
        "description": "Merging of ن with ي, ن, م, و with nasalization",
        "example": "مَن يَعْمَلْ",
        "trigger": ["ن"],
        "followed_by": ["ي", "ن", "م", "و"],
        "audio_characteristics": {
            "duration": "2 counts",
            "complete_merge": True,
            "nasal_sound": True
        },
        "severity": "high"
    },
    {
        "name": "Idgham without Ghunnah",
        "description": "Merging of ن with ل, ر without nasalization",
        "example": "مِن رَبِّهِمْ",
        "trigger": ["ن"],
        "followed_by": ["ل", "ر"],
        "audio_characteristics": {
            "duration": "1 count",
            "complete_merge": True,
            "no_nasal": True
        },
        "severity": "high"
    },
    {
        "name": "Qalqalah",
        "description": "Echoing sound on ق, ط, ب, ج, د when stopped",
        "example": "يَقْطَعُ",
        "trigger": None,
        "followed_by": ["ق", "ط", "ب", "ج", "د"],
        "audio_characteristics": {
            "duration": "1 count",
            "echo_sound": True,
            "frequency_range": "100-500 Hz"
        },
        "severity": "medium"
    },
    {
        "name": "Madd Al-Muttasil",
        "description": "Required elongation when hamza follows a vowel",
        "example": "جَاءَ",
        "trigger": ["ا", "و", "ي"],
        "followed_by": ["ء"],
        "audio_characteristics": {
            "duration": "4-5 counts",
            "elongation": True
        },
        "severity": "high"
    },
    {
        "name": "Madd Al-Munfasil",
        "description": "Permissible elongation when hamza follows a vowel across words",
        "example": "إِنَّا أَعْطَيْنَا",
        "trigger": ["ا", "و", "ي"],
        "followed_by": ["ء"],
        "audio_characteristics": {
            "duration": "2-5 counts",
            "elongation": True
        },
        "severity": "low"
    },
    {
        "name": "Waqf (Stopping)",
        "description": "Proper stopping on words ending with sukun",
        "example": "كُلُّ",
        "trigger": None,
        "followed_by": [],
        "audio_characteristics": {
            "duration": "1 count",
            "clear_stop": True
        },
        "severity": "medium"
    }
]

class ArabicPhonemeDetector:
    """Detects and analyzes Arabic phonemes in text"""
    
    def __init__(self):
        self.phoneme_map = ARABIC_PHONEMES
        
    def extract_phonemes(self, text: str) -> List[Dict]:
        """Extract phonemes from Arabic text with positions"""
        phonemes = []
        for i, char in enumerate(text):
            if char in self.phoneme_map:
                phonemes.append({
                    'char': char,
                    'phoneme': self.phoneme_map[char],
                    'position': i,
                    'type': self._classify_phoneme(char)
                })
        return phonemes
    
    def _classify_phoneme(self, char: str) -> str:
        """Classify phoneme type"""
        if char in ['ا', 'و', 'ي']:
            return 'vowel'
        elif char in ['َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ً', 'ٌ', 'ٍ']:
            return 'diacritic'
        elif char in ['ء', 'ه']:
            return 'glottal'
        else:
            return 'consonant'

class EnhancedTajweedValidator:
    """Enhanced Tajweed validation with audio integration"""
    
    def __init__(self):
        self.rules = ENHANCED_TAJWEED_RULES
        self.phoneme_detector = ArabicPhonemeDetector()
        
    def validate_text(self, text: str) -> Dict:
        """Comprehensive Tajweed validation"""
        errors = []
        warnings = []
        score = 100
        
        # Extract phonemes
        phonemes = self.phoneme_detector.extract_phonemes(text)
        
        # Check each rule
        for rule in self.rules:
            rule_errors = self._check_rule(text, rule, phonemes)
            errors.extend(rule_errors)
            
            # Deduct points for errors
            for error in rule_errors:
                if rule['severity'] == 'high':
                    score -= 10
                elif rule['severity'] == 'medium':
                    score -= 5
                else:
                    score -= 2
                    
        # Ensure score doesn't go below 0
        score = max(0, score)
        
        return {
            'score': score,
            'errors': errors,
            'warnings': warnings,
            'phonemes': phonemes,
            'total_rules_checked': len(self.rules)
        }
    
    def _check_rule(self, text: str, rule: Dict, phonemes: List[Dict]) -> List[Dict]:
        """Check a specific Tajweed rule"""
        errors = []
        words = text.split()
        
        for w_idx, word in enumerate(words):
            for i, char in enumerate(word):
                trigger = rule.get("trigger")
                followed_by = rule.get("followed_by", [])
                
                # Check trigger conditions
                if trigger and char in trigger and i + 1 < len(word):
                    next_char = word[i + 1]
                    if next_char in followed_by:
                        errors.append({
                            "rule": rule["name"],
                            "description": rule["description"],
                            "example": rule["example"],
                            "word_index": w_idx,
                            "char_index": i,
                            "severity": rule["severity"],
                            "audio_characteristics": rule["audio_characteristics"],
                            "message": f"Check Tajweed rule: {rule['name']} for '{char}{next_char}' in word '{word}'"
                        })
                
                # Check Qalqalah at word end
                elif not trigger and char in followed_by and i == len(word) - 1:
                    errors.append({
                        "rule": rule["name"],
                        "description": rule["description"],
                        "example": rule["example"],
                        "word_index": w_idx,
                        "char_index": i,
                        "severity": rule["severity"],
                        "audio_characteristics": rule["audio_characteristics"],
                        "message": f"Check Tajweed rule: {rule['name']} for '{char}' at end of word '{word}'"
                    })
        
        return errors
    
    def validate_audio_segment(self, text: str, audio_features: Dict) -> Dict:
        """Validate Tajweed rules against audio features"""
        text_validation = self.validate_text(text)
        
        # Audio-specific validations
        audio_errors = []
        
        # Check duration for elongation rules
        for rule in self.rules:
            if 'duration' in rule['audio_characteristics']:
                expected_duration = rule['audio_characteristics']['duration']
                actual_duration = audio_features.get('duration', 0)
                
                # Simple duration validation (can be enhanced)
                if 'counts' in expected_duration:
                    counts = int(expected_duration.split()[0])
                    expected_seconds = counts * 0.5  # Approximate
                    
                    if abs(actual_duration - expected_seconds) > 0.3:
                        audio_errors.append({
                            "rule": rule["name"],
                            "type": "duration_mismatch",
                            "expected": expected_duration,
                            "actual": f"{actual_duration:.2f}s",
                            "message": f"Duration for {rule['name']} should be {expected_duration}"
                        })
        
        return {
            **text_validation,
            'audio_errors': audio_errors,
            'audio_score': max(0, text_validation['score'] - len(audio_errors) * 5)
        }

def generate_tajweed_feedback(validation_result: Dict) -> Tuple[List[str], List[Tuple]]:
    """Generate user-friendly feedback from validation results"""
    feedback = []
    highlights = []
    
    if validation_result['score'] == 100:
        feedback.append("✅ Excellent! No Tajweed errors detected.")
        return feedback, highlights
    
    # Add score feedback
    score = validation_result['score']
    if score >= 90:
        feedback.append(f"🎯 Great job! Your Tajweed score is {score}/100")
    elif score >= 70:
        feedback.append(f"👍 Good effort! Your Tajweed score is {score}/100")
    else:
        feedback.append(f"📚 Keep practicing! Your Tajweed score is {score}/100")
    
    # Add specific error feedback
    for error in validation_result['errors']:
        severity_icon = "🔴" if error['severity'] == 'high' else "🟡" if error['severity'] == 'medium' else "🟢"
        feedback.append(f"{severity_icon} {error['message']}")
        highlights.append((error['word_index'], error['char_index']))
    
    return feedback, highlights

# Backward compatibility functions
def validate_tajweed(text):
    """Legacy function for backward compatibility"""
    validator = EnhancedTajweedValidator()
    result = validator.validate_text(text)
    return result['errors']

def tajweed_feedback(text):
    """Legacy function for backward compatibility"""
    validator = EnhancedTajweedValidator()
    result = validator.validate_text(text)
    return generate_tajweed_feedback(result) 