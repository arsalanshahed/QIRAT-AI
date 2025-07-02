import streamlit as st
import os
import soundfile as sf
import uuid
import numpy as np
from analyze_pitch import align_by_first_word, extract_pitch_contour, save_audio, generate_detailed_feedback, analyze_pitch_differences
from feedback import format_feedback_for_display, get_summary_statistics
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av
import matplotlib.pyplot as plt
import pandas as pd
import requests
from urllib.parse import urlparse
import tempfile
import yt_dlp
import re

st.set_page_config(page_title="QIRAT AI: Enhanced Pitch Analysis", layout="wide")

st.title('🎵 QIRAT AI: Enhanced Pitch Analysis System')
st.write('Compare your audio recording with a reference and get detailed, timestamped pitch analysis with note-by-note feedback.')

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    feedback_threshold = st.slider("Feedback Threshold (Hz)", 10, 100, 50, help="Lower values = more sensitive feedback")
    show_notes = st.checkbox("Show Musical Notes", True, help="Display musical note names (C4, A4, etc.)")
    show_cents = st.checkbox("Show Cents", True, help="Display pitch differences in cents")

def is_youtube_url(url):
    """Check if the URL is a valid YouTube URL."""
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+'
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return True
    return False

def extract_video_info(youtube_url):
    """Extract video information from YouTube URL."""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            return {
                'title': info.get('title', 'Unknown Title'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown Uploader'),
                'view_count': info.get('view_count', 0),
                'thumbnail': info.get('thumbnail', ''),
                'description': info.get('description', '')[:200] + '...' if info.get('description', '') else ''
            }
    except Exception as e:
        st.error(f"❌ Error extracting video info: {str(e)}")
        return None

def download_youtube_audio(youtube_url, filename="youtube_audio"):
    """
    Download audio from YouTube URL and save it locally.
    Returns the path to the downloaded file.
    """
    try:
        # Validate YouTube URL
        if not is_youtube_url(youtube_url):
            raise ValueError("Invalid YouTube URL format")
        
        # Extract video info first
        video_info = extract_video_info(youtube_url)
        if not video_info:
            raise ValueError("Could not extract video information")
        
        # Display video info
        st.info(f"📺 **{video_info['title']}**")
        st.info(f"👤 Uploader: {video_info['uploader']}")
        if video_info['duration'] > 0:
            duration_min = video_info['duration'] // 60
            duration_sec = video_info['duration'] % 60
            st.info(f"⏱️ Duration: {duration_min}:{duration_sec:02d}")
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'temp_{filename}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [lambda d: st.progress(d.get('downloaded_bytes', 0) / max(d.get('total_bytes', 1), 1)) if d['status'] == 'downloading' else None],
        }
        
        # Download the audio
        with st.spinner(f"🎵 Downloading audio from YouTube..."):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
        
        # Find the downloaded file
        downloaded_file = None
        for file in os.listdir('.'):
            if file.startswith(f'temp_{filename}') and file.endswith('.mp3'):
                downloaded_file = file
                break
        
        if downloaded_file:
            st.success(f"✅ Successfully downloaded audio from YouTube!")
            return downloaded_file
        else:
            raise ValueError("Downloaded file not found")
            
    except Exception as e:
        st.error(f"❌ Failed to download from YouTube: {str(e)}")
        return None

