#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arabic Speech Recognition Module
Integrates Whisper for Arabic transcription and connects with Tajweed analysis
"""

import os
import sys
import json
import numpy as np
import librosa
import soundfile as sf
from typing import Dict, List, Tuple, Optional, Any
import whisper
from datetime import datetime
import torch

# Import our enhanced modules
from tajweed_rules import EnhancedTajweedValidator, ArabicPhonemeDetector
from enhanced_pitch_analysis import ArabicPronunciationAnalyzer

class ArabicSpeechRecognizer:
    """Advanced Arabic speech recognition with Tajweed integration"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Arabic speech recognizer
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
        """
        self.model_size = model_size
        self.model = None
        self.tajweed_validator = EnhancedTajweedValidator()
        self.phoneme_detector = ArabicPhonemeDetector()
        self.pronunciation_analyzer = ArabicPronunciationAnalyzer()
        
        # Load Whisper model
        self._load_whisper_model()
    
    def _load_whisper_model(self):
        """Load Whisper model for Arabic transcription"""
        try:
            print(f"🔄 Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            print(f"✅ Whisper model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading Whisper model: {e}")
            print("💡 Try installing whisper: pip install openai-whisper")
            raise
    
    def transcribe_audio(self, audio_file: str, language: str = "ar") -> Dict:
        """
        Transcribe Arabic audio to text
        
        Args:
            audio_file: Path to audio file
            language: Language code (default: "ar" for Arabic)
        
        Returns:
            Dictionary with transcription results
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        try:
            print(f"🎤 Transcribing audio: {audio_file}")
            
            # Transcribe with Whisper
            if self.model is None:
                raise RuntimeError("Whisper model not loaded")
                
            result = self.model.transcribe(
                audio_file,
                language=language,
                task="transcribe",
                verbose=False
            )
            
            # Extract results
            text = result.get('text', '')
            if isinstance(text, list):
                text = ' '.join(text)
            
            segments = result.get('segments', [])
            duration = segments[-1].get('end', 0) if segments and isinstance(segments, list) else 0
            
            transcription = {
                'text': text.strip(),
                'segments': segments,
                'language': result.get('language', 'ar'),
                'duration': duration,
                'confidence': self._calculate_confidence(segments),
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ Transcription completed: {len(transcription['text'])} characters")
            return transcription
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            raise
    
    def _calculate_confidence(self, segments: List[Dict]) -> float:
        """Calculate overall confidence from segments"""
        if not segments:
            return 0.0
        
        # Extract confidence scores (if available)
        confidences = []
        for segment in segments:
            if 'avg_logprob' in segment:
                # Convert log probability to confidence
                confidence = np.exp(segment['avg_logprob'])
                confidences.append(confidence)
        
        return float(np.mean(confidences) if confidences else 0.8)  # Default confidence
    
    def analyze_recitation(self, audio_file: str, reference_text: str = None) -> Dict:
        """
        Comprehensive recitation analysis with transcription and Tajweed validation
        
        Args:
            audio_file: Path to audio file
            reference_text: Expected text (optional, for comparison)
        
        Returns:
            Comprehensive analysis results
        """
        print(f"🔍 Starting comprehensive recitation analysis...")
        
        # Step 1: Transcribe audio
        transcription = self.transcribe_audio(audio_file)
        
        # Step 2: Analyze transcribed text
        text_analysis = self._analyze_transcribed_text(transcription['text'])
        
        # Step 3: Compare with reference if provided
        comparison_analysis = None
        if reference_text:
            comparison_analysis = self._compare_with_reference(
                transcription['text'], reference_text
            )
        
        # Step 4: Audio pronunciation analysis
        pronunciation_analysis = self._analyze_pronunciation(audio_file, transcription['text'])
        
        # Step 5: Generate comprehensive feedback
        feedback = self._generate_recitation_feedback(
            transcription, text_analysis, comparison_analysis, pronunciation_analysis
        )
        
        return {
            'transcription': transcription,
            'text_analysis': text_analysis,
            'comparison_analysis': comparison_analysis,
            'pronunciation_analysis': pronunciation_analysis,
            'feedback': feedback,
            'overall_score': self._calculate_recitation_score(
                transcription, text_analysis, comparison_analysis, pronunciation_analysis
            )
        }
    
    def _analyze_transcribed_text(self, text: str) -> Dict:
        """Analyze transcribed text for Tajweed and phoneme patterns"""
        
        # Extract phonemes
        phonemes = self.phoneme_detector.extract_phonemes(text)
        
        # Validate Tajweed rules
        tajweed_result = self.tajweed_validator.validate_text(text)
        
        # Analyze text characteristics
        text_stats = {
            'total_chars': len(text),
            'total_phonemes': len(phonemes),
            'vowel_count': len([p for p in phonemes if p['type'] == 'vowel']),
            'consonant_count': len([p for p in phonemes if p['type'] == 'consonant']),
            'diacritic_count': len([p for p in phonemes if p['type'] == 'diacritic']),
            'word_count': len(text.split()),
            'avg_word_length': np.mean([len(word) for word in text.split()]) if text.split() else 0
        }
        
        return {
            'phonemes': phonemes,
            'tajweed_analysis': tajweed_result,
            'text_statistics': text_stats
        }
    
    def _compare_with_reference(self, transcribed_text: str, reference_text: str) -> Dict:
        """Compare transcribed text with reference text"""
        
        # Simple text similarity (can be enhanced with more sophisticated algorithms)
        transcribed_words = set(transcribed_text.split())
        reference_words = set(reference_text.split())
        
        # Calculate word-level accuracy
        correct_words = transcribed_words.intersection(reference_words)
        total_reference_words = len(reference_words)
        word_accuracy = len(correct_words) / total_reference_words if total_reference_words > 0 else 0
        
        # Character-level accuracy
        char_accuracy = self._calculate_character_accuracy(transcribed_text, reference_text)
        
        # Find missing and extra words
        missing_words = reference_words - transcribed_words
        extra_words = transcribed_words - reference_words
        
        return {
            'word_accuracy': word_accuracy,
            'character_accuracy': char_accuracy,
            'correct_words': list(correct_words),
            'missing_words': list(missing_words),
            'extra_words': list(extra_words),
            'total_reference_words': total_reference_words,
            'total_transcribed_words': len(transcribed_words)
        }
    
    def _calculate_character_accuracy(self, transcribed: str, reference: str) -> float:
        """Calculate character-level accuracy using Levenshtein distance"""
        from difflib import SequenceMatcher
        
        # Use sequence matcher for similarity
        similarity = SequenceMatcher(None, transcribed, reference).ratio()
        return similarity
    
    def _analyze_pronunciation(self, audio_file: str, text: str) -> Dict:
        """Analyze pronunciation using our enhanced analyzer"""
        try:
            # Use our enhanced pronunciation analyzer
            analysis = self.pronunciation_analyzer.analyze_pronunciation(audio_file, text)
            return analysis
        except Exception as e:
            print(f"⚠️ Pronunciation analysis failed: {e}")
            return {
                'tajweed_analysis': {'score': 0, 'errors': []},
                'audio_analysis': {},
                'overall_score': 0
            }
    
    def _generate_recitation_feedback(self, transcription: Dict, text_analysis: Dict,
                                    comparison_analysis: Optional[Dict], 
                                    pronunciation_analysis: Dict) -> Dict:
        """Generate comprehensive feedback for the recitation"""
        
        feedback = {
            'transcription_feedback': [],
            'tajweed_feedback': [],
            'pronunciation_feedback': [],
            'comparison_feedback': [],
            'improvement_suggestions': []
        }
        
        # Transcription feedback
        confidence = transcription.get('confidence', 0)
        if confidence < 0.7:
            feedback['transcription_feedback'].append("🎤 Speak more clearly for better transcription")
        else:
            feedback['transcription_feedback'].append("✅ Clear speech detected")
        
        # Tajweed feedback
        tajweed_score = text_analysis['tajweed_analysis']['score']
        if tajweed_score < 100:
            feedback['tajweed_feedback'].append(f"📚 Tajweed Score: {tajweed_score}/100")
            for error in text_analysis['tajweed_analysis']['errors']:
                feedback['tajweed_feedback'].append(f"⚠️ {error['rule']}: {error['message']}")
        else:
            feedback['tajweed_feedback'].append("✅ Excellent Tajweed!")
        
        # Comparison feedback
        if comparison_analysis:
            word_acc = comparison_analysis['word_accuracy']
            if word_acc < 0.8:
                feedback['comparison_feedback'].append(f"📝 Word accuracy: {word_acc:.1%} - Review pronunciation")
            else:
                feedback['comparison_feedback'].append(f"🎯 Great accuracy: {word_acc:.1%}")
        
        # Pronunciation feedback
        if 'feedback' in pronunciation_analysis:
            feedback['pronunciation_feedback'].extend(
                pronunciation_analysis['feedback'].get('pronunciation_feedback', [])
            )
        
        # Improvement suggestions
        if tajweed_score < 80:
            feedback['improvement_suggestions'].append("📖 Study Tajweed rules, especially Ghunnah and Idgham")
        
        if comparison_analysis and comparison_analysis['word_accuracy'] < 0.7:
            feedback['improvement_suggestions'].append("🗣️ Practice pronunciation with reference audio")
        
        return feedback
    
    def _calculate_recitation_score(self, transcription: Dict, text_analysis: Dict,
                                  comparison_analysis: Optional[Dict], 
                                  pronunciation_analysis: Dict) -> int:
        """Calculate overall recitation score"""
        
        # Transcription confidence (20%)
        confidence_score = transcription.get('confidence', 0) * 20
        
        # Tajweed score (40%)
        tajweed_score = text_analysis['tajweed_analysis']['score'] * 0.4
        
        # Comparison accuracy (20%)
        comparison_score = 0
        if comparison_analysis:
            comparison_score = comparison_analysis['word_accuracy'] * 20
        
        # Pronunciation score (20%)
        pronunciation_score = 0
        if 'overall_score' in pronunciation_analysis:
            pronunciation_score = pronunciation_analysis['overall_score'] * 0.2
        
        total_score = confidence_score + tajweed_score + comparison_score + pronunciation_score
        
        return int(min(100, total_score))
    
    def segment_audio_for_analysis(self, audio_file: str, segment_duration: float = 5.0) -> List[Dict]:
        """Segment audio for detailed analysis"""
        
        # Load audio
        y, sr = librosa.load(audio_file)
        
        # Calculate segment parameters
        samples_per_segment = int(segment_duration * sr)
        segments = []
        
        for i in range(0, len(y), samples_per_segment):
            segment_audio = y[i:i + samples_per_segment]
            
            # Save segment to temporary file
            segment_file = f"temp_segment_{i//samples_per_segment}.wav"
            sf.write(segment_file, segment_audio, sr)
            
            # Transcribe segment
            try:
                segment_transcription = self.transcribe_audio(segment_file)
                segments.append({
                    'segment_id': i // samples_per_segment,
                    'start_time': i / sr,
                    'end_time': (i + len(segment_audio)) / sr,
                    'audio_file': segment_file,
                    'transcription': segment_transcription,
                    'analysis': self._analyze_transcribed_text(segment_transcription['text'])
                })
            except Exception as e:
                print(f"⚠️ Error analyzing segment {i // samples_per_segment}: {e}")
            
            # Clean up temporary file
            if os.path.exists(segment_file):
                os.remove(segment_file)
        
        return segments
    
    def save_analysis_report(self, analysis_results: Dict, output_file: str):
        """Save analysis results to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, ensure_ascii=False, indent=2)
            print(f"📄 Analysis report saved to: {output_file}")
        except Exception as e:
            print(f"❌ Error saving report: {e}")

def main():
    """Demo function for Arabic speech recognition"""
    print("🎤 Arabic Speech Recognition Demo")
    print("=" * 50)
    
    # Initialize recognizer
    recognizer = ArabicSpeechRecognizer(model_size="base")
    
    # Example usage
    print("\n📝 Example usage:")
    print("""
    # Transcribe audio
    transcription = recognizer.transcribe_audio("audio_file.wav")
    
    # Analyze recitation
    analysis = recognizer.analyze_recitation("audio_file.wav", "reference_text")
    
    # Save report
    recognizer.save_analysis_report(analysis, "recitation_report.json")
    """)

if __name__ == "__main__":
    main() 