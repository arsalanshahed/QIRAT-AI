#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Frontend with Arabic ASR Integration
Combines pitch analysis with Arabic speech recognition and Tajweed analysis
"""

import streamlit as st
import os
import soundfile as sf
import uuid
import numpy as np
import json
import tempfile
from analyze_pitch import align_by_first_word, extract_pitch_contour, save_audio, generate_detailed_feedback, analyze_pitch_differences
from feedback import format_feedback_for_display, get_summary_statistics
from arabic_asr import ArabicASR
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av
import matplotlib.pyplot as plt
import pandas as pd
import requests
from urllib.parse import urlparse
import yt_dlp
import re
from tajweed_rules import tajweed_feedback
from quran_integration import fetch_surah_list, fetch_surah_ayah_count, get_verse_text, fetch_ayah_translation
from auth_system import AuthSystem, show_login_page, show_register_page
import streamlit_lottie as st_lottie
from memorization_aid import spaced_repetition_schedule, check_memorization, get_due_ayahs, record_review, get_streak
from pronunciation_assist import play_correct_recitation, compare_user_and_correct
from realtime_feedback import stream_asr_and_tajweed
from personalization import recommend_next_practice, get_achievements, get_streak, get_progress_analytics
from community import share_progress, get_leaderboard, get_community_feed
import librosa
import sounddevice as sd
import time

# Page configuration
st.set_page_config(
    page_title="QIRAT AI: Enhanced Arabic Learning Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better Arabic text display
st.markdown("""
<style>
body, .stApp {
    background: linear-gradient(120deg, #181c24 0%, #232a36 100%) !important;
    font-family: 'Segoe UI', 'Noto Naskh Arabic', 'Amiri', sans-serif;
    color: #f5f7fa !important;
}

h1, h2, h3, .stTitle, .stHeader {
    font-weight: 700;
    letter-spacing: 0.01em;
    color: #e3e9f3;
    margin-bottom: 0.5em;
}

.card {
    background: #232a36;
    border-radius: 16px;
    box-shadow: 0 2px 16px 0 rgba(20,24,32,0.18);
    padding: 1.5em 1.5em 1em 1.5em;
    margin-bottom: 1.5em;
    transition: box-shadow 0.3s cubic-bezier(.4,0,.2,1), transform 0.3s cubic-bezier(.4,0,.2,1);
    animation: fadeIn 0.7s;
    color: #f5f7fa;
}
.card:hover {
    box-shadow: 0 8px 32px 0 rgba(20,24,32,0.32);
    transform: translateY(-2px) scale(1.01);
}

.fade-in {
    animation: fadeIn 1.2s;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: none; }
}

.metric-animated {
    transition: color 0.5s, background 0.5s;
}
.metric-animated[data-good="true"] {
    color: #7fffd4;
    background: #1b2a2f;
}
.metric-animated[data-bad="true"] {
    color: #ff8a65;
    background: #2d1a1a;
}

.stButton>button {
    border-radius: 8px;
    font-weight: 600;
    transition: background 0.3s, color 0.3s;
    background: #232a36 !important;
    color: #f5f7fa !important;
    border: 1.5px solid #3a4250;
}
.stButton>button:hover {
    background: #7c4dff !important;
    color: #fff !important;
}

.stTextInput>div>input, .stTextArea>div>textarea {
    border-radius: 8px;
    border: 1.5px solid #3a4250;
    background: #232a36;
    color: #f5f7fa;
    transition: border 0.3s;
}
.stTextInput>div>input:focus, .stTextArea>div>textarea:focus {
    border: 1.5px solid #7c4dff;
}

