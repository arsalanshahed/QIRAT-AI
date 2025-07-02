"""
Real-Time Feedback Module
"""
import time
import random
from vosk import Model, KaldiRecognizer
import wave
import json as js

def stream_asr_and_tajweed(audio_path, reference_text):
    model_path = "models/vosk-model-ar-mgb2-0.4"
    if audio_path:
        yield from stream_vosk_asr(audio_path, model_path, reference_text)
    else:
        # Fallback: Simulate streaming by splitting reference_text into words
        words = reference_text.split()
        for i, word in enumerate(words):
            time.sleep(0.5)
            feedback = {"word": word, "correct": random.random() > 0.2, "error": None}
            if not feedback["correct"]:
                feedback["error"] = random.choice(["Tajweed", "Pronunciation"])
            yield feedback

def stream_vosk_asr(audio_path, model_path, reference_text=None):
    model = Model(model_path)
    wf = wave.open(audio_path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = js.loads(rec.Result())
            for word in res.get("result", []):
                feedback = {"word": word["word"], "start": word["start"], "end": word["end"], "correct": True, "error": None}
                # Optionally compare to reference_text for correctness
                yield feedback
    # Final partial
    res = js.loads(rec.FinalResult())
    for word in res.get("result", []):
        feedback = {"word": word["word"], "start": word["start"], "end": word["end"], "correct": True, "error": None}
        yield feedback 