def download_audio_from_url(url, filename="downloaded_audio"):
    """
    Download audio file from URL and save it locally.
    Returns the path to the downloaded file.
    """
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format")
        
        # Download the file
        with st.spinner(f"Downloading audio from {url}..."):
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Determine file extension from URL or content-type
            content_type = response.headers.get('content-type', '')
            if 'audio' in content_type:
                if 'mp3' in content_type:
                    ext = '.mp3'
                elif 'wav' in content_type:
                    ext = '.wav'
                elif 'mpeg' in content_type:
                    ext = '.mp3'
                else:
                    ext = '.mp3'  # Default to mp3
            else:
                # Try to get extension from URL
                path = parsed_url.path
                if path.endswith('.mp3'):
                    ext = '.mp3'
                elif path.endswith('.wav'):
                    ext = '.wav'
                elif path.endswith('.m4a'):
                    ext = '.m4a'
                else:
                    ext = '.mp3'  # Default to mp3
            
            # Create temporary file
            temp_file = f"temp_{filename}{ext}"
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = downloaded / total_size
                            st.progress(progress)
            
            st.success(f"✅ Successfully downloaded audio file!")
            return temp_file
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to download from URL: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Error processing URL: {str(e)}")
        return None

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📁 Reference Audio Input")
    
    # Reference input method selection
    ref_input_method = st.radio(
        'Reference Audio Source', 
        ['Upload File', 'Download from URL', 'YouTube Link'], 
        help="Choose how to provide reference audio"
    )
    
    ref_file = None
    ref_file_path = None
    
    if ref_input_method == 'Upload File':
        ref_file = st.file_uploader(
            'Reference Audio File', 
            type=['wav', 'mp3', 'm4a'], 
            help="Upload your reference audio file"
        )
        if ref_file:
            ref_file_path = f"uploaded_ref_{uuid.uuid4().hex[:8]}.wav"
            with open(ref_file_path, 'wb') as f:
                f.write(ref_file.read())
            st.success("✅ Reference audio uploaded successfully!")
    
    elif ref_input_method == 'Download from URL':
        st.info("🌐 Enter a direct link to an audio file (MP3, WAV, M4A)")
        
        # URL input with examples
        url_examples = [
            "https://example.com/audio.mp3",
            "https://example.com/recording.wav",
            "https://example.com/song.m4a"
        ]
        
        with st.expander("💡 URL Examples"):
            for example in url_examples:
                st.code(example)
        
        ref_url = st.text_input(
            'Audio URL',
            placeholder="https://example.com/audio.mp3",
            help="Enter the direct URL to your reference audio file"
        )
        
        if ref_url:
            if st.button("🔽 Download Reference Audio"):
                ref_file_path = download_audio_from_url(ref_url, "reference_audio")
                if ref_file_path:
                    st.session_state['ref_file_path'] = ref_file_path
                    st.success(f"✅ Reference audio downloaded as: {ref_file_path}")
        
        # Show downloaded file if available
        if 'ref_file_path' in st.session_state and os.path.exists(st.session_state['ref_file_path']):
            ref_file_path = st.session_state['ref_file_path']
            st.success(f"📁 Reference file ready: {os.path.basename(ref_file_path)}")
            
            # Option to remove downloaded file
            if st.button("🗑️ Remove Downloaded File"):
                if os.path.exists(ref_file_path):
                    os.remove(ref_file_path)
                if 'ref_file_path' in st.session_state:
                    del st.session_state['ref_file_path']
                st.rerun()
    
    elif ref_input_method == 'YouTube Link':
        st.info("📺 Enter a YouTube video link to extract audio")
        
        # YouTube URL examples
        youtube_examples = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ"
        ]
        
        with st.expander("💡 YouTube URL Examples"):
            for example in youtube_examples:
                st.code(example)
        
        youtube_url = st.text_input(
            'YouTube URL',
            placeholder="https://www.youtube.com/watch?v=...",
            help="Enter the YouTube video URL"
        )
        
        if youtube_url:
            if st.button("🎵 Download YouTube Audio"):
                ref_file_path = download_youtube_audio(youtube_url, "youtube_reference")
                if ref_file_path:
                    st.session_state['ref_file_path'] = ref_file_path
                    st.success(f"✅ YouTube audio downloaded as: {ref_file_path}")
        
        # Show downloaded file if available
        if 'ref_file_path' in st.session_state and os.path.exists(st.session_state['ref_file_path']):
            ref_file_path = st.session_state['ref_file_path']
            st.success(f"📁 Reference file ready: {os.path.basename(ref_file_path)}")
            
            # Option to remove downloaded file
            if st.button("🗑️ Remove Downloaded File"):
                if os.path.exists(ref_file_path):
                    os.remove(ref_file_path)
                if 'ref_file_path' in st.session_state:
                    del st.session_state['ref_file_path']
                st.rerun()

with col2:
    st.subheader("🎤 User Audio Input")
    user_input_mode = st.radio('Input Method', ['Record', 'Upload'], help="Choose how to provide your audio")

user_audio = None
user_sr = 48000  # Default for webrtc
user_wav_path = 'user_recorded.wav'

if user_input_mode == 'Record':
    st.info("🎙️ Click 'Start' to begin recording. Speak or sing clearly into your microphone.")
    
    class AudioProcessor(AudioProcessorBase):
        def __init__(self):
            self.frames = []
        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            pcm = frame.to_ndarray()
            self.frames.append(pcm)
            return frame
    
    # Device selection
    audio_device_id = st.text_input('Audio Device ID (optional)', '', help="Leave blank for default device")
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
            st.success("✅ Recording completed!")

elif user_input_mode == 'Upload':
    user_file = st.file_uploader('Upload Your Audio', type=['wav', 'mp3', 'm4a'], help="Upload your audio file")
    if user_file:
        with open(user_wav_path, 'wb') as f:
            f.write(user_file.read())
        user_audio, user_sr = sf.read(user_wav_path)
        st.success("✅ Audio uploaded successfully!")