.arabic-text {
    font-family: 'Amiri', 'Noto Naskh Arabic', serif;
    font-size: 1.2em;
    direction: rtl;
    text-align: right;
    line-height: 1.8;
    letter-spacing: 0.01em;
    background: linear-gradient(90deg, #232a36 0%, #181c24 100%);
    border-radius: 8px;
    padding: 0.5em 1em;
    margin-bottom: 0.5em;
    animation: fadeIn 1.2s;
    color: #f5f7fa;
}

.analysis-card {
    background-color: #232a36;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    border-left: 4px solid #7c4dff;
    animation: fadeIn 1.2s;
    color: #f5f7fa;
}

.error-card {
    background-color: #2d1a1a;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    border-left: 4px solid #ff8a65;
    animation: fadeIn 1.2s;
    color: #ffb4a2;
}

.success-card {
    background-color: #1b2a2f;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    border-left: 4px solid #7fffd4;
    animation: fadeIn 1.2s;
    color: #7fffd4;
}

.stAlert {
    animation: fadeIn 1.2s;
    color: #f5f7fa;
}

::-webkit-scrollbar {
    width: 8px;
    background: #232a36;
}
::-webkit-scrollbar-thumb {
    background: #3a4250;
    border-radius: 8px;
}

@media (max-width: 600px) {
  .card, .analysis-card, .error-card, .success-card, .arabic-text {
    font-size: 1em !important;
    padding: 0.7em 0.5em !important;
    margin-bottom: 0.5em !important;
  }
  h1, h2, h3, .stTitle, .stHeader {
    font-size: 1.2em !important;
  }
  .stButton>button {
    font-size: 1em !important;
    padding: 0.5em 1em !important;
  }
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'asr_model' not in st.session_state:
    st.session_state.asr_model = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

# --- Authentication and Demo Mode ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None
if 'demo_mode' not in st.session_state:
    st.session_state['demo_mode'] = False

def show_auth_or_demo():
    st.title('🕌 QIRAT AI: Login or Demo Mode')
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Login / Register'):
            st.session_state['show_login'] = True
    with col2:
        if st.button('Continue as Guest (Demo Mode)'):
            st.session_state['demo_mode'] = True
            st.session_state['authenticated'] = True
            st.session_state['user_data'] = {'username': 'Demo User', 'user_id': 'demo'}
            st.success('Demo Mode Activated!')

if not st.session_state['authenticated']:
    show_auth_or_demo()
    if st.session_state.get('show_login', False):
        show_login_page()
    st.stop()

# --- Demo Mode Banner ---
if st.session_state.get('demo_mode', False):
    st.markdown("""
    <div style='background-color:#ffe082;padding:10px;border-radius:5px;margin-bottom:10px;text-align:center;'>
        <b>Demo Mode:</b> Your progress will not be saved after you close this session.
    </div>
    """, unsafe_allow_html=True)

# Title and description
st.title('🕌 QIRAT AI: Enhanced Arabic Learning Platform')
st.markdown("""
<div class="arabic-text">
مرحباً بكم في منصة تعلم القرآن الكريم الذكية
</div>
""", unsafe_allow_html=True)
st.write('Advanced Arabic speech recognition, pitch analysis, and Tajweed correction system.')

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # ASR Model Settings
    st.subheader("🎤 Speech Recognition")
    model_size = st.selectbox(
        "Whisper Model Size",
        ["tiny", "base", "small", "medium", "large"],
        index=1,
        help="Larger models are more accurate but slower"
    )
    
    # Analysis Settings
    st.subheader("📊 Analysis Settings")
    feedback_threshold = st.slider("Feedback Threshold (Hz)", 10, 100, 50, help="Lower values = more sensitive feedback")
    show_notes = st.checkbox("Show Musical Notes", True, help="Display musical note names (C4, A4, etc.)")
    show_cents = st.checkbox("Show Cents", True, help="Display pitch differences in cents")
    
    # ASR Settings
    st.subheader("🔤 ASR Settings")
    enable_asr = st.checkbox("Enable Arabic ASR", True, help="Enable speech recognition for Arabic text")
    enable_pronunciation = st.checkbox("Enable Pronunciation Detection", True, help="Detect pronunciation errors")
    enable_tajweed = st.checkbox("Enable Tajweed Analysis", True, help="Analyze Tajweed rules")

    # Quran Verse Selection
    st.subheader("📖 Quran Verse Selection")
    surah_list = fetch_surah_list()
    surah_names = [f"{s['id']}: {s['name_simple']}" for s in surah_list]
    surah_ids = [s['id'] for s in surah_list]
    surah_idx = st.selectbox("Select Surah", options=range(len(surah_names)), format_func=lambda i: surah_names[i])
    selected_surah = surah_ids[surah_idx] if surah_list else 1
    ayah_count = fetch_surah_ayah_count(selected_surah)
    ayah_number = st.selectbox("Select Ayah", options=list(range(1, ayah_count+1)))
    if st.button("Fetch Verse Text"):
        verse_text = get_verse_text(selected_surah, ayah_number)
        translation = fetch_ayah_translation(selected_surah, ayah_number)
        if verse_text:
            st.session_state["reference_text"] = verse_text
            st.session_state["reference_translation"] = translation
            st.success(f"Verse: {verse_text}")
        else:
            st.error("Verse not found.")

# Initialize ASR model
@st.cache_resource
def load_asr_model(model_size):
    """Load ASR model with caching"""
    try:
        asr = ArabicASR(model_size=model_size)
        return asr
    except Exception as e:
        st.error(f"Failed to load ASR model: {e}")
        return None

if enable_asr:
    with st.spinner("Loading Arabic ASR model..."):
        st.session_state.asr_model = load_asr_model(model_size)

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
    
    reference_file = None
    
    if ref_input_method == 'Upload File':
        uploaded_ref = st.file_uploader(
            "Upload Reference Audio",
            type=['mp3', 'wav', 'm4a', 'ogg'],
            help="Upload reference audio file"
        )
        if uploaded_ref:
            # Save uploaded file
            ref_filename = f"uploaded_ref_{uuid.uuid4().hex[:8]}.wav"
            with open(ref_filename, "wb") as f:
                f.write(uploaded_ref.getbuffer())
            reference_file = ref_filename
            st.success(f"✅ Reference audio uploaded: {uploaded_ref.name}")
    
    elif ref_input_method == 'Download from URL':
        ref_url = st.text_input("Enter Audio URL", help="Direct link to audio file")
        if ref_url:
            if st.button("Download Reference Audio"):
                with st.spinner("Downloading reference audio..."):
                    # Download logic (simplified)
                    st.info("Download functionality would be implemented here")
    
    elif ref_input_method == 'YouTube Link':
        ref_youtube_url = st.text_input("Enter YouTube URL", help="YouTube video URL")
        if ref_youtube_url:
            if st.button("Download from YouTube"):
                with st.spinner("Downloading from YouTube..."):
                    # YouTube download logic (simplified)
                    st.info("YouTube download functionality would be implemented here")
    
    # Reference text input (for ASR comparison)
    if enable_asr:
        st.subheader("📝 Reference Text (Optional)")
        reference_text = st.text_area(
            "Enter Reference Arabic Text",
            value=st.session_state.get("reference_text", "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"),
            help="Enter the Arabic text that should match the audio for ASR comparison"
        )
        reference_translation = st.session_state.get("reference_translation", "")
        if reference_translation:
            st.markdown(f"<div style='color: #444; font-size: 1em; margin-bottom: 1em;'><b>Translation:</b> {reference_translation}</div>", unsafe_allow_html=True)

with col2:
    st.subheader("🎤 User Recording")
    
    # Recording options
    recording_method = st.radio(
        'Recording Method',
        ['Record Audio', 'Upload Audio'],
        help="Choose how to provide your audio"
    )
    
    user_file = None
    
    if recording_method == 'Record Audio':
        # WebRTC audio recording
        st.write("Click 'Start' to begin recording, then 'Stop' when finished.")
        
        def audio_frame_callback(frame):
            # Process audio frame
            return frame
        
        webrtc_ctx = webrtc_streamer(
            key="speech-to-text",
            mode=WebRtcMode.SENDONLY,
            audio_frame_callback=audio_frame_callback,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={"video": False, "audio": True},
        )
        
        if webrtc_ctx.state.playing:
            st.success("🎤 Recording in progress...")
    
    elif recording_method == 'Upload Audio':
        uploaded_user = st.file_uploader(
            "Upload Your Audio",
            type=['mp3', 'wav', 'm4a', 'ogg'],
            help="Upload your audio recording"
        )
        if uploaded_user:
            # Save uploaded file
            user_filename = f"uploaded_user_{uuid.uuid4().hex[:8]}.wav"
            with open(user_filename, "wb") as f:
                f.write(uploaded_user.getbuffer())
            user_file = user_filename
            st.success(f"✅ User audio uploaded: {uploaded_user.name}")

# Analysis section
if reference_file and user_file:
    st.header("🔍 Analysis Results")
    
    # Create tabs for different analysis types
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🎵 Pitch Analysis", "🔤 ASR Analysis", "📊 Combined Results", "📈 Progress Tracking", "🧠 Memorization Aid", "🗣️ Pronunciation Assist", "🌍 Community"])
    
    with tab1:
        st.subheader("🎵 Pitch Analysis")
        
        with st.spinner("Analyzing pitch contours..."):
            try:
                # Extract pitch contours
                user_pitch, sr, hop = extract_pitch_contour(user_file)
                ref_pitch, _, _ = extract_pitch_contour(reference_file)
                
                # Generate feedback
                feedback = generate_detailed_feedback(user_pitch, ref_pitch, hop, sr, feedback_threshold)
                formatted_feedback = format_feedback_for_display(feedback)
                stats = get_summary_statistics(feedback)
                
                # Display results
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Accuracy", f"{stats['accuracy_percentage']:.1f}%")
                
                with col2:
                    st.metric("Total Differences", stats['total_differences'])
                
                with col3:
                    st.metric("Average Deviation", f"{stats['average_deviation_cents']:.0f} cents")
                
                # Detailed feedback
                if feedback:
                    st.subheader("🎯 Detailed Feedback")
                    for item in formatted_feedback[:10]:  # Show first 10 items
                        st.markdown(f"<div class='analysis-card'>{item['display_text']}</div>", unsafe_allow_html=True)
                else:
                    st.success("🎉 Excellent! No significant pitch differences detected.")
                
                # Store results
                st.session_state.analysis_results['pitch'] = {
                    'feedback': feedback,
                    'stats': stats,
                    'user_pitch': user_pitch.tolist(),
                    'ref_pitch': ref_pitch.tolist()
                }
                
            except Exception as e:
                st.error(f"Pitch analysis failed: {e}")
    
    with tab2:
        if enable_asr and st.session_state.asr_model:
            st.subheader("🔤 Arabic Speech Recognition")
            
            with st.spinner("Performing Arabic ASR analysis..."):
                try:
                    asr = st.session_state.asr_model
                    
                    # Transcribe user audio
                    user_transcription = asr.transcribe_audio(user_file)
                    
                    if user_transcription["success"]:
                        st.success("✅ Transcription successful!")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("🎤 Your Transcription")
                            st.markdown(f"<div class='arabic-text'>{user_transcription['text']}</div>", unsafe_allow_html=True)
                        
                        with col2:
                            if reference_text:
                                st.subheader("📝 Reference Text")
                                st.markdown(f"<div class='arabic-text'>{reference_text}</div>", unsafe_allow_html=True)
                            if reference_translation:
                                st.markdown(f"<div style='color: #444; font-size: 1em; margin-bottom: 1em;'><b>Translation:</b> {reference_translation}</div>", unsafe_allow_html=True)
                        
                        # Pronunciation analysis
                        if enable_pronunciation and reference_text:
                            st.subheader("🎯 Pronunciation Analysis")
                            
                            pronunciation_result = asr.detect_pronunciation_errors(user_file, reference_text)
                            
                            if pronunciation_result["success"]:
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.metric("Accuracy", f"{pronunciation_result['accuracy']:.1f}%")
                                
                                with col2:
                                    st.metric("Errors Detected", pronunciation_result['total_errors'])
                                
                                if pronunciation_result['errors']:
                                    st.subheader("🚨 Pronunciation Errors")
                                    for error in pronunciation_result['errors'][:5]:
                                        st.markdown(f"<div class='error-card'>{error['message']} (at {error['start_time']:.2f}s)</div>", unsafe_allow_html=True)
                                else:
                                    st.success("✅ No pronunciation errors detected!")
                                
                                # Store results
                                st.session_state.analysis_results['asr'] = {
                                    'transcription': user_transcription,
                                    'pronunciation': pronunciation_result
                                }
                            else:
                                st.error(f"Pronunciation analysis failed: {pronunciation_result.get('error', 'Unknown error')}")
                        else:
                            # Store basic transcription
                            st.session_state.analysis_results['asr'] = {
                                'transcription': user_transcription
                            }
                        
                        # Tajweed analysis with highlighting
                        st.subheader("🕌 Tajweed Analysis")
                        feedback, highlights = tajweed_feedback(reference_text)
                        # Highlight errors in the verse
                        words = reference_text.split()
                        highlighted_verse = ""
                        for w_idx, word in enumerate(words):
                            chars = list(word)
                            for c_idx, char in enumerate(chars):
                                if (w_idx, c_idx) in highlights:
                                    chars[c_idx] = f"<span style='background-color: #ffe082; color: #d84315; font-weight: bold;'>{char}</span>"
                            highlighted_verse += " " + "".join(chars)
                        st.markdown(f"<div class='arabic-text'>{highlighted_verse.strip()}</div>", unsafe_allow_html=True)
                        for fb in feedback:
                            if fb.startswith("✅"):
                                st.success(fb)
                            else:
                                st.warning(fb)
                    else:
                        st.error(f"Transcription failed: {user_transcription.get('error', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"ASR analysis failed: {e}")
        else:
            st.info("🔤 Arabic ASR is disabled. Enable it in the sidebar to use this feature.")
    
    with tab3:
        st.subheader("📊 Combined Analysis Results")
        
        if st.session_state.analysis_results:
            # Combine pitch and ASR results
            combined_score = 0
            total_metrics = 0
            
            # Pitch score
            if 'pitch' in st.session_state.analysis_results:
                pitch_score = st.session_state.analysis_results['pitch']['stats']['accuracy_percentage']
                combined_score += pitch_score
                total_metrics += 1
                
                st.metric("🎵 Pitch Accuracy", f"{pitch_score:.1f}%")
            
            # ASR score
            if 'asr' in st.session_state.analysis_results:
                if 'pronunciation' in st.session_state.analysis_results['asr']:
                    asr_score = st.session_state.analysis_results['asr']['pronunciation']['accuracy']
                    combined_score += asr_score
                    total_metrics += 1
                    
                    st.metric("🔤 Pronunciation Accuracy", f"{asr_score:.1f}%")
            
            # Overall score
            if total_metrics > 0:
                overall_score = combined_score / total_metrics
                st.metric("🏆 Overall Score", f"{overall_score:.1f}%")
                
                # Performance level
                if overall_score >= 90:
                    level = "Excellent"
                    color = "green"
                elif overall_score >= 80:
                    level = "Good"
                    color = "blue"
                elif overall_score >= 70:
                    level = "Fair"
                    color = "orange"
                else:
                    level = "Needs Improvement"
                    color = "red"
                
                st.markdown(f"<div class='success-card'><strong>Performance Level:</strong> {level}</div>", unsafe_allow_html=True)
            
            # Recommendations
            st.subheader("💡 Recommendations")
            recommendations = []
            
            if 'pitch' in st.session_state.analysis_results:
                pitch_stats = st.session_state.analysis_results['pitch']['stats']
                if pitch_stats['high_pitch_count'] > pitch_stats['low_pitch_count']:
                    recommendations.append("🎵 Focus on singing slightly lower")
                else:
                    recommendations.append("🎵 Focus on singing slightly higher")
            
            if 'asr' in st.session_state.analysis_results:
                if 'pronunciation' in st.session_state.analysis_results['asr']:
                    if st.session_state.analysis_results['asr']['pronunciation']['total_errors'] > 0:
                        recommendations.append("🔤 Practice pronunciation of difficult words")
            
            if recommendations:
                for rec in recommendations:
                    st.markdown(f"<div class='analysis-card'>{rec}</div>", unsafe_allow_html=True)
            else:
                st.success("🎉 Excellent performance! Keep up the great work!")
    
    with tab4:
        st.subheader("📈 Progress Tracking & Analytics")
        if st.session_state.get('demo_mode', False):
            st.info('You are in Demo Mode. Progress is only saved for this session.')
            demo_results = st.session_state.get('demo_results', [])
            if demo_results:
                df = pd.DataFrame(demo_results)
                st.dataframe(df)
                # Weekly/Monthly analytics
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                    df['Week'] = df['Date'].dt.isocalendar().week
                    df['Month'] = df['Date'].dt.month
                    st.line_chart(df.groupby('Week')['ASR Accuracy'].mean(), use_container_width=True)
                    st.line_chart(df.groupby('Month')['ASR Accuracy'].mean(), use_container_width=True)
                # Best/Worst verses
                if not df.empty:
                    best = df.loc[df['ASR Accuracy'].idxmax()]
                    worst = df.loc[df['ASR Accuracy'].idxmin()]
                    st.success(f"🏆 Best Verse: Surah {best['Surah']} Ayah {best['Ayah']} ({best['ASR Accuracy']}%)")
                    st.error(f"⚠️ Most Challenging: Surah {worst['Surah']} Ayah {worst['Ayah']} ({worst['ASR Accuracy']}%)")
            else:
                st.write('No demo results yet. Complete an analysis to see progress.')
        else:
            # Authenticated user: fetch from database
            auth_system = AuthSystem()
            user_id = st.session_state['user_data']['user_id']
            success, analyses = auth_system.get_user_analyses(user_id, limit=50)
            if success and analyses:
                df = pd.DataFrame([
                    json.loads(a) if isinstance(a, str) else a for a in analyses
                ])
                df = pd.DataFrame([
                    {
                        'Date': entry.get('analysis_date', ''),
                        'Surah': entry.get('reference_file', ''),
                        'Ayah': entry.get('user_file', ''),
                        'ASR Accuracy': json.loads(entry.get('summary_stats', '{}')).get('accuracy_percentage', 0),
                        'Tajweed Errors': len(json.loads(entry.get('segments_data', '[]')))
                    } for entry in df.to_dict(orient='records')
                ])
                st.dataframe(df)
                # Weekly/Monthly analytics
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                    df['Week'] = df['Date'].dt.isocalendar().week
                    df['Month'] = df['Date'].dt.month
                    st.line_chart(df.groupby('Week')['ASR Accuracy'].mean(), use_container_width=True)
                    st.line_chart(df.groupby('Month')['ASR Accuracy'].mean(), use_container_width=True)
                # Best/Worst verses
                if not df.empty:
                    best = df.loc[df['ASR Accuracy'].idxmax()]
                    worst = df.loc[df['ASR Accuracy'].idxmin()]
                    st.success(f"🏆 Best Verse: Surah {best['Surah']} Ayah {best['Ayah']} ({best['ASR Accuracy']}%)")
                    st.error(f"⚠️ Most Challenging: Surah {worst['Surah']} Ayah {worst['Ayah']} ({worst['ASR Accuracy']}%)")
            else:
                st.write('No progress data found. Complete an analysis to see progress.')

    with tab5:
        st.subheader("🧠 Memorization Aid (Hifz)")
        if st.session_state['authenticated']:
            user_id = st.session_state['user_data']['user_id']
            due_ayahs = get_due_ayahs(user_id)
            streak = get_streak(user_id)
            st.markdown(f"**Current Streak:** {streak} days")
            if due_ayahs:
                for surah, ayah, next_review, status in due_ayahs:
                    st.markdown(f"- Surah {surah}, Ayah {ayah} | Next Review: {next_review or 'Now'} | Status: {status}")
                    user_input = st.text_area(f"Type Ayah {ayah} from Surah {surah} from memory:", key=f"mem_input_{surah}_{ayah}")
                    quality = st.slider(f"How well did you recall this ayah? (1=Forgot, 5=Perfect)", 1, 5, 3, key=f"mem_quality_{surah}_{ayah}")
                    if st.button(f"Check & Record Review for Surah {surah} Ayah {ayah}", key=f"mem_btn_{surah}_{ayah}"):
                        feedback = check_memorization(user_input, st.session_state.get("reference_text", ""))
                        st.metric("Score", f"{feedback['score']}%")
                        if feedback['missing_words']:
                            st.warning(f"Missing words: {', '.join(feedback['missing_words'])}")
                        st.info(feedback['suggestion'])
                        result = record_review(user_id, surah, ayah, quality)
                        st.success(f"Review recorded! Next review in {result['interval']} days. Streak: {result['streak']} | Status: {result['status']}")
                        st.experimental_rerun()
            else:
                st.success("No ayahs due for review today! Keep up the great work.")
        else:
            st.info("Login to access personalized memorization tracking.")

    with tab6:
        st.subheader("🗣️ Pronunciation Assistance")
        st.markdown("Listen to the correct recitation and compare with your own.")
        qari = st.selectbox("Select Qari/Qirat", ["Mishary Alafasy (Hafs)", "Abdul Basit (Murattal)", "Minshawi", "Warsh"], index=0, key="qari_select")
        ref_audio_path = None
        if st.button("Play Correct Recitation"):
            ref_audio_path = play_correct_recitation(selected_surah, ayah_number, qari)
            st.success("Reference recitation played.")
        if reference_file and user_file:
            st.markdown("**Visual/Audio Comparison:**")
            # Play user audio
            if st.button("Play Your Audio"):
                data, sr = sf.read(user_file)
                sd.play(data, sr)
                sd.wait()
            # Play reference audio (if generated)
            if st.button("Play Reference Audio"):
                if ref_audio_path:
                    data, sr = sf.read(ref_audio_path)
                else:
                    data, sr = sf.read(reference_file)
                sd.play(data, sr)
                sd.wait()
            # Show waveforms
            user_y, user_sr = librosa.load(user_file, sr=None)
            ref_y, ref_sr = librosa.load(reference_file, sr=None)
            fig, ax = plt.subplots(figsize=(10, 3))
            ax.plot(librosa.times_like(user_y), user_y, label='User', alpha=0.7)
            ax.plot(librosa.times_like(ref_y), ref_y, label='Reference', alpha=0.7)
            ax.set_title('Waveform Comparison')
            ax.legend()
            st.pyplot(fig)
            # Show error highlights
            mismatches = compare_user_and_correct(user_file, reference_file)
            if mismatches:
                st.warning(f"Pronunciation mismatches detected at: {[round(m['timestamp'],2) for m in mismatches]} seconds.")
                fig2, ax2 = plt.subplots(figsize=(10, 1))
                ax2.plot(librosa.times_like(user_y), user_y, color='gray', alpha=0.5)
                for m in mismatches:
                    ax2.axvline(m['timestamp'], color='red', linestyle='--', alpha=0.7)
                ax2.set_title('Mismatch Timestamps')
                st.pyplot(fig2)
            else:
                st.success("No major pronunciation mismatches detected!")

    with tab7:
        st.subheader("🌍 Community Feed & Leaderboard")
        # Leaderboard
        st.markdown("**Top Users**")
        leaderboard = get_leaderboard()
        for entry in leaderboard:
            st.markdown(f"**{entry['username']}**: {entry['score']}% accuracy | 🔥 Streak: {entry['streak']}")
        st.markdown("---")
        # Share progress
        if st.session_state['authenticated']:
            user_id = st.session_state['user_data']['user_id']
            username = st.session_state['user_data']['username']
            st.subheader("Share Your Progress")
            message = st.text_input("Message (optional)", key="community_message")
            achievement = st.selectbox("Achievement to share", ["Best Score", "Streak", "Tajweed Master", "7-Day Streak", "Other"])
            if st.button("Share to Community"):
                share_progress(user_id, username, message, achievement)
                st.success("Progress shared with the community!")
                st.experimental_rerun()
        # Community feed
        st.subheader("Recent Community Posts")
        feed = get_community_feed()
        for post in feed:
            st.markdown(f"<b>{post['username']}</b> ({post['date'][:16]})<br>🏅 <i>{post['achievement']}</i><br>{post['message']}", unsafe_allow_html=True)
            st.markdown("---")

# --- Real-Time Feedback (optional, for future expansion) ---
with st.expander("🔴 Real-Time Feedback (Beta)"):
    st.markdown("Get live word-by-word feedback as you recite.")
    audio_file = st.file_uploader("Upload your recitation for real-time feedback (WAV format, 16kHz recommended)", type=["wav"])
    if st.button("Start Real-Time Feedback"):
        reference_text = st.session_state.get("reference_text", "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ")
        st.info("Streaming feedback...")
        feedback_placeholder = st.empty()
        transcript = ""
        if audio_file:
            with open("temp_realtime.wav", "wb") as f:
                f.write(audio_file.read())
            for feedback in stream_asr_and_tajweed("temp_realtime.wav", reference_text):
                word = feedback['word']
                if feedback.get('correct', True):
                    transcript += f"<span style='color: #7fffd4; font-weight: bold;'>{word}</span> "
                else:
                    color = '#ff8a65' if feedback.get('error') == 'Pronunciation' else '#ffe082'
                    transcript += f"<span style='color: {color}; font-weight: bold;'>{word}</span> "
                feedback_placeholder.markdown(transcript, unsafe_allow_html=True)
                import time
                time.sleep(0.1)
        else:
            for feedback in stream_asr_and_tajweed(None, reference_text):
                word = feedback['word']
                if feedback.get('correct', True):
                    transcript += f"<span style='color: #7fffd4; font-weight: bold;'>{word}</span> "
                else:
                    color = '#ff8a65' if feedback.get('error') == 'Pronunciation' else '#ffe082'
                    transcript += f"<span style='color: {color}; font-weight: bold;'>{word}</span> "
                feedback_placeholder.markdown(transcript, unsafe_allow_html=True)
                import time
                time.sleep(0.1)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🕌 QIRAT AI - Advanced Arabic Learning Platform</p>
    <p>Powered by OpenAI Whisper, Librosa, and Streamlit</p>
</div>
""", unsafe_allow_html=True)

# --- Store Results After Analysis ---
def store_analysis_result(surah, ayah, asr_accuracy, tajweed_errors):
    if st.session_state.get('demo_mode', False):
        demo_results = st.session_state.get('demo_results', [])
        demo_results.append({
            'Surah': surah,
            'Ayah': ayah,
            'ASR Accuracy': asr_accuracy,
            'Tajweed Errors': tajweed_errors
        })
        st.session_state['demo_results'] = demo_results
    else:
        auth_system = AuthSystem()
        user_id = st.session_state['user_data']['user_id']
        # Save to DB (implement as needed)
        # auth_system.save_analysis_data(user_id, surah, ayah, ...)

# --- After each analysis, call store_analysis_result ---
# Example usage after analysis:
# store_analysis_result(selected_surah, ayah_number, stats['accuracy_percentage'], len(highlights))

# --- Lottie animation loader ---
def load_lottieurl(url):
    import requests
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Lottie animations
confetti_lottie = load_lottieurl('https://assets2.lottiefiles.com/packages/lf20_jbrw3hcz.json')
well_done_lottie = load_lottieurl('https://assets2.lottiefiles.com/packages/lf20_0yfsb3a1.json')
encourage_lottie = load_lottieurl('https://assets2.lottiefiles.com/packages/lf20_2glqweqs.json')
error_lottie = load_lottieurl('https://assets2.lottiefiles.com/packages/lf20_2ks3pjua.json')
onboard_lottie = load_lottieurl('https://assets2.lottiefiles.com/packages/lf20_1pxqjqps.json')

# --- Onboarding animation on first visit ---
if 'onboarded' not in st.session_state:
    if onboard_lottie is not None:
        st_lottie.st_lottie(onboard_lottie, height=180, key="onboard")
    st.session_state['onboarded'] = True
    st.info('Welcome to QIRAT AI! Select a verse and upload or record your recitation to begin.')

# --- After analysis, show Lottie animations for milestones ---
if 'analysis_results' in st.session_state:
    pitch_stats = st.session_state.analysis_results.get('pitch', {}).get('stats', {})
    asr_stats = st.session_state.analysis_results.get('asr', {}).get('pronunciation', {})
    asr_accuracy = pitch_stats.get('accuracy_percentage', 0)
    tajweed_errors = 0
    if 'tajweed' in st.session_state.analysis_results:
        tajweed_errors = st.session_state.analysis_results['tajweed'].get('errors', 0)
    with st.container():
        if (asr_accuracy >= 90 or tajweed_errors == 0) and confetti_lottie is not None:
            st_lottie.st_lottie(confetti_lottie, height=180, key="confetti", speed=1, loop=False)
            st.success('🎉 Amazing! You achieved a milestone!')
        elif asr_accuracy >= 75 and encourage_lottie is not None:
            st_lottie.st_lottie(encourage_lottie, height=120, key="encourage", speed=1)
            st.info('Great progress! Keep going!')
        elif asr_accuracy < 60 and error_lottie is not None:
            st_lottie.st_lottie(error_lottie, height=120, key="error", speed=1)
            st.warning('Don\'t give up! Practice makes perfect.')

# --- Confetti animation for new achievements ---
if 'analysis_results' in st.session_state and st.session_state['authenticated']:
    user_id = st.session_state['user_data']['user_id']
    badges = get_achievements(user_id)
    if 'Tajweed Master' in badges and confetti_lottie is not None:
        st_lottie.st_lottie(confetti_lottie, height=180, key="confetti_achieve", speed=1, loop=False)
        st.success('🎉 Achievement unlocked: Tajweed Master!')
    if '7-Day Streak' in badges and confetti_lottie is not None:
        st_lottie.st_lottie(confetti_lottie, height=180, key="confetti_streak", speed=1, loop=False)
        st.success('🎉 Achievement unlocked: 7-Day Streak!')

# --- Feedback/Help Sidebar ---
with st.sidebar:
    st.markdown('---')
    st.header('💡 Help & Feedback')
    st.info('Hover over any button or input for tips!')
    st.markdown('''
    <ul style='font-size:1em;'>
      <li>Use the <b>Quran Verse Selection</b> to pick any verse.</li>
      <li>Upload or record your recitation for instant feedback.</li>
      <li>See Tajweed errors highlighted in the verse.</li>
      <li>Progress is tracked per user or in demo mode.</li>
    </ul>
    ''', unsafe_allow_html=True)
    st.markdown('---')
    st.subheader('Send us your feedback:')
    feedback_text = st.text_area('Your feedback', help='Share your thoughts, suggestions, or issues.')
    if st.button('Submit Feedback'):
        st.success('Thank you for your feedback!')

# --- Add advanced features to sidebar ---
with st.sidebar:
    st.header("🌟 Advanced Features")
    if st.session_state['authenticated']:
        user_id = st.session_state['user_data']['user_id']
        st.subheader("🎯 Personalized Suggestions")
        rec = recommend_next_practice(user_id)
        st.info(rec['suggestion'])
        st.subheader("🏅 Achievements")
        badges = get_achievements(user_id)
        for badge in badges:
            st.markdown(f"- 🏆 **{badge}**")
        streak = get_streak(user_id)
        st.subheader("🔥 Current Streak")
        st.markdown(f"**{streak} days**")
        st.progress(min(streak/7, 1.0))
        st.subheader("📈 Progress Analytics")
        dates, scores = get_progress_analytics(user_id)
        if dates and scores:
            fig, ax = plt.subplots(figsize=(3,2))
            ax.plot(dates, scores, marker='o', linewidth=2, markersize=4)
            ax.set_xlabel('Date')
            ax.set_ylabel('Accuracy (%)')
            ax.set_title('Progress')
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
        st.subheader("🌍 Community Leaderboard")
        leaderboard = get_leaderboard()
        for entry in leaderboard:
            st.markdown(f"**{entry['username']}**: {entry['score']}% accuracy") 