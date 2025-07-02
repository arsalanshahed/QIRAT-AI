#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Pitch Analysis Module
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