import numpy as np
from analyze_pitch import generate_detailed_feedback, analyze_pitch_differences

def generate_feedback(diff, hop_length, sr, threshold=50):
    """
    Legacy function for backward compatibility.
    Now uses the enhanced detailed feedback system.
    """
    # This function is kept for backward compatibility
    # The new system uses generate_detailed_feedback from analyze_pitch.py
    feedback = []
    times = np.arange(len(diff)) * hop_length / sr
    for i, d in enumerate(diff):
        if abs(d) > threshold:
            t = times[i]
            msg = f"Pitch off by {d:.1f} Hz at {t:.2f} sec"
            feedback.append((t, msg))
    return feedback

def generate_comprehensive_feedback(user_pitch, ref_pitch, hop_length, sr, threshold=50):
    """
    Generate comprehensive feedback with detailed analysis.
    This is the main feedback function for the updated system.
    """
    return generate_detailed_feedback(user_pitch, ref_pitch, hop_length, sr, threshold)

def format_feedback_for_display(feedback_list):
    """
    Format feedback for display in web interface or console.
    """
    formatted_output = []
    
    for item in feedback_list:
        timestamp = item['timestamp']
        message = item['message']
        freq_diff = item['freq_diff']
        note_transition = item['note_transition']
        cents_diff = item['cents_diff']
        user_note = item['user_note']
        ref_note = item['ref_note']
        
        # Create formatted display
        display_text = f"⏰ {timestamp:.2f}s | "
        display_text += f"🎵 {user_note} → {ref_note} | "
        display_text += f"📊 {abs(freq_diff):.1f} Hz {'↑' if freq_diff > 0 else '↓'} | "
        display_text += f"🎼 {cents_diff:.0f} cents"
        
        formatted_output.append({
            'timestamp': timestamp,
            'display_text': display_text,
            'full_message': message,
            'freq_diff': freq_diff,
            'note_transition': note_transition,
            'cents_diff': cents_diff,
            'user_note': user_note,
            'ref_note': ref_note
        })
    
    return formatted_output

def get_summary_statistics(feedback_list):
    """
    Generate summary statistics from feedback analysis.
    """
    if not feedback_list:
        return {
            'total_differences': 0,
            'average_deviation_hz': 0,
            'max_deviation_hz': 0,
            'average_deviation_cents': 0,
            'most_common_issue': 'None',
            'accuracy_percentage': 100,
            'high_pitch_count': 0,
            'low_pitch_count': 0
        }
    
    freq_diffs = [abs(item['freq_diff']) for item in feedback_list]
    cents_diffs = [abs(item['cents_diff']) for item in feedback_list]
    
    # Calculate statistics
    avg_freq_diff = np.mean(freq_diffs)
    max_freq_diff = np.max(freq_diffs)
    avg_cents_diff = np.mean(cents_diffs)
    
    # Determine most common issue
    high_pitch_count = sum(1 for item in feedback_list if item['freq_diff'] > 0)
    low_pitch_count = sum(1 for item in feedback_list if item['freq_diff'] < 0)
    
    if high_pitch_count > low_pitch_count:
        most_common_issue = "Singing too high"
    elif low_pitch_count > high_pitch_count:
        most_common_issue = "Singing too low"
    else:
        most_common_issue = "Mixed pitch issues"
    
    # Calculate accuracy percentage (assuming threshold of 50 Hz)
    total_frames = len(feedback_list)  # This is a simplified calculation
    accuracy_percentage = max(0, 100 - (len(feedback_list) / max(total_frames, 1)) * 100)
    
    return {
        'total_differences': len(feedback_list),
        'average_deviation_hz': avg_freq_diff,
        'max_deviation_hz': max_freq_diff,
        'average_deviation_cents': avg_cents_diff,
        'most_common_issue': most_common_issue,
        'accuracy_percentage': accuracy_percentage,
        'high_pitch_count': high_pitch_count,
        'low_pitch_count': low_pitch_count
    }

if __name__ == "__main__":
    # Example usage
    print("Testing enhanced feedback system...")
    
    # Create sample pitch data
    user_pitch = np.array([440, 450, 430, 460, 440])  # A4 with some variations
    ref_pitch = np.array([440, 440, 440, 440, 440])   # Perfect A4
    
    hop_length = 512
    sr = 44100
    
    # Generate detailed feedback
    feedback = generate_detailed_feedback(user_pitch, ref_pitch, hop_length, sr, threshold=10)
    
    print("=== ENHANCED FEEDBACK EXAMPLE ===")
    for item in feedback:
        print(item['message'])
    
    # Format for display
    formatted = format_feedback_for_display(feedback)
    print("\n=== FORMATTED DISPLAY ===")
    for item in formatted:
        print(item['display_text'])
    
    # Get summary statistics
    stats = get_summary_statistics(feedback)
    print("\n=== SUMMARY STATISTICS ===")
    for key, value in stats.items():
        print(f"{key}: {value}") 