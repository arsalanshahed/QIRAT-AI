import streamlit as st
import os
import soundfile as sf
import uuid
import numpy as np
from analyze_pitch import align_by_first_word, extract_pitch_contour, auto_tune_audio, save_audio
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av

st.title('QIRAT AI: Audio Comparison & Auto-Tune')

st.write('Upload your reference audio, then either record or upload your own audio. After processing, you can play your original, the reference, and your auto-tuned audio.')

ref_file = st.file_uploader('Upload Reference Audio', type=['wav', 'mp3'])

user_input_mode = st.radio('How do you want to provide your audio?', ['Record', 'Upload'])

user_audio = None
user_sr = 48000  # Default for webrtc
user_wav_path = 'user_recorded.wav'

def get_audio_input_devices():
    import streamlit.components.v1 as components
    devices = []
    # Use JS to enumerate devices and return to Streamlit
    device_script = """
    <script>
    navigator.mediaDevices.enumerateDevices().then(devices => {
        const audioInputs = devices.filter(d => d.kind === 'audioinput');
        const deviceList = audioInputs.map(d => ({label: d.label, id: d.deviceId}));
        window.parent.postMessage({deviceList: deviceList}, '*');
    });
    </script>
    """
    components.html(device_script, height=0)
    # Streamlit cannot directly get JS results, so fallback to default
    return devices

audio_device_id = None
if user_input_mode == 'Record':
    # Try to get device list (will be empty unless extended with JS/Streamlit component)
    # For now, allow user to enter device ID manually if needed
    st.info('If you have multiple microphones, you can enter the device ID below (leave blank for default).')
    audio_device_id = st.text_input('Audio Device ID (optional)', '')
    class AudioProcessor(AudioProcessorBase):
        def __init__(self):
            self.frames = []
        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            pcm = frame.to_ndarray()
            self.frames.append(pcm)
            return frame
    constraints = {"audio": {"deviceId": {"exact": audio_device_id}}} if audio_device_id else {"audio": True}
    audio_ctx = webrtc_streamer(
        key="audio",
        mode=WebRtcMode.SENDRECV,
        audio_receiver_size=1024,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints=constraints,
    )
    if audio_ctx and audio_ctx.state.playing and hasattr(audio_ctx, 'audio_processor') and audio_ctx.audio_processor:
        frames = audio_ctx.audio_processor.frames
        if frames:
            user_audio = np.concatenate(frames, axis=1).flatten().astype(np.float32)
            user_audio = user_audio / np.max(np.abs(user_audio))
            sf.write(user_wav_path, user_audio, user_sr)
elif user_input_mode == 'Upload':
    user_file = st.file_uploader('Upload Your Audio', type=['wav', 'mp3'])
    if user_file:
        with open(user_wav_path, 'wb') as f:
            f.write(user_file.read())
        user_audio, user_sr = sf.read(user_wav_path)

if ref_file and user_audio is not None and len(user_audio) > 0:
    # Save reference file
    with open('uploaded_ref.wav', 'wb') as f:
        f.write(ref_file.read())
    # Align reference to user's first word
    user_y, user_sr, aligned_ref_y, ref_sr = align_by_first_word(user_wav_path, 'uploaded_ref.wav')
    save_audio(user_y, user_sr, 'user_aligned.wav')
    save_audio(aligned_ref_y, ref_sr, 'reference_aligned.wav')
    # Auto-tune
    aligned_ref_path = f"temp_aligned_ref_{uuid.uuid4().hex}.wav"
    sf.write(aligned_ref_path, aligned_ref_y, user_sr)
    ref_pitch, _, _ = extract_pitch_contour(aligned_ref_path, hop_length=512)
    corrected_audio, _ = auto_tune_audio(user_wav_path, ref_pitch, 512)
    save_audio(corrected_audio, user_sr, 'user_autotuned.wav')
    os.remove(aligned_ref_path)
    st.header('Playback')
    st.subheader('User Recording')
    st.audio('user_aligned.wav', format='audio/wav')
    st.subheader('Reference Audio (Aligned)')
    st.audio('reference_aligned.wav', format='audio/wav')
    st.subheader('User Audio (Auto-Tuned)')
    st.audio('user_autotuned.wav', format='audio/wav') 