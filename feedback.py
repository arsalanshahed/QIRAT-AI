import numpy as np

def generate_feedback(diff, hop_length, sr, threshold=50):
    feedback = []
    times = np.arange(len(diff)) * hop_length / sr
    for i, d in enumerate(diff):
        if abs(d) > threshold:
            t = times[i]
            msg = f"Pitch off by {d:.1f} Hz at {t:.2f} sec"
            feedback.append((t, msg))
    return feedback

if __name__ == "__main__":
    # Example usage
    diff = np.array([0, 10, 60, -80, 20, 0, 100])
    hop_length = 512
    sr = 44100
    fb = generate_feedback(diff, hop_length, sr)
    for t, msg in fb:
        print(msg) 