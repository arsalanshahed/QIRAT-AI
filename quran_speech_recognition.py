#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quran Speech Recognition Module
Arabic ASR integration with Whisper and Quran text comparison
"""

import whisper
import numpy as np
import librosa
import requests
import json
import re
from typing import Dict, List, Tuple, Optional
import arabic_reshaper
from bidi.algorithm import get_display
import difflib

class QuranSpeechRecognition:
    def __init__(self, model_size="base"):
        """
        Initialize Quran Speech Recognition system
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
        """
        self.model = whisper.load_model(model_size)
        self.quran_api_base = "https://api.quran.com/api/v4"
        
        # Arabic phoneme mapping for Tajweed analysis
        self.arabic_phonemes = {
            'ا': 'alif', 'ب': 'ba', 'ت': 'ta', 'ث': 'tha', 'ج': 'jim',
            'ح': 'ha', 'خ': 'kha', 'د': 'dal', 'ذ': 'thal', 'ر': 'ra',
            'ز': 'zay', 'س': 'sin', 'ش': 'shin', 'ص': 'sad', 'ض': 'dad',
            'ط': 'ta', 'ظ': 'za', 'ع': 'ayn', 'غ': 'ghayn', 'ف': 'fa',
            'ق': 'qaf', 'ك': 'kaf', 'ل': 'lam', 'م': 'mim', 'ن': 'nun',
            'ه': 'ha', 'و': 'waw', 'ي': 'ya', 'ء': 'hamza'
        }
        
        # Tajweed rules database
        self.tajweed_rules = self._initialize_tajweed_rules()
    
    def _initialize_tajweed_rules(self) -> Dict:
        """Initialize Tajweed rules database"""
        return {
            'ghunnah': {
                'description': 'Nasalization of ن and م when followed by certain letters',
                'rules': ['ن', 'م'],
                'triggers': ['ب', 'ج', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي'],
                'duration': 2  # counts
            },
            'idgham': {
                'description': 'Merging of ن with following letters',
                'rules': ['ن'],
                'triggers': ['ي', 'ر', 'م', 'ل', 'و', 'ن'],
                'duration': 1
            },
            'ikhfa': {
                'description': 'Partial hiding of ن sound',
                'rules': ['ن'],
                'triggers': ['ت', 'ث', 'ج', 'د', 'ذ', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ف', 'ق', 'ك'],
                'duration': 2
            },
            'qalqalah': {
                'description': 'Bouncing sound for ق ط ب ج د',
                'rules': ['ق', 'ط', 'ب', 'ج', 'د'],
                'triggers': ['sukun'],  # when these letters have sukun
                'duration': 1
            },
            'madd': {
                'description': 'Elongation of vowels',
                'rules': ['ا', 'و', 'ي'],
                'triggers': ['hamza', 'sukun'],
                'duration': 4  # counts for obligatory madd
            }
        }
    
    def transcribe_audio(self, audio_file: str) -> Dict:
        """
        Transcribe Arabic audio using Whisper
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Dictionary containing transcription and metadata
        """
        try:
            # Load and transcribe audio
            result = self.model.transcribe(audio_file, language="ar")
            
            # Process transcription
            transcription = {
                'text': result['text'].strip(),
                'segments': result['segments'],
                'language': result['language'],
                'confidence': self._calculate_confidence(result['segments'])
            }
            
            return transcription
            
        except Exception as e:
            return {
                'error': f"Transcription failed: {str(e)}",
                'text': '',
                'segments': [],
                'confidence': 0.0
            }
    
    def _calculate_confidence(self, segments: List[Dict]) -> float:
        """Calculate overall confidence score from segments"""
        if not segments:
            return 0.0
        
        total_confidence = sum(seg.get('avg_logprob', 0) for seg in segments)
        return total_confidence / len(segments)
    
    def get_quran_verse(self, surah: int, ayah: int) -> Dict:
        """
        Fetch Quran verse text from API
        
        Args:
            surah: Surah number (1-114)
            ayah: Ayah number within surah
            
        Returns:
            Dictionary containing verse text and metadata
        """
        try:
            url = f"{self.quran_api_base}/verses/by_key/{surah}:{ayah}?fields=text_arabic,text_uthmani,chapter_id,verse_number,juz_number,page_number,hizb_number"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            verse_data = data['verse']
            
            return {
                'text': verse_data.get('text_arabic', verse_data.get('text', '')),
                'text_uthmani': verse_data.get('text_uthmani', verse_data.get('text', '')),
                'surah': verse_data.get('chapter_id', verse_data.get('surah', 1)),
                'ayah': verse_data.get('verse_number', verse_data.get('ayah', 1)),
                'juz': verse_data.get('juz_number', 1),
                'page': verse_data.get('page_number', 1),
                'hizb': verse_data.get('hizb_number', 1)
            }
            
        except Exception as e:
            return {
                'error': f"Failed to fetch verse: {str(e)}",
                'text': '',
                'surah': surah,
                'ayah': ayah
            }
    
    def compare_recitation(self, audio_file: str, surah: int, ayah: int) -> Dict:
        """
        Compare user recitation with correct Quran text
        
        Args:
            audio_file: Path to user's audio file
            surah: Surah number
            ayah: Ayah number
            
        Returns:
            Dictionary containing comparison results and feedback
        """
        # Get correct verse text
        correct_verse = self.get_quran_verse(surah, ayah)
        if 'error' in correct_verse:
            return {'error': correct_verse['error']}
        
        # Transcribe user audio
        user_transcription = self.transcribe_audio(audio_file)
        if 'error' in user_transcription:
            return {'error': user_transcription['error']}
        
        # Compare texts
        comparison = self._compare_texts(
            user_transcription['text'], 
            correct_verse['text_uthmani']
        )
        
        # Analyze Tajweed
        tajweed_analysis = self._analyze_tajweed(
            user_transcription['text'], 
            correct_verse['text_uthmani']
        )
        
        return {
            'user_text': user_transcription['text'],
            'correct_text': correct_verse['text_uthmani'],
            'confidence': user_transcription['confidence'],
            'comparison': comparison,
            'tajweed_analysis': tajweed_analysis,
            'verse_info': {
                'surah': surah,
                'ayah': ayah,
                'text_arabic': correct_verse['text']
            }
        }
    
    def _compare_texts(self, user_text: str, correct_text: str) -> Dict:
        """
        Compare user text with correct text and identify differences
        
        Args:
            user_text: User's transcribed text
            correct_text: Correct Quran text
            
        Returns:
            Dictionary containing comparison results
        """
        # Clean and normalize texts
        user_clean = self._normalize_arabic_text(user_text)
        correct_clean = self._normalize_arabic_text(correct_text)
        
        # Calculate similarity
        similarity = difflib.SequenceMatcher(None, user_clean, correct_clean).ratio()
        
        # Find differences
        differences = []
        matcher = difflib.SequenceMatcher(None, user_clean, correct_clean)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != 'equal':
                differences.append({
                    'type': tag,
                    'user_text': user_clean[i1:i2],
                    'correct_text': correct_clean[j1:j2],
                    'position': i1
                })
        
        return {
            'similarity': similarity,
            'accuracy_percentage': similarity * 100,
            'differences': differences,
            'total_differences': len(differences)
        }
    
    def _normalize_arabic_text(self, text: str) -> str:
        """Normalize Arabic text for comparison"""
        # Remove diacritics (harakat) for basic comparison
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
        
        # Normalize Arabic characters
        text = arabic_reshaper.reshape(text)
        text = get_display(text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _analyze_tajweed(self, user_text: str, correct_text: str) -> Dict:
        """
        Analyze Tajweed rules in user's recitation
        
        Args:
            user_text: User's transcribed text
            correct_text: Correct Quran text
            
        Returns:
            Dictionary containing Tajweed analysis
        """
        analysis = {
            'errors': [],
            'score': 100,
            'rule_violations': {}
        }
        
        # Check each Tajweed rule
        for rule_name, rule_data in self.tajweed_rules.items():
            violations = self._check_tajweed_rule(user_text, correct_text, rule_name, rule_data)
            if violations:
                analysis['rule_violations'][rule_name] = violations
                analysis['errors'].extend(violations)
                # Reduce score for each violation
                analysis['score'] -= len(violations) * 5
        
        analysis['score'] = max(0, analysis['score'])
        
        return analysis
    
    def _check_tajweed_rule(self, user_text: str, correct_text: str, rule_name: str, rule_data: Dict) -> List[Dict]:
        """Check specific Tajweed rule violations"""
        violations = []
        
        # This is a simplified implementation
        # In a full system, you would need more sophisticated Arabic text analysis
        
        if rule_name == 'ghunnah':
            # Check for proper nasalization
            violations.extend(self._check_ghunnah(user_text, correct_text))
        elif rule_name == 'madd':
            # Check for proper elongation
            violations.extend(self._check_madd(user_text, correct_text))
        elif rule_name == 'qalqalah':
            # Check for proper bouncing sounds
            violations.extend(self._check_qalqalah(user_text, correct_text))
        
        return violations
    
    def _check_ghunnah(self, user_text: str, correct_text: str) -> List[Dict]:
        """Check Ghunnah rule violations"""
        violations = []
        # Simplified implementation - would need more sophisticated analysis
        return violations
    
    def _check_madd(self, user_text: str, correct_text: str) -> List[Dict]:
        """Check Madd (elongation) rule violations"""
        violations = []
        # Simplified implementation - would need more sophisticated analysis
        return violations
    
    def _check_qalqalah(self, user_text: str, correct_text: str) -> List[Dict]:
        """Check Qalqalah rule violations"""
        violations = []
        # Simplified implementation - would need more sophisticated analysis
        return violations
    
    def generate_feedback(self, comparison_result: Dict) -> Dict:
        """
        Generate detailed feedback based on comparison results
        
        Args:
            comparison_result: Results from compare_recitation method
            
        Returns:
            Dictionary containing detailed feedback
        """
        if 'error' in comparison_result:
            return {'error': comparison_result['error']}
        
        feedback = {
            'overall_score': 0,
            'pronunciation_score': 0,
            'tajweed_score': 0,
            'suggestions': [],
            'positive_feedback': [],
            'areas_for_improvement': []
        }
        
        # Calculate scores
        comparison = comparison_result['comparison']
        tajweed = comparison_result['tajweed_analysis']
        
        # Overall accuracy score
        feedback['overall_score'] = comparison['accuracy_percentage']
        feedback['pronunciation_score'] = comparison['accuracy_percentage']
        feedback['tajweed_score'] = tajweed['score']
        
        # Generate suggestions
        if comparison['accuracy_percentage'] < 80:
            feedback['areas_for_improvement'].append(
                "Focus on correct pronunciation of Arabic letters"
            )
            feedback['suggestions'].append(
                "Practice with a qualified teacher to improve pronunciation"
            )
        
        if tajweed['score'] < 80:
            feedback['areas_for_improvement'].append(
                "Pay attention to Tajweed rules"
            )
            feedback['suggestions'].append(
                "Study Tajweed rules and practice with audio examples"
            )
        
        if comparison['accuracy_percentage'] > 90:
            feedback['positive_feedback'].append(
                "Excellent pronunciation accuracy!"
            )
        
        if tajweed['score'] > 90:
            feedback['positive_feedback'].append(
                "Great adherence to Tajweed rules!"
            )
        
        return feedback

# Example usage and testing
if __name__ == "__main__":
    # Initialize the system
    qsr = QuranSpeechRecognition()
    
    # Test with a sample audio file
    # result = qsr.compare_recitation("user_recording.wav", 1, 1)  # Al-Fatiha, verse 1
    # print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Test verse fetching
    verse = qsr.get_quran_verse(1, 1)
    print("Sample verse:", verse) 