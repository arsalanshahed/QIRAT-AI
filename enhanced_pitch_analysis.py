#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Pitch Analysis Module with Arabic Phoneme Detection
5-second segment analysis for QIRAT AI
"""

import librosa
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import soundfile as sf
import os
import json
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import re

# Import our enhanced Tajweed rules
from tajweed_rules import EnhancedTajweedValidator, ArabicPhonemeDetector, generate_tajweed_feedback

# Arabic Phoneme Frequency Ranges (approximate)
ARABIC_PHONEME_FREQUENCIES = {
    # Vowels
    'alif': (200, 800),      # ا
    'waw': (150, 600),       # و  
    'ya': (250, 1000),       # ي
    
    # Consonants by articulation
    'qaf': (100, 400),       # ق - uvular
    'kaf': (200, 800),       # ك - velar
    'ghayn': (150, 500),     # غ - uvular fricative
    'kha': (200, 800),       # خ - velar fricative
    
    'ta': (300, 1200),       # ت - dental
    'tha': (300, 1200),      # ث - interdental
    'dal': (200, 800),       # د - dental
    'dhal': (200, 800),      # ذ - interdental
    'sad': (300, 1500),      # ص - emphatic dental
    'dad': (200, 800),       # ض - emphatic dental
    'ta_emphatic': (200, 800), # ط - emphatic dental
    'za': (200, 800),        # ظ - emphatic interdental
    
    'ba': (150, 600),        # ب - bilabial
    'mim': (150, 600),       # م - bilabial nasal
    'fa': (300, 1200),       # ف - labiodental
    
    'jim': (200, 800),       # ج - palatal
    'shin': (300, 1500),     # ش - palato-alveolar
    'ya': (250, 1000),       # ي - palatal
    
    'lam': (200, 800),       # ل - alveolar
    'nun': (150, 600),       # ن - alveolar nasal
    'ra': (200, 800),        # ر - alveolar trill
    'sin': (300, 1500),      # س - alveolar fricative
    'zay': (300, 1500),      # ز - alveolar fricative
    
    'ha': (200, 800),        # ه - glottal
    'hamza': (200, 800),     # ء - glottal stop
    'ayn': (150, 500),       # ع - pharyngeal
    'ha_pharyngeal': (150, 500), # ح - pharyngeal fricative
}

# Arabic Phoneme Duration Patterns
ARABIC_PHONEME_DURATIONS = {
    'short_vowel': 0.1,      # فتحة، ضمة، كسرة
    'long_vowel': 0.2,       # مد
    'consonant': 0.05,       # حرف ساكن
    'ghunnah': 0.3,          # غنة
    'qalqalah': 0.15,        # قلقة
    'madd': 0.4,             # مد
}

def extract_pitch_contour(audio_file, hop_length=512):
    """Extract pitch contour from audio file"""
    y, sr = librosa.load(audio_file)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr, hop_length=hop_length)
    pitch_contour = []
    for i in range(pitches.shape[1]):
        index = magnitudes[:, i].argmax()
        pitch = pitches[index, i]
        pitch_contour.append(pitch)
    pitch_contour = np.array(pitch_contour)
    return pitch_contour, sr, hop_length

def hz_to_note(frequency):
    """Convert frequency in Hz to musical note name"""
    if frequency <= 0:
        return "Silence"
    
    # A4 = 440 Hz
    A4 = 440.0
    C0 = A4 * (2 ** (-4.75))
    
    if frequency < C0:
        return "Below C0"
    
    # Calculate semitones from C0
    semitones = 12 * np.log2(frequency / C0)
    octave = int(semitones // 12)
    note_index = int(semitones % 12)
    
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    note_name = notes[note_index]
    
    return f"{note_name}{octave}"

def get_note_difference(freq1, freq2):
    """Calculate the difference between two frequencies in semitones and cents"""
    if freq1 <= 0 or freq2 <= 0:
        return 0, 0, "N/A"
    
    # Convert to MIDI note numbers
    midi1 = librosa.hz_to_midi(freq1)
    midi2 = librosa.hz_to_midi(freq2)
    
    # Calculate difference in semitones
    semitone_diff = midi2 - midi1
    
    # Calculate cents (1 semitone = 100 cents)
    cents_diff = semitone_diff * 100
    
    # Get note names
    note1 = hz_to_note(freq1)
    note2 = hz_to_note(freq2)
    
    return semitone_diff, cents_diff, f"{note1} → {note2}"

def segment_audio(y, sr, interval=5.0):
    """Segment audio into fixed-length intervals"""
    segments = []
    total_len = len(y)
    samples_per_interval = int(interval * sr)
    
    for start in range(0, total_len, samples_per_interval):
        end = min(start + samples_per_interval, total_len)
        segments.append(y[start:end])
    
    return segments

def save_audio(y, sr, filename):
    """Save audio to file"""
    sf.write(filename, y, sr)

def align_by_first_word(user_file, ref_file, threshold=0.02):
    """Enhanced alignment by detecting first matching word/sound"""
    user_y, user_sr = librosa.load(user_file)
    ref_y, ref_sr = librosa.load(ref_file)
    
    # Find first non-silent frame in user
    user_energy = np.abs(user_y)
    user_start = int(np.argmax(user_energy > threshold))
    
    # Find first non-silent frame in reference
    ref_energy = np.abs(ref_y)
    ref_start = int(np.argmax(ref_energy > threshold))
    
    # Align reference to user start
    offset = max(0, ref_start - user_start)
    aligned_ref_y = ref_y[offset:offset+len(user_y)]
    
    return user_y, user_sr, aligned_ref_y, ref_sr

class ArabicPronunciationAnalyzer:
    """Advanced Arabic pronunciation analysis with phoneme detection"""
    
    def __init__(self):
        self.tajweed_validator = EnhancedTajweedValidator()
        self.phoneme_detector = ArabicPhonemeDetector()
        self.phoneme_frequencies = ARABIC_PHONEME_FREQUENCIES
        self.phoneme_durations = ARABIC_PHONEME_DURATIONS
    
    def analyze_pronunciation(self, audio_file: str, text: str, ref_audio_file: Optional[str] = None) -> Dict:
        """Comprehensive Arabic pronunciation analysis"""
        
        # Extract audio features
        y, sr = librosa.load(audio_file)
        pitch_contour, _, hop_length = extract_pitch_contour(audio_file)
        
        # Analyze phonemes in text
        phonemes = self.phoneme_detector.extract_phonemes(text)
        
        # Validate Tajweed rules
        tajweed_result = self.tajweed_validator.validate_text(text)
        
        # Analyze audio characteristics
        audio_analysis = self._analyze_audio_characteristics(y, int(sr), pitch_contour, hop_length)
        
        # Compare with reference if provided
        reference_comparison = None
        if ref_audio_file:
            reference_comparison = self._compare_with_reference(audio_file, ref_audio_file, text)
        
        # Generate comprehensive feedback
        feedback = self._generate_comprehensive_feedback(
            tajweed_result, audio_analysis, reference_comparison, phonemes
        )
        
        return {
            'tajweed_analysis': tajweed_result,
            'audio_analysis': audio_analysis,
            'phoneme_analysis': phonemes,
            'reference_comparison': reference_comparison,
            'feedback': feedback,
            'overall_score': self._calculate_overall_score(tajweed_result, audio_analysis, reference_comparison)
        }
    
    def _analyze_audio_characteristics(self, y: np.ndarray, sr: int, pitch_contour: np.ndarray, hop_length: int) -> Dict:
        """Analyze audio characteristics for Arabic pronunciation"""
        
        # Extract various audio features
        features = {}
        
        # Pitch analysis
        features['pitch_mean'] = np.mean(pitch_contour[pitch_contour > 0])
        features['pitch_std'] = np.std(pitch_contour[pitch_contour > 0])
        features['pitch_range'] = np.max(pitch_contour) - np.min(pitch_contour[pitch_contour > 0])
        
        # Duration analysis
        features['total_duration'] = len(y) / sr
        features['speech_duration'] = self._calculate_speech_duration(y, sr)
        
        # Energy analysis
        features['energy_mean'] = np.mean(np.abs(y))
        features['energy_std'] = np.std(np.abs(y))
        
        # Rhythm analysis
        features['rhythm_consistency'] = self._analyze_rhythm_consistency(y, sr)
        
        # Nasal detection (for Ghunnah)
        features['nasal_ratio'] = self._detect_nasal_sounds(y, sr)
        
        # Qalqalah detection
        features['qalqalah_detected'] = self._detect_qalqalah(y, sr)
        
        return features
    
    def _calculate_speech_duration(self, y: np.ndarray, sr: int) -> float:
        """Calculate actual speech duration (excluding silence)"""
        energy = np.abs(y)
        threshold = np.mean(energy) * 0.1
        speech_frames = np.sum(energy > threshold)
        return speech_frames / sr
    
    def _analyze_rhythm_consistency(self, y: np.ndarray, sr: int) -> float:
        """Analyze rhythm consistency using onset detection"""
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        if len(onset_frames) < 2:
            return 0.0
        
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        intervals = np.diff(onset_times)
        
        # Calculate coefficient of variation (lower = more consistent)
        if np.mean(intervals) > 0:
            return 1.0 - (np.std(intervals) / np.mean(intervals))
        return 0.0
    
    def _detect_nasal_sounds(self, y: np.ndarray, sr: int) -> float:
        """Detect nasal sounds (for Ghunnah analysis)"""
        # Simple nasal detection using spectral centroid
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        nasal_threshold = 2000  # Hz - nasal sounds typically below this
        
        nasal_frames = np.sum(spectral_centroids < nasal_threshold)
        total_frames = len(spectral_centroids)
        
        return float(nasal_frames / total_frames if total_frames > 0 else 0.0)
    
    def _detect_qalqalah(self, y: np.ndarray, sr: int) -> bool:
        """Detect Qalqalah (echoing sounds)"""
        # Detect sudden energy bursts that might indicate Qalqalah
        energy = np.abs(y)
        energy_diff = np.diff(energy)
        
        # Look for sharp energy increases followed by decreases
        qalqalah_threshold = np.std(energy_diff) * 2
        qalqalah_candidates = np.sum(np.abs(energy_diff) > qalqalah_threshold)
        
        return bool(qalqalah_candidates > len(energy_diff) * 0.01)  # 1% threshold
    
    def _compare_with_reference(self, user_file: str, ref_file: str, text: str) -> Dict:
        """Compare user pronunciation with reference"""
        
        # Load both audio files
        user_y, user_sr = librosa.load(user_file)
        ref_y, ref_sr = librosa.load(ref_file)
        
        # Extract pitch contours
        user_pitch, _, hop = extract_pitch_contour(user_file)
        ref_pitch, _, _ = extract_pitch_contour(ref_file)
        
        # Align audio files
        user_y, user_sr, aligned_ref_y, ref_sr = align_by_first_word(user_file, ref_file)
        
        # Calculate differences
        min_len = min(len(user_pitch), len(ref_pitch))
        pitch_differences = []
        
        for i in range(min_len):
            if user_pitch[i] > 0 and ref_pitch[i] > 0:
                freq_diff = user_pitch[i] - ref_pitch[i]
                semitone_diff, cents_diff, note_transition = get_note_difference(ref_pitch[i], user_pitch[i])
                
                pitch_differences.append({
                    'frame': i,
                    'time': i * hop / user_sr,
                    'freq_diff': freq_diff,
                    'semitone_diff': semitone_diff,
                    'cents_diff': cents_diff,
                    'note_transition': note_transition
                })
        
        # Calculate overall similarity
        if pitch_differences:
            avg_semitone_diff = np.mean([abs(d['semitone_diff']) for d in pitch_differences])
            similarity_score = max(0, 100 - avg_semitone_diff * 10)  # Convert to 0-100 scale
        else:
            similarity_score = 0
        
        return {
            'pitch_differences': pitch_differences,
            'similarity_score': similarity_score,
            'avg_semitone_diff': avg_semitone_diff if pitch_differences else 0,
            'total_comparisons': len(pitch_differences)
        }
    
    def _generate_comprehensive_feedback(self, tajweed_result: Dict, audio_analysis: Dict, 
                                       reference_comparison: Optional[Dict], phonemes: List[Dict]) -> Dict:
        """Generate comprehensive feedback for the user"""
        
        feedback = {
            'tajweed_feedback': [],
            'pronunciation_feedback': [],
            'audio_quality_feedback': [],
            'improvement_suggestions': []
        }
        
        # Tajweed feedback
        if tajweed_result['score'] < 100:
            feedback['tajweed_feedback'].append(f"Tajweed Score: {tajweed_result['score']}/100")
            for error in tajweed_result['errors']:
                feedback['tajweed_feedback'].append(f"⚠️ {error['message']}")
        else:
            feedback['tajweed_feedback'].append("✅ Excellent Tajweed!")
        
        # Pronunciation feedback based on audio analysis
        if audio_analysis['pitch_std'] > 100:
            feedback['pronunciation_feedback'].append("📈 Consider maintaining more consistent pitch")
        
        if audio_analysis['rhythm_consistency'] < 0.7:
            feedback['pronunciation_feedback'].append("⏱️ Work on maintaining consistent rhythm")
        
        if audio_analysis['nasal_ratio'] < 0.1:
            feedback['pronunciation_feedback'].append("👃 Pay attention to nasal sounds (Ghunnah)")
        
        # Reference comparison feedback
        if reference_comparison:
            if reference_comparison['similarity_score'] < 70:
                feedback['pronunciation_feedback'].append("🎯 Try to match the reference pronunciation more closely")
            else:
                feedback['pronunciation_feedback'].append("🎉 Great job matching the reference!")
        
        # Improvement suggestions
        if tajweed_result['score'] < 80:
            feedback['improvement_suggestions'].append("📚 Review Tajweed rules, especially Ghunnah and Idgham")
        
        if audio_analysis['speech_duration'] < audio_analysis['total_duration'] * 0.8:
            feedback['improvement_suggestions'].append("🗣️ Speak more clearly and reduce pauses")
        
        return feedback
    
    def _calculate_overall_score(self, tajweed_result: Dict, audio_analysis: Dict, 
                                reference_comparison: Optional[Dict]) -> int:
        """Calculate overall pronunciation score"""
        
        # Tajweed score (40% weight)
        tajweed_score = tajweed_result['score'] * 0.4
        
        # Audio quality score (30% weight)
        audio_score = 0
        if audio_analysis['rhythm_consistency'] > 0.8:
            audio_score += 30
        elif audio_analysis['rhythm_consistency'] > 0.6:
            audio_score += 20
        else:
            audio_score += 10
        
        # Reference similarity score (30% weight)
        ref_score = 0
        if reference_comparison:
            ref_score = reference_comparison['similarity_score'] * 0.3
        
        return int(float(tajweed_score + audio_score + ref_score))

def analyze_5second_segments(user_file, ref_file, threshold=50):
    """
    Analyze audio in 5-second segments and identify major pitch differences
    Returns segments with significant pitch differences
    """
    # Align audio files
    user_y, user_sr, aligned_ref_y, ref_sr = align_by_first_word(user_file, ref_file)
    
    # Segment both audio files into 5-second intervals
    user_segments = segment_audio(user_y, user_sr, interval=5.0)
    ref_segments = segment_audio(aligned_ref_y, ref_sr, interval=5.0)
    
    # Ensure both have same number of segments
    min_segments = min(len(user_segments), len(ref_segments))
    user_segments = user_segments[:min_segments]
    ref_segments = ref_segments[:min_segments]
    
    segments_with_differences = []
    
    for i, (user_seg, ref_seg) in enumerate(zip(user_segments, ref_segments)):
        # Save temporary segment files for analysis
        user_seg_file = f"temp_user_seg_{i}.wav"
        ref_seg_file = f"temp_ref_seg_{i}.wav"
        
        save_audio(user_seg, user_sr, user_seg_file)
        save_audio(ref_seg, ref_sr, ref_seg_file)
        
        # Extract pitch contours for this segment
        user_pitch, _, hop = extract_pitch_contour(user_seg_file, hop_length=512)
        ref_pitch, _, _ = extract_pitch_contour(ref_seg_file, hop_length=512)
        
        # Analyze pitch differences in this segment
        segment_differences = analyze_segment_pitch_differences(
            user_pitch, ref_pitch, hop, user_sr, threshold, i * 5.0
        )
        
        # Calculate segment statistics
        segment_stats = calculate_segment_statistics(user_pitch, ref_pitch, hop, user_sr)
        
        # Only include segments with significant differences
        if segment_differences:
            segments_with_differences.append({
                'segment_id': i,
                'start_time': i * 5.0,
                'end_time': (i + 1) * 5.0,
                'differences': segment_differences,
                'statistics': segment_stats,
                'user_segment_file': user_seg_file,
                'ref_segment_file': ref_seg_file,
                'user_pitch_contour': user_pitch.tolist(),
                'ref_pitch_contour': ref_pitch.tolist()
            })
        
        # Clean up temporary files
        if os.path.exists(user_seg_file):
            os.remove(user_seg_file)
        if os.path.exists(ref_seg_file):
            os.remove(ref_seg_file)
    
    return segments_with_differences

def analyze_segment_pitch_differences(user_pitch, ref_pitch, hop_length, sr, threshold=50, segment_start_time=0.0):
    """Analyze pitch differences within a 5-second segment"""
    min_len = min(len(user_pitch), len(ref_pitch))
    differences = []
    
    for i in range(min_len):
        user_freq = user_pitch[i]
        ref_freq = ref_pitch[i]
        
        if user_freq > 0 and ref_freq > 0:
            # Calculate absolute time (segment start + frame time)
            frame_time = i * hop_length / sr
            absolute_time = segment_start_time + frame_time
            
            # Calculate frequency difference
            freq_diff = user_freq - ref_freq
            
            # Only include significant differences
            if abs(freq_diff) > threshold:
                # Calculate note difference
                semitone_diff, cents_diff, note_transition = get_note_difference(ref_freq, user_freq)
                
                differences.append({
                    'timestamp': absolute_time,
                    'segment_time': frame_time,
                    'user_freq': user_freq,
                    'ref_freq': ref_freq,
                    'freq_diff': freq_diff,
                    'semitone_diff': semitone_diff,
                    'cents_diff': cents_diff,
                    'note_transition': note_transition,
                    'user_note': hz_to_note(user_freq),
                    'ref_note': hz_to_note(ref_freq),
                    'direction': 'higher' if freq_diff > 0 else 'lower'
                })
    
    return differences

def calculate_segment_statistics(user_pitch, ref_pitch, hop_length, sr):
    """Calculate comprehensive statistics for a 5-second segment"""
    min_len = min(len(user_pitch), len(ref_pitch))
    
    if min_len == 0:
        return {
            'total_frames': 0,
            'pitch_differences_count': 0,
            'average_deviation_hz': 0,
            'average_deviation_cents': 0,
            'max_deviation_hz': 0,
            'max_deviation_cents': 0,
            'high_pitch_count': 0,
            'low_pitch_count': 0,
            'accuracy_percentage': 100
        }
    
    # Calculate differences for all frames
    differences = []
    high_pitch_count = 0
    low_pitch_count = 0
    valid_frames = 0
    
    for i in range(min_len):
        user_freq = user_pitch[i]
        ref_freq = ref_pitch[i]
        
        if user_freq > 0 and ref_freq > 0:
            valid_frames += 1
            freq_diff = user_freq - ref_freq
            differences.append(freq_diff)
            
            if freq_diff > 0:
                high_pitch_count += 1
            elif freq_diff < 0:
                low_pitch_count += 1
    
    if not differences:
        return {
            'total_frames': min_len,
            'pitch_differences_count': 0,
            'average_deviation_hz': 0,
            'average_deviation_cents': 0,
            'max_deviation_hz': 0,
            'max_deviation_cents': 0,
            'high_pitch_count': 0,
            'low_pitch_count': 0,
            'accuracy_percentage': 100
        }
    
    differences = np.array(differences)
    abs_differences = np.abs(differences)
    
    # Calculate statistics
    avg_deviation_hz = np.mean(abs_differences)
    max_deviation_hz = np.max(abs_differences)
    
    # Convert to cents
    avg_deviation_cents = np.mean([abs(librosa.hz_to_midi(user_freq) - librosa.hz_to_midi(ref_freq)) * 100 
                                  for user_freq, ref_freq in zip(user_pitch, ref_pitch) 
                                  if user_freq > 0 and ref_freq > 0])
    max_deviation_cents = np.max([abs(librosa.hz_to_midi(user_freq) - librosa.hz_to_midi(ref_freq)) * 100 
                                 for user_freq, ref_freq in zip(user_pitch, ref_pitch) 
                                 if user_freq > 0 and ref_freq > 0])
    
    # Calculate accuracy percentage (frames within threshold)
    threshold_frames = np.sum(abs_differences <= 50)  # 50 Hz threshold
    accuracy_percentage = (threshold_frames / len(differences)) * 100 if differences.size > 0 else 100
    
    return {
        'total_frames': min_len,
        'valid_frames': valid_frames,
        'pitch_differences_count': len(differences),
        'average_deviation_hz': float(avg_deviation_hz),
        'average_deviation_cents': float(avg_deviation_cents),
        'max_deviation_hz': float(max_deviation_hz),
        'max_deviation_cents': float(max_deviation_cents),
        'high_pitch_count': int(high_pitch_count),
        'low_pitch_count': int(low_pitch_count),
        'accuracy_percentage': float(accuracy_percentage),
        'std_deviation_hz': float(np.std(abs_differences)),
        'median_deviation_hz': float(np.median(abs_differences))
    }

def generate_segment_feedback(segments_data):
    """Generate comprehensive feedback for 5-second segments"""
    feedback = {
        'total_segments': len(segments_data),
        'segments_with_issues': len(segments_data),
        'overall_summary': '',
        'segment_details': [],
        'recommendations': []
    }
    
    if not segments_data:
        feedback['overall_summary'] = "🎉 Excellent! No significant pitch issues detected in any 5-second segment."
        return feedback
    
    # Analyze each segment
    total_high_pitch = 0
    total_low_pitch = 0
    total_deviation = 0
    worst_segments = []
    
    for segment in segments_data:
        stats = segment['statistics']
        differences = segment['differences']
        
        total_high_pitch += stats['high_pitch_count']
        total_low_pitch += stats['low_pitch_count']
        total_deviation += stats['average_deviation_hz']
        
        # Create segment detail
        segment_detail = {
            'segment_id': segment['segment_id'],
            'time_range': f"{segment['start_time']:.1f}s - {segment['end_time']:.1f}s",
            'issues_count': len(differences),
            'average_deviation': f"{stats['average_deviation_hz']:.1f} Hz",
            'accuracy': f"{stats['accuracy_percentage']:.1f}%",
            'main_issues': []
        }
        
        # Identify main issues in this segment
        if differences:
            # Group issues by type
            high_pitch_issues = [d for d in differences if d['direction'] == 'higher']
            low_pitch_issues = [d for d in differences if d['direction'] == 'lower']
            
            if high_pitch_issues:
                avg_high_deviation = np.mean([abs(d['freq_diff']) for d in high_pitch_issues])
                segment_detail['main_issues'].append(f"Too high: {avg_high_deviation:.1f} Hz average")
            
            if low_pitch_issues:
                avg_low_deviation = np.mean([abs(d['freq_diff']) for d in low_pitch_issues])
                segment_detail['main_issues'].append(f"Too low: {avg_low_deviation:.1f} Hz average")
        
        feedback['segment_details'].append(segment_detail)
        
        # Track worst segments for recommendations
        worst_segments.append({
            'segment_id': segment['segment_id'],
            'time_range': f"{segment['start_time']:.1f}s - {segment['end_time']:.1f}s",
            'deviation': stats['average_deviation_hz'],
            'issues_count': len(differences)
        })
    
    # Sort worst segments by deviation
    worst_segments.sort(key=lambda x: x['deviation'], reverse=True)
    
    # Generate overall summary
    avg_deviation = total_deviation / len(segments_data) if segments_data else 0
    
    if avg_deviation < 30:
        feedback['overall_summary'] = "🎵 Good performance! Minor pitch adjustments needed."
    elif avg_deviation < 60:
        feedback['overall_summary'] = "⚠️ Moderate pitch issues detected. Focus on the problematic segments below."
    else:
        feedback['overall_summary'] = "❌ Significant pitch issues detected. Practice the highlighted segments."
    
    # Generate recommendations
    if total_high_pitch > total_low_pitch:
        feedback['recommendations'].append("🎯 Overall tendency: You're singing slightly higher than the reference")
    else:
        feedback['recommendations'].append("🎯 Overall tendency: You're singing slightly lower than the reference")
    
    if worst_segments:
        feedback['recommendations'].append(f"🎵 Focus on segment {worst_segments[0]['time_range']} (highest deviation: {worst_segments[0]['deviation']:.1f} Hz)")
    
    feedback['recommendations'].append("📝 Practice each problematic segment individually")
    feedback['recommendations'].append("🎧 Listen to the reference audio for each segment")
    
    return feedback

def create_segment_visualization(segments_data):
    """Create visualization for 5-second segments"""
    if not segments_data:
        return None
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Segment accuracy overview
    segment_ids = [seg['segment_id'] for seg in segments_data]
    accuracies = [seg['statistics']['accuracy_percentage'] for seg in segments_data]
    deviations = [seg['statistics']['average_deviation_hz'] for seg in segments_data]
    
    # Color code by accuracy
    colors = ['green' if acc >= 80 else 'orange' if acc >= 60 else 'red' for acc in accuracies]
    
    bars1 = ax1.bar(segment_ids, accuracies, color=colors, alpha=0.7)
    ax1.set_xlabel('5-Second Segment')
    ax1.set_ylabel('Accuracy (%)')
    ax1.set_title('Segment-by-Segment Accuracy')
    ax1.set_ylim(0, 100)
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, acc in zip(bars1, accuracies):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{acc:.1f}%', ha='center', va='bottom')
    
    # Plot 2: Average deviation by segment
    bars2 = ax2.bar(segment_ids, deviations, color='skyblue', alpha=0.7)
    ax2.set_xlabel('5-Second Segment')
    ax2.set_ylabel('Average Deviation (Hz)')
    ax2.set_title('Segment-by-Segment Pitch Deviation')
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, dev in zip(bars2, deviations):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{dev:.1f} Hz', ha='center', va='bottom')
    
    plt.tight_layout()
    return fig

def save_segment_audio_files(segments_data, output_dir="segment_audio"):
    """Save individual segment audio files for user download"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    saved_files = []
    
    for segment in segments_data:
        segment_id = segment['segment_id']
        start_time = segment['start_time']
        end_time = segment['end_time']
        
        # Copy segment files to output directory
        user_seg_file = f"{output_dir}/user_segment_{segment_id}_{start_time:.1f}s_to_{end_time:.1f}s.wav"
        ref_seg_file = f"{output_dir}/ref_segment_{segment_id}_{start_time:.1f}s_to_{end_time:.1f}s.wav"
        
        # Save segment files
        if os.path.exists(segment['user_segment_file']):
            save_audio(segment['user_segment_file'], 22050, user_seg_file)
        if os.path.exists(segment['ref_segment_file']):
            save_audio(segment['ref_segment_file'], 22050, ref_seg_file)
        
        saved_files.append({
            'segment_id': segment_id,
            'time_range': f"{start_time:.1f}s - {end_time:.1f}s",
            'user_file': user_seg_file,
            'ref_file': ref_seg_file
        })
    
    return saved_files 