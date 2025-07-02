"""
Pronunciation Assistance (TTS) Module
"""
from gtts import gTTS
import os
import librosa
import numpy as np
import sounddevice as sd
import soundfile as sf
import requests

# Map Qari/Qirat to Quran.com reciter IDs
RECITER_MAP = {
    "Mishary Alafasy (Hafs)": "1",
    "Abdul Basit (Murattal)": "7",
    "Minshawi": "4",
    "Warsh": "10"
}

def play_correct_recitation(surah, ayah, qirat_style="Mishary Alafasy (Hafs)"):
    reciter_id = RECITER_MAP.get(qirat_style, "1")
    surah_str = f"{int(surah):03d}"
    ayah_str = f"{int(ayah):03d}"
    url = f"https://verses.quran.com/{reciter_id}/{surah_str}{ayah_str}.mp3"
    local_filename = f"reference_{reciter_id}_{surah_str}_{ayah_str}.mp3"
    # Download if not cached
    if not os.path.exists(local_filename):
        r = requests.get(url)
        if r.status_code == 200:
            with open(local_filename, 'wb') as f:
                f.write(r.content)
        else:
            raise Exception(f"Failed to fetch audio from Quran.com: {url}")
    # Play audio
    data, sr = sf.read(local_filename)
    sd.play(data, sr)
    sd.wait()
    return local_filename

def compare_user_and_correct(user_audio_path, reference_audio_path):
    # Load audio
    user_y, user_sr = librosa.load(user_audio_path, sr=None)
    ref_y, ref_sr = librosa.load(reference_audio_path, sr=None)
    # Extract MFCCs
    user_mfcc = librosa.feature.mfcc(y=user_y, sr=user_sr, n_mfcc=13)
    ref_mfcc = librosa.feature.mfcc(y=ref_y, sr=ref_sr, n_mfcc=13)
    # DTW alignment
    D, wp = librosa.sequence.dtw(user_mfcc, ref_mfcc, metric='euclidean')
    # Find mismatches (simple threshold on distance)
    mismatches = []
    for i, (u_idx, r_idx) in enumerate(wp[::-1]):
        dist = np.linalg.norm(user_mfcc[:, u_idx] - ref_mfcc[:, r_idx])
        if dist > 50:  # Threshold for mismatch
            time = librosa.frames_to_time(u_idx, sr=user_sr)
            mismatches.append({'timestamp': float(time), 'distance': float(dist)})
    return mismatches 