# Analysis section
if ref_file_path and user_audio is not None and len(user_audio) > 0:
    st.header("🔍 Analysis Results")
    
    with st.spinner("Processing audio and generating analysis..."):
        # Align reference to user's first word
        user_y, user_sr, aligned_ref_y, ref_sr = align_by_first_word(user_wav_path, ref_file_path)
        save_audio(user_y, user_sr, 'user_aligned.wav')
        save_audio(aligned_ref_y, ref_sr, 'reference_aligned.wav')
        
        # Extract pitch contours
        user_pitch, sr, hop = extract_pitch_contour('user_aligned.wav', hop_length=512)
        ref_pitch, _, _ = extract_pitch_contour('reference_aligned.wav', hop_length=512)
        
        # Generate detailed feedback
        detailed_feedback = generate_detailed_feedback(user_pitch, ref_pitch, hop, sr, threshold=feedback_threshold)
        formatted_feedback = format_feedback_for_display(detailed_feedback)
        stats = get_summary_statistics(detailed_feedback)
    
    # Display results in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary", "🎵 Detailed Analysis", "📈 Pitch Visualization", "🎧 Audio Comparison"])
    
    with tab1:
        st.subheader("📊 Analysis Summary")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Differences", stats['total_differences'])
        
        with col2:
            st.metric("Average Deviation", f"{stats['average_deviation_hz']:.1f} Hz")
        
        with col3:
            st.metric("Max Deviation", f"{stats['max_deviation_hz']:.1f} Hz")
        
        with col4:
            st.metric("Accuracy", f"{stats['accuracy_percentage']:.1f}%")
        
        # Performance assessment
        st.subheader("🎯 Performance Assessment")
        
        if stats['total_differences'] == 0:
            st.success("🎉 EXCELLENT! No significant pitch differences detected.")
            st.write("Your performance matches the reference very well!")
        else:
            # Most common issue
            st.warning(f"⚠️ Most common issue: {stats['most_common_issue']}")
            
            # Recommendations
            st.subheader("💡 Recommendations")
            if stats['high_pitch_count'] > stats['low_pitch_count']:
                st.write("• Focus on singing slightly lower")
            else:
                st.write("• Focus on singing slightly higher")
            st.write("• Practice the specific timestamps mentioned in the detailed analysis")
            st.write("• Use the aligned audio files for practice")
        
        # Pitch distribution
        if detailed_feedback:
            st.subheader("📈 Pitch Distribution")
            freq_diffs = [item['freq_diff'] for item in detailed_feedback]
            
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.hist(freq_diffs, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Perfect Pitch')
            ax.set_xlabel('Pitch Difference (Hz)')
            ax.set_ylabel('Frequency')
            ax.set_title('Distribution of Pitch Differences')
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
    
    with tab2:
        st.subheader("🎵 Detailed Timestamped Analysis")
        
        if detailed_feedback:
            # Create a DataFrame for better display
            df_data = []
            for item in detailed_feedback:
                df_data.append({
                    'Timestamp (s)': f"{item['timestamp']:.2f}",
                    'User Note': item['user_note'],
                    'Reference Note': item['ref_note'],
                    'Frequency Diff (Hz)': f"{item['freq_diff']:.1f}",
                    'Cents Diff': f"{item['cents_diff']:.0f}",
                    'Direction': "↑ Higher" if item['freq_diff'] > 0 else "↓ Lower"
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Detailed feedback list
            st.subheader("📝 Detailed Feedback")
            for item in formatted_feedback:
                st.write(f"**{item['display_text']}**")
        else:
            st.success("🎉 No significant pitch differences detected!")
    
    with tab3:
        st.subheader("📈 Pitch Contour Visualization")
        
        # Create pitch contour plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Convert frame indices to time
        time_axis = np.arange(len(user_pitch)) * hop / sr
        
        # Plot pitch contours
        ax.plot(time_axis, user_pitch, label='Your Recording', color='blue', alpha=0.7, linewidth=2)
        ax.plot(time_axis, ref_pitch, label='Reference', color='red', alpha=0.7, linewidth=2)
        
        # Highlight differences
        if detailed_feedback:
            diff_times = [item['timestamp'] for item in detailed_feedback]
            diff_user_pitches = [user_pitch[int(t * sr / hop)] for t in diff_times if int(t * sr / hop) < len(user_pitch)]
            diff_ref_pitches = [ref_pitch[int(t * sr / hop)] for t in diff_times if int(t * sr / hop) < len(ref_pitch)]
            
            ax.scatter(diff_times[:len(diff_user_pitches)], diff_user_pitches, 
                      color='orange', s=50, alpha=0.8, label='Pitch Differences', zorder=5)
        
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Pitch (Hz)')
        ax.set_title('Pitch Contour Comparison')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(bottom=0)
        
        st.pyplot(fig)
        
        # Pitch difference plot
        if detailed_feedback:
            st.subheader("📊 Pitch Differences Over Time")
            
            fig2, ax2 = plt.subplots(figsize=(12, 4))
            
            # Calculate pitch differences for all frames
            min_len = min(len(user_pitch), len(ref_pitch))
            all_diffs = user_pitch[:min_len] - ref_pitch[:min_len]
            all_times = np.arange(min_len) * hop / sr
            
            ax2.plot(all_times, all_diffs, color='purple', alpha=0.7, linewidth=1)
            ax2.axhline(y=0, color='red', linestyle='--', alpha=0.5, label='Perfect Match')
            ax2.fill_between(all_times, all_diffs, 0, where=(all_diffs > 0).tolist(), 
                           alpha=0.3, color='green', label='Higher than Reference')
            ax2.fill_between(all_times, all_diffs, 0, where=(all_diffs < 0).tolist(), 
                           alpha=0.3, color='orange', label='Lower than Reference')
            
            ax2.set_xlabel('Time (seconds)')
            ax2.set_ylabel('Pitch Difference (Hz)')
            ax2.set_title('Pitch Differences Over Time')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            st.pyplot(fig2)
    
    with tab4:
        st.subheader("🎧 Audio Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Your Recording (Aligned)**")
            st.audio('user_aligned.wav', format='audio/wav')
        
        with col2:
            st.write("**Reference Audio (Aligned)**")
            st.audio('reference_aligned.wav', format='audio/wav')
        
        # Segment comparison
        if detailed_feedback:
            st.subheader("🎵 Problematic Segments")
            st.write("Listen to specific segments where pitch differences were detected:")
            
            # Show first few problematic segments
            for i, item in enumerate(detailed_feedback[:5]):
                with st.expander(f"Segment {i+1}: {item['message']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Your segment:**")
                        # Extract segment (1 second)
                        start_time = max(0, item['timestamp'] - 0.5)
                        end_time = min(len(user_y) / user_sr, item['timestamp'] + 0.5)
                        
                        # Save segment
                        seg_file = f"temp_seg_{i}.wav"
                        user_seg = user_y[int(start_time * user_sr):int(end_time * user_sr)]
                        save_audio(user_seg, user_sr, seg_file)
                        st.audio(seg_file, format='audio/wav')
                    
                    with col2:
                        st.write("**Reference segment:**")
                        ref_seg = aligned_ref_y[int(start_time * ref_sr):int(end_time * ref_sr)]
                        ref_seg_file = f"temp_ref_seg_{i}.wav"
                        save_audio(ref_seg, ref_sr, ref_seg_file)
                        st.audio(ref_seg_file, format='audio/wav')
                    
                    # Clean up temporary files
                    if os.path.exists(seg_file):
                        os.remove(seg_file)
                    if os.path.exists(ref_seg_file):
                        os.remove(ref_seg_file)
    
    # Download section
    st.header("📁 Download Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with open('user_aligned.wav', 'rb') as f:
            st.download_button(
                label="Download Your Aligned Audio",
                data=f.read(),
                file_name="user_aligned.wav",
                mime="audio/wav"
            )
    
    with col2:
        with open('reference_aligned.wav', 'rb') as f:
            st.download_button(
                label="Download Reference Aligned Audio",
                data=f.read(),
                file_name="reference_aligned.wav",
                mime="audio/wav"
            )
    
    with col3:
        # Create analysis report
        report = f"""QIRAT AI Analysis Report

Summary:
- Total pitch differences: {stats['total_differences']}
- Average deviation: {stats['average_deviation_hz']:.1f} Hz
- Maximum deviation: {stats['max_deviation_hz']:.1f} Hz
- Accuracy: {stats['accuracy_percentage']:.1f}%

Detailed Feedback:
"""
        for item in detailed_feedback:
            report += f"- {item['message']}\n"
        
        st.download_button(
            label="Download Analysis Report",
            data=report,
            file_name="qirat_analysis_report.txt",
            mime="text/plain"
        )

else:
    if not ref_file_path:
        st.info("👆 Please provide a reference audio file (upload, download from URL, or YouTube link) to begin analysis.")
    elif user_audio is None or len(user_audio) == 0:
        st.info("👆 Please provide your audio recording to begin analysis.") 