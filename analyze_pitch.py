import librosa
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import soundfile as sf
import librosa
import inspect
print("pitch_shift location:", librosa.effects.pitch_shift.__module__)
print(inspect.getsource(librosa.effects.pitch_shift))


def extract_pitch_contour(audio_file, hop_length=512):
    y, sr = librosa.load(audio_file)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr, hop_length=hop_length)
    pitch_contour = []
    for i in range(pitches.shape[1]):
        index = magnitudes[:, i].argmax()
        pitch = pitches[index, i]
        pitch_contour.append(pitch)
    pitch_contour = np.array(pitch_contour)
    return pitch_contour, sr, hop_length

def plot_pitch_contours(user_pitch, orig_pitch, hop_length, sr):
    plt.figure(figsize=(12, 4))
    plt.plot(user_pitch, label='User')
    plt.plot(orig_pitch, label='Reference')
    plt.xlabel('Frame')
    plt.ylabel('Pitch (Hz)')
    plt.title('Pitch Contour Comparison')
    plt.legend()
    plt.show()

def compare_pitch_contours(user_pitch, orig_pitch):
    min_len = min(len(user_pitch), len(orig_pitch))
    diff = user_pitch[:min_len] - orig_pitch[:min_len]
    return diff

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

def analyze_pitch_differences(user_pitch, ref_pitch, hop_length, sr, threshold=50):
    """Analyze pitch differences with detailed timestamped feedback"""
    min_len = min(len(user_pitch), len(ref_pitch))
    differences = []
    
    for i in range(min_len):
        user_freq = user_pitch[i]
        ref_freq = ref_pitch[i]
        
        if user_freq > 0 and ref_freq > 0:
            # Calculate time
            time_sec = i * hop_length / sr
            
            # Calculate frequency difference
            freq_diff = user_freq - ref_freq
            
            # Calculate note difference
            semitone_diff, cents_diff, note_transition = get_note_difference(ref_freq, user_freq)
            
            # Only include significant differences
            if abs(freq_diff) > threshold:
                differences.append({
                    'timestamp': time_sec,
                    'user_freq': user_freq,
                    'ref_freq': ref_freq,
                    'freq_diff': freq_diff,
                    'semitone_diff': semitone_diff,
                    'cents_diff': cents_diff,
                    'note_transition': note_transition,
                    'user_note': hz_to_note(user_freq),
                    'ref_note': hz_to_note(ref_freq)
                })
    
    return differences

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

def segment_audio(y, sr, interval=5.0):
    segments = []
    total_len = len(y)
    samples_per_interval = int(interval * sr)
    for start in range(0, total_len, samples_per_interval):
        end = min(start + samples_per_interval, total_len)
        segments.append(y[start:end])
    return segments

def save_audio(y, sr, filename):
    sf.write(filename, y, sr)

def extract_audio_segment(audio_file, start_time, end_time):
    y, sr = librosa.load(audio_file)
    start_sample = int(start_time * sr)
    end_sample = int(end_time * sr)
    return y[start_sample:end_sample], sr

def play_audio_segment(audio_segment, sr):
    sd.play(audio_segment, sr)
    sd.wait()

def generate_detailed_feedback(user_pitch, ref_pitch, hop_length, sr, threshold=50):
    """Generate detailed timestamped feedback with note analysis"""
    differences = analyze_pitch_differences(user_pitch, ref_pitch, hop_length, sr, threshold)
    
    feedback = []
    for diff in differences:
        timestamp = diff['timestamp']
        freq_diff = diff['freq_diff']
        note_transition = diff['note_transition']
        cents_diff = diff['cents_diff']
        
        # Create detailed feedback message
        if freq_diff > 0:
            direction = "higher"
        else:
            direction = "lower"
        
        message = f"At {timestamp:.2f}s: Pitch is {abs(freq_diff):.1f} Hz {direction} than reference"
        message += f" ({note_transition}, {cents_diff:.0f} cents)"
        
        feedback.append({
            'timestamp': timestamp,
            'message': message,
            'freq_diff': freq_diff,
            'note_transition': note_transition,
            'cents_diff': cents_diff,
            'user_note': diff['user_note'],
            'ref_note': diff['ref_note']
        })
    
    return feedback

if __name__ == "__main__":
    user_file = "user_recording.wav"
    ref_file = "azan15.mp3"
    user_pitch, sr, hop = extract_pitch_contour(user_file)
    ref_pitch, _, _ = extract_pitch_contour(ref_file)
    plot_pitch_contours(user_pitch, ref_pitch, hop, sr)
    
    # Generate detailed feedback
    feedback = generate_detailed_feedback(user_pitch, ref_pitch, hop, sr)
    
    print("=== DETAILED PITCH ANALYSIS ===")
    for item in feedback:
        print(item['message'])
    
    print(f"\nTotal pitch differences detected: {len(feedback)}") 