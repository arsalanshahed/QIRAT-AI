from record_audio import record_audio
from analyze_pitch import extract_pitch_contour, plot_pitch_contours, compare_pitch_contours, extract_audio_segment, play_audio_segment, align_by_first_word, segment_audio, save_audio, generate_detailed_feedback, analyze_pitch_differences
from feedback import generate_comprehensive_feedback, format_feedback_for_display, get_summary_statistics
import os
import sounddevice as sd
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase

if __name__ == "__main__":
    print("🎵 QIRAT AI: Enhanced Pitch Analysis System")
    print("=" * 50)
    
    # Get reference file
    ref_file = input("Enter path to reference file (e.g., C:/Users/ashah/Downloads/azan15.mp3): ").strip()
    if not os.path.exists(ref_file):
        print(f"❌ Reference file '{ref_file}' not found.")
        exit(1)
    
    # Get recording duration
    duration = int(input("Enter recording duration in seconds (e.g., 120): "))
    user_file = "user_recording.wav"
    
    # Record user audio
    print(f"\n🎤 Recording for {duration} seconds...")
    record_audio(user_file, duration=duration)
    print("✅ Recording completed!")
    
    # Extract pitch contours
    print("\n📊 Analyzing pitch contours...")
    user_pitch, sr, hop = extract_pitch_contour(user_file)
    ref_pitch, _, _ = extract_pitch_contour(ref_file)
    
    # Plot pitch contours
    print("📈 Generating pitch comparison plot...")
    plot_pitch_contours(user_pitch, ref_pitch, hop, sr)
    
    # Generate detailed feedback
    print("\n🔍 Generating detailed pitch analysis...")
    detailed_feedback = generate_detailed_feedback(user_pitch, ref_pitch, hop, sr)
    
    # Format feedback for display
    formatted_feedback = format_feedback_for_display(detailed_feedback)
    
    # Get summary statistics
    stats = get_summary_statistics(detailed_feedback)
    
    # Display results
    print("\n" + "=" * 60)
    print("📋 DETAILED PITCH ANALYSIS RESULTS")
    print("=" * 60)
    
    # Summary statistics
    print(f"\n📊 SUMMARY STATISTICS:")
    print(f"   • Total pitch differences detected: {stats['total_differences']}")
    print(f"   • Average deviation: {stats['average_deviation_hz']:.1f} Hz ({stats['average_deviation_cents']:.0f} cents)")
    print(f"   • Maximum deviation: {stats['max_deviation_hz']:.1f} Hz")
    print(f"   • Most common issue: {stats['most_common_issue']}")
    print(f"   • Accuracy percentage: {stats['accuracy_percentage']:.1f}%")
    print(f"   • High pitch instances: {stats['high_pitch_count']}")
    print(f"   • Low pitch instances: {stats['low_pitch_count']}")
    
    # Detailed feedback
    if detailed_feedback:
        print(f"\n🎵 DETAILED TIMESTAMPED FEEDBACK:")
        print("-" * 60)
        for item in formatted_feedback:
            print(f"   {item['display_text']}")
        
        # Option to play problematic segments
        print(f"\n🎧 Would you like to hear specific problematic segments? (y/n): ", end="")
        play_segments = input().strip().lower()
        
        if play_segments == 'y':
            print("\n🎵 Playing problematic segments for comparison...")
            for i, item in enumerate(detailed_feedback[:5]):  # Limit to first 5 segments
                timestamp = item['timestamp']
                print(f"\n   Segment {i+1}: {item['message']}")
                
                # Extract and play user segment
                seg_duration = 1.0  # seconds
                user_seg, _ = extract_audio_segment(user_file, timestamp, timestamp + seg_duration)
                print("   Playing user segment...")
                play_audio_segment(user_seg, sr)
                
                # Extract and play reference segment
                ref_seg, _ = extract_audio_segment(ref_file, timestamp, timestamp + seg_duration)
                print("   Playing reference segment...")
                play_audio_segment(ref_seg, sr)
                
                # Ask if user wants to continue
                if i < 4:  # Don't ask after the last segment
                    print("   Continue to next segment? (y/n): ", end="")
                    if input().strip().lower() != 'y':
                        break
    else:
        print("\n🎉 EXCELLENT! No significant pitch differences detected.")
        print("   Your performance matches the reference very well!")
    
    # Enhanced alignment and segment analysis
    print(f"\n🔄 Performing enhanced word-by-word alignment...")
    user_y, user_sr, aligned_ref_y, ref_sr = align_by_first_word(user_file, ref_file)
    save_audio(user_y, user_sr, 'user_aligned.wav')
    save_audio(aligned_ref_y, ref_sr, 'reference_aligned.wav')
    
    # Segment analysis
    print(f"\n📊 Performing segment-by-segment analysis...")
    user_segments = segment_audio(user_y, user_sr, interval=5.0)
    ref_segments = segment_audio(aligned_ref_y, ref_sr, interval=5.0)
    
    print(f"\n🎵 5-SECOND INTERVAL ANALYSIS:")
    print("-" * 50)
    
    for i, (u_seg, r_seg) in enumerate(zip(user_segments, ref_segments)):
        print(f"\n   Interval {i+1} (seconds {i*5}-{(i+1)*5}):")
        
        # Save segments for analysis
        u_seg_file = f"temp_user_seg_{i}.wav"
        r_seg_file = f"temp_ref_seg_{i}.wav"
        save_audio(u_seg, user_sr, u_seg_file)
        save_audio(r_seg, ref_sr, r_seg_file)
        
        # Analyze segments
        u_pitch, _, _ = extract_pitch_contour(u_seg_file, hop_length=512)
        r_pitch, _, _ = extract_pitch_contour(r_seg_file, hop_length=512)
        
        # Get segment feedback
        segment_feedback = generate_detailed_feedback(u_pitch, r_pitch, 512, user_sr)
        
        if not segment_feedback:
            print("     ✅ Great job! No major pitch issues detected.")
        else:
            print(f"     ⚠️  {len(segment_feedback)} pitch differences detected:")
            for item in segment_feedback[:3]:  # Show first 3 issues
                print(f"        • {item['message']}")
            if len(segment_feedback) > 3:
                print(f"        • ... and {len(segment_feedback) - 3} more")
        
        # Clean up temporary files
        os.remove(u_seg_file)
        os.remove(r_seg_file)
    
    # Final summary
    print(f"\n" + "=" * 60)
    print("📁 OUTPUT FILES GENERATED:")
    print("=" * 60)
    print("   • user_aligned.wav - Your recording (aligned to reference)")
    print("   • reference_aligned.wav - Reference audio (aligned to your start)")
    print("   • user_recording.wav - Your original recording")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    print("-" * 30)
    if stats['total_differences'] > 0:
        if stats['high_pitch_count'] > stats['low_pitch_count']:
            print("   • Focus on singing slightly lower")
        else:
            print("   • Focus on singing slightly higher")
        print("   • Practice the specific timestamps mentioned above")
        print("   • Use the aligned audio files for practice")
    else:
        print("   • Excellent pitch accuracy! Keep up the great work!")
        print("   • Continue practicing to maintain consistency")
    
    print(f"\n✨ Analysis complete! Thank you for using QIRAT AI!") 