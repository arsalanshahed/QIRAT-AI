from record_audio import record_audio
from analyze_pitch import extract_pitch_contour, plot_pitch_contours, compare_pitch_contours, auto_tune_audio, extract_audio_segment, play_audio_segment, align_by_first_word, segment_audio, save_audio
from feedback import generate_feedback
import os
import sounddevice as sd
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase

if __name__ == "__main__":
    ref_file = input("Enter path to reference file (e.g., C:/Users/ashah/Downloads/azan15.mp3): ").strip()
    if not os.path.exists(ref_file):
        print(f"Reference file '{ref_file}' not found.")
        exit(1)
    duration = int(input("Enter recording duration in seconds (e.g., 120): "))
    user_file = "user_recording.wav"
    record_audio(user_file, duration=duration)
    user_pitch, sr, hop = extract_pitch_contour(user_file)
    ref_pitch, _, _ = extract_pitch_contour(ref_file)
    plot_pitch_contours(user_pitch, ref_pitch, hop, sr)
    diff = compare_pitch_contours(user_pitch, ref_pitch)
    feedback = generate_feedback(diff, hop, sr)
    print("\n--- FEEDBACK ---")
    if not feedback:
        print("Great job! No major pitch issues detected.")
    else:
        for t, msg in feedback:
            print(msg)
            # Play user and reference segments for pitch-off part
            seg_duration = 1.0  # seconds
            user_seg, _ = extract_audio_segment(user_file, t, t + seg_duration)
            ref_seg, _ = extract_audio_segment(ref_file, t, t + seg_duration)
            print("Playing user segment...")
            play_audio_segment(user_seg, sr)
            print("Playing reference segment...")
            play_audio_segment(ref_seg, sr)
        # Optionally auto-tune and play corrected audio
        auto_tune = input("Would you like to hear the auto-tuned version? (y/n): ").strip().lower()
        if auto_tune == 'y':
            corrected_audio, sr = auto_tune_audio(user_file, ref_pitch, hop)
            print("Playing auto-tuned audio...")
            play_audio_segment(corrected_audio, sr)

    # Align reference to user's first word
    user_y, user_sr, aligned_ref_y, ref_sr = align_by_first_word(user_file, ref_file)
    save_audio(user_y, user_sr, 'user_aligned.wav')
    save_audio(aligned_ref_y, ref_sr, 'reference_aligned.wav')
    # Segment both audios into 5s intervals
    user_segments = segment_audio(user_y, user_sr, interval=5.0)
    ref_segments = segment_audio(aligned_ref_y, ref_sr, interval=5.0)
    print("\n--- 5s INTERVAL FEEDBACK ---")
    for i, (u_seg, r_seg) in enumerate(zip(user_segments, ref_segments)):
        print(f"Interval {i+1} (seconds {i*5}-{(i+1)*5}):")
        u_pitch, _, _ = extract_pitch_contour(u_seg, hop_length=512)
        r_pitch, _, _ = extract_pitch_contour(r_seg, hop_length=512)
        diff = compare_pitch_contours(u_pitch, r_pitch)
        feedback = generate_feedback(diff, 512, user_sr)
        if not feedback:
            print("  Great job! No major pitch issues detected.")
        else:
            for t, msg in feedback:
                print(f"  {msg}")
    # Auto-tune the user audio to match the aligned reference
    corrected_audio, _ = auto_tune_audio(user_file, extract_pitch_contour(aligned_ref_y)[0], 512)
    save_audio(corrected_audio, user_sr, 'user_autotuned.wav')
    print("\nSaved files:")
    print("  user_aligned.wav (original user, aligned)")
    print("  user_autotuned.wav (auto-tuned user)")
    print("  reference_aligned.wav (aligned reference)") 