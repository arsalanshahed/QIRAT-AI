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

def auto_tune_audio(audio_file, target_pitch_contour, hop_length=512):
    y, sr = librosa.load(audio_file)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr, hop_length=hop_length)
    corrected_audio = np.zeros_like(y)
    frame_length = hop_length
    for i in range(pitches.shape[1]):
        index = magnitudes[:, i].argmax()
        user_pitch = pitches[index, i]
        if user_pitch > 0 and target_pitch_contour[i] > 0:
            n_steps = librosa.hz_to_midi(target_pitch_contour[i]) - librosa.hz_to_midi(user_pitch)
            start = i * hop_length
            end = min(len(y), start + frame_length)
            shifted = librosa.effects.pitch_shift(y[start:end], sr=sr, n_steps=n_steps)
            corrected_audio[start:end] += shifted
        else:
            start = i * hop_length
            end = min(len(y), start + frame_length)
            corrected_audio[start:end] += y[start:end]
    return corrected_audio, sr

def extract_audio_segment(audio_file, start_time, end_time):
    y, sr = librosa.load(audio_file)
    start_sample = int(start_time * sr)
    end_sample = int(end_time * sr)
    return y[start_sample:end_sample], sr

def play_audio_segment(audio_segment, sr):
    sd.play(audio_segment, sr)
    sd.wait()

def align_by_first_word(user_file, ref_file, threshold=0.02):
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

if __name__ == "__main__":
    user_file = "user_recording.wav"
    ref_file = "azan15.mp3"
    user_pitch, sr, hop = extract_pitch_contour(user_file)
    ref_pitch, _, _ = extract_pitch_contour(ref_file)
    plot_pitch_contours(user_pitch, ref_pitch, hop, sr)
    diff = compare_pitch_contours(user_pitch, ref_pitch)
    print(f"Mean pitch difference: {np.mean(np.abs(diff)):.2f} Hz") 