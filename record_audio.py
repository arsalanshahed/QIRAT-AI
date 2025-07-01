import pyaudio
import wave

def record_audio(filename: str, duration: int = 10, fs: int = 44100, channels: int = 1):
    chunk = 1024
    sample_format = pyaudio.paInt16
    p = pyaudio.PyAudio()
    stream = p.open(format=sample_format, channels=channels, rate=fs,
                    frames_per_buffer=chunk, input=True)
    frames = []
    print(f"Recording for {duration} seconds...")
    for _ in range(0, int(fs / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
    print("Recording finished.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

if __name__ == "__main__":
    record_audio("user_recording.wav", duration=10) 