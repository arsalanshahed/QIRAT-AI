#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arabic ASR (Automatic Speech Recognition) Module
Using OpenAI Whisper for Arabic transcription and analysis
"""

import whisper
import torch
import numpy as np
import librosa
import soundfile as sf
import json
import re
from typing import Dict, List, Tuple, Optional
import arabic_reshaper
from bidi.algorithm import get_display
# Arabic text processing functions (fallback if pyarabic not available)
def strip_tashkeel(text):
    """Remove Arabic diacritics (tashkeel)"""
    import re
    # Remove Arabic diacritics
    tashkeel_pattern = re.compile(r'[\u064B-\u065F\u0670]')
    return tashkeel_pattern.sub('', text)

def strip_tatweel(text):
    """Remove Arabic tatweel (stretching)"""
    import re
    # Remove tatweel character
    return text.replace('\u0640', '')

def strip_shadda(text):
    """Remove Arabic shadda (doubling)"""
    import re
    # Remove shadda character
    return text.replace('\u0651', '')
import os
import tempfile

class ArabicASR:
    def __init__(self, model_size="base"):
        """
        Initialize Arabic ASR with Whisper model
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
        """
        self.model_size = model_size
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.load_model()
        
    def load_model(self):
        """Load Whisper model"""
        try:
            print(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size, device=self.device)
            print(f"Model loaded successfully on {self.device}")
        except Exception as e:
            print(f"Error loading model: {e}")
            # Fallback to CPU if CUDA fails
            if self.device == "cuda":
                print("Falling back to CPU")
                self.device = "cpu"
                self.model = whisper.load_model(self.model_size, device=self.device)
    
    def transcribe_audio(self, audio_file: str, language="ar") -> Dict:
        """
        Transcribe Arabic audio using Whisper
        
        Args:
            audio_file: Path to audio file
            language: Language code (default: "ar" for Arabic)
            
        Returns:
            Dictionary containing transcription results
        """
        try:
            # Check if model is loaded
            if self.model is None:
                return {
                    "text": "",
                    "segments": [],
                    "language": language,
                    "success": False,
                    "error": "Model not loaded"
                }
            
            # Load and transcribe audio
            result = self.model.transcribe(
                audio_file,
                language=language,
                task="transcribe",
                verbose=True
            )
            
            return {
                "text": result["text"],
                "segments": result["segments"],
                "language": result["language"],
                "success": True
            }
            
        except Exception as e:
            return {
                "text": "",
                "segments": [],
                "language": language,
                "success": False,
                "error": str(e)
            }
    
    def clean_arabic_text(self, text: str) -> str:
        """
        Clean and normalize Arabic text
        
        Args:
            text: Raw Arabic text
            
        Returns:
            Cleaned Arabic text
        """
        # Remove diacritics (tashkeel)
        text = strip_tashkeel(text)
        
        # Remove tatweel (stretching)
        text = strip_tatweel(text)
        
        # Remove shadda (doubling)
        text = strip_shadda(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Reshape Arabic text for proper display
        text = arabic_reshaper.reshape(text)
        text = get_display(text)
        
        return text
    
    def extract_phonemes(self, text: str) -> List[str]:
        """
        Extract Arabic phonemes from text
        
        Args:
            text: Arabic text
            
        Returns:
            List of phonemes
        """
        # Arabic phoneme mapping
        arabic_phonemes = {
            'ا': 'alif', 'ب': 'ba', 'ت': 'ta', 'ث': 'tha', 'ج': 'jim',
            'ح': 'ha', 'خ': 'kha', 'د': 'dal', 'ذ': 'dhal', 'ر': 'ra',
            'ز': 'zay', 'س': 'sin', 'ش': 'shin', 'ص': 'sad', 'ض': 'dad',
            'ط': 'ta', 'ظ': 'za', 'ع': 'ayn', 'غ': 'ghayn', 'ف': 'fa',
            'ق': 'qaf', 'ك': 'kaf', 'ل': 'lam', 'م': 'mim', 'ن': 'nun',
            'ه': 'ha', 'و': 'waw', 'ي': 'ya', 'ة': 'ta_marbuta', 'ء': 'hamza'
        }
        
        phonemes = []
        for char in text:
            if char in arabic_phonemes:
                phonemes.append(arabic_phonemes[char])
            elif char.isspace():
                phonemes.append('space')
            else:
                phonemes.append('unknown')
        
        return phonemes
    
    def align_text_audio(self, audio_file: str, reference_text: str) -> Dict:
        """
        Align Arabic text with audio using Whisper
        
        Args:
            audio_file: Path to audio file
            reference_text: Reference Arabic text
            
        Returns:
            Dictionary with alignment results
        """
        try:
            # Transcribe audio
            transcription = self.transcribe_audio(audio_file)
            
            if not transcription["success"]:
                return {"success": False, "error": transcription.get("error", "Transcription failed")}
            
            # Get segments with timestamps
            segments = transcription["segments"]
            
            # Clean reference text
            clean_ref_text = self.clean_arabic_text(reference_text)
            trans_result = self.transcribe_audio(audio_file)
            clean_trans_text = trans_result["text"] if trans_result["success"] else ""
            
            # Simple word-level alignment
            alignment = self._simple_word_alignment(segments, clean_ref_text, clean_trans_text)
            
            return {
                "success": True,
                "transcription": clean_trans_text,
                "reference": clean_ref_text,
                "segments": segments,
                "alignment": alignment,
                "accuracy": self._calculate_accuracy(clean_ref_text, clean_trans_text)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _simple_word_alignment(self, segments: List, ref_text: str, trans_text: str) -> List:
        """
        Simple word-level alignment between reference and transcription
        
        Args:
            segments: Whisper segments with timestamps
            ref_text: Reference text
            trans_text: Transcribed text
            
        Returns:
            List of aligned words with timestamps
        """
        # Split texts into words
        ref_words = ref_text.split()
        trans_words = trans_text.split()
        
        alignment = []
        
        # Simple mapping (can be improved with more sophisticated algorithms)
        for i, segment in enumerate(segments):
            segment_words = segment["text"].split()
            
            for j, word in enumerate(segment_words):
                if j < len(ref_words):
                    alignment.append({
                        "word": word,
                        "reference_word": ref_words[j] if j < len(ref_words) else "",
                        "start_time": segment["start"],
                        "end_time": segment["end"],
                        "confidence": segment.get("avg_logprob", 0.0)
                    })
        
        return alignment
    
    def _calculate_accuracy(self, ref_text: str, trans_text: str) -> float:
        """
        Calculate transcription accuracy using character-level comparison
        
        Args:
            ref_text: Reference text
            trans_text: Transcribed text
            
        Returns:
            Accuracy percentage
        """
        # Remove spaces for comparison
        ref_clean = re.sub(r'\s+', '', ref_text)
        trans_clean = re.sub(r'\s+', '', trans_text)
        
        if len(ref_clean) == 0:
            return 0.0
        
        # Calculate character-level accuracy
        correct_chars = sum(1 for a, b in zip(ref_clean, trans_clean) if a == b)
        total_chars = len(ref_clean)
        
        return (correct_chars / total_chars) * 100
    
    def detect_pronunciation_errors(self, audio_file: str, reference_text: str) -> Dict:
        """
        Detect pronunciation errors by comparing audio with reference text
        
        Args:
            audio_file: Path to audio file
            reference_text: Reference Arabic text
            
        Returns:
            Dictionary with pronunciation analysis
        """
        try:
            # Get alignment
            alignment_result = self.align_text_audio(audio_file, reference_text)
            
            if not alignment_result["success"]:
                return {"success": False, "error": alignment_result["error"]}
            
            # Analyze pronunciation
            errors = []
            alignment = alignment_result["alignment"]
            
            for item in alignment:
                if item["confidence"] < -0.5:  # Low confidence threshold
                    errors.append({
                        "word": item["word"],
                        "reference_word": item["reference_word"],
                        "start_time": item["start_time"],
                        "end_time": item["end_time"],
                        "confidence": item["confidence"],
                        "error_type": "pronunciation",
                        "message": f"Possible pronunciation error in '{item['word']}'"
                    })
            
            return {
                "success": True,
                "errors": errors,
                "total_errors": len(errors),
                "accuracy": alignment_result["accuracy"],
                "alignment": alignment
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def extract_audio_features(self, audio_file: str) -> Dict:
        """
        Extract audio features for analysis
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Dictionary with audio features
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_file)
            
            # Extract features
            features = {
                "duration": len(y) / sr,
                "sample_rate": sr,
                "rms_energy": np.sqrt(np.mean(y**2)),
                "spectral_centroid": np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)),
                "spectral_rolloff": np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)),
                "zero_crossing_rate": np.mean(librosa.feature.zero_crossing_rate(y)),
                "mfcc": np.mean(librosa.feature.mfcc(y=y, sr=sr), axis=1).tolist()
            }
            
            return {"success": True, "features": features}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Utility functions
def test_arabic_asr():
    """Test Arabic ASR functionality"""
    print("Testing Arabic ASR...")
    
    # Initialize ASR
    asr = ArabicASR(model_size="base")
    
    # Test with sample audio (if available)
    test_files = ["azan15.mp3", "quran_recitation_02b5b653.wav"]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\nTesting with {test_file}...")
            
            # Test transcription
            result = asr.transcribe_audio(test_file)
            if result["success"]:
                print(f"Transcription: {result['text'][:100]}...")
                print(f"Language detected: {result['language']}")
            else:
                print(f"Transcription failed: {result.get('error', 'Unknown error')}")
            
            # Test audio features
            features = asr.extract_audio_features(test_file)
            if features["success"]:
                print(f"Duration: {features['features']['duration']:.2f}s")
                print(f"RMS Energy: {features['features']['rms_energy']:.4f}")
            else:
                print(f"Feature extraction failed: {features.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_arabic_asr() 