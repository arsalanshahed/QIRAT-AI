# -*- coding: utf-8 -*-
"""
QIRAT AI Frontend - Simplified Version
Comprehensive QIRAT learning platform with speech recognition and Tajweed analysis
"""

import streamlit as st
import os
import soundfile as sf
import uuid
import numpy as np
import json
import requests
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av
import matplotlib.pyplot as plt
from enhanced_pitch_analysis import (
    analyze_5second_segments, generate_segment_feedback, 
    create_segment_visualization, save_audio
)
from auth_system import (
    AuthSystem, show_login_page, show_register_page, 
    show_forgot_password_page, show_reset_password_page, logout
)

# Try to import Quran speech recognition
try:
    from quran_speech_recognition import QuranSpeechRecognition
    QURAN_ASR_AVAILABLE = True
except ImportError:
    QURAN_ASR_AVAILABLE = False
    st.warning("QIRAT Speech Recognition not available. Install: pip install openai-whisper arabic-reshaper python-bidi")

# Page configuration
st.set_page_config(
    page_title="QIRAT AI: Complete Learning Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None
if 'show_register' not in st.session_state:
    st.session_state['show_register'] = False
if 'show_forgot_password' not in st.session_state:
    st.session_state['show_forgot_password'] = False

def get_qirat_surahs():
    """Get list of Quran surahs"""
    try:
        response = requests.get("https://api.quran.com/api/v4/chapters")
        if response.status_code == 200:
            data = response.json()
            return {f"{chapter['id']}. {chapter['name_arabic']} - {chapter['name_simple']}": chapter['id'] 
                   for chapter in data['chapters']}
    except:
        pass
    
    # Fallback to common surahs
    return {
        "1. الفاتحة - Al-Fatiha": 1,
        "2. البقرة - Al-Baqarah": 2,
        "3. آل عمران - Aal-Imran": 3,
        "36. يس - Ya-Sin": 36,
        "55. الرحمن - Ar-Rahman": 55,
        "67. الملك - Al-Mulk": 67,
        "112. الإخلاص - Al-Ikhlas": 112,
        "113. الفلق - Al-Falaq": 113,
        "114. الناس - An-Nas": 114
    }

def get_surah_verses(surah_id):
    """Get verses for a specific surah"""
    try:
        response = requests.get(f"https://api.quran.com/api/v4/verses/by_chapter/{surah_id}")
        if response.status_code == 200:
            data = response.json()
            return {f"Verse {verse['verse_number']}": verse['verse_number'] 
                   for verse in data['verses']}
    except:
        pass
    
    # Fallback to first few verses
    return {f"Verse {i}": i for i in range(1, min(11, 8))}

def main_app():
    """Main application after authentication"""
    st.title('QIRAT AI: Complete Learning Platform')
    st.write('Master Quran recitation with AI-powered pronunciation, Tajweed, and memorization assistance.')
    
    # User info and logout
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.write(f"Welcome, **{st.session_state['user_data']['username']}**!")
    with col2:
        st.write(f"{st.session_state['user_data']['email']}")
    with col3:
        if st.button("Logout"):
            logout()
    
    # Mode selection
    st.sidebar.header("Learning Mode")
    mode = st.sidebar.selectbox(
        "Choose your learning mode:",
        ["Pitch Analysis", "QIRAT Recitation", "Tajweed Practice", "Memorization", "Progress Tracking"],
        index=0
    )
    
    if mode == "Pitch Analysis":
        show_pitch_analysis_mode()
    elif mode == "QIRAT Recitation":
        show_qirat_recitation_mode()
    elif mode == "Tajweed Practice":
        show_tajweed_practice_mode()
    elif mode == "Memorization":
        show_memorization_mode()
    elif mode == "Progress Tracking":
        show_progress_tracking_mode()

def show_pitch_analysis_mode():
    """Show the original pitch analysis mode"""
    st.header("Pitch Analysis Mode")
    st.write("Compare your audio recording with a reference and get detailed 5-second segment analysis.")
    
    # Original pitch analysis functionality
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Reference Audio Input")
        
        # Reference input method selection
        ref_input_method = st.radio(
            'Reference Audio Source', 
            ['Upload File', 'Download from URL'], 
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
                st.success("Reference audio uploaded successfully!")

    with col2:
        st.subheader("User Audio Input")
        user_input_mode = st.radio('Input Method', ['Record', 'Upload'], help="Choose how to provide your audio")

    user_audio = None
    user_sr = 48000  # Default for webrtc
    user_wav_path = 'user_recorded.wav'

    if user_input_mode == 'Record':
        st.info("Click 'Start' to begin recording. Speak or sing clearly into your microphone.")
        
        class AudioProcessor(AudioProcessorBase):
            def __init__(self):
                self.frames = []
            def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
                pcm = frame.to_ndarray()
                self.frames.append(pcm)
                return frame
        
        audio_ctx = webrtc_streamer(
            key="audio",
            mode=WebRtcMode.SENDRECV,
            audio_receiver_size=1024,
            audio_processor_factory=AudioProcessor,
            media_stream_constraints={"audio": True},
        )
        
        if audio_ctx and audio_ctx.state.playing and hasattr(audio_ctx, 'audio_processor') and audio_ctx.audio_processor:
            frames = audio_ctx.audio_processor.frames
            if frames:
                # Convert frames to audio
                audio_data = np.concatenate(frames, axis=0)
                # If audio_data is 2D, flatten to 1D for mono
                if audio_data.ndim > 1:
                    audio_data = audio_data.flatten()
                # Convert to float32
                audio_data = audio_data.astype(np.float32)
                sf.write(user_wav_path, audio_data, user_sr)
                user_audio = audio_data
                st.success("Audio recorded successfully!")
                
                # Play recorded audio
                st.audio(user_wav_path, format='audio/wav')

    else:  # Upload mode
        uploaded_file = st.file_uploader(
            'Upload Audio File', 
            type=['wav', 'mp3', 'm4a'],
            help="Upload your audio file for analysis"
        )
        
        if uploaded_file:
            user_wav_path = f"uploaded_user_{uuid.uuid4().hex[:8]}.wav"
            with open(user_wav_path, 'wb') as f:
                f.write(uploaded_file.read())
            st.success("Audio uploaded successfully!")
            st.audio(user_wav_path, format='audio/wav')

    # Analysis button
    if ref_file_path and os.path.exists(user_wav_path):
        if st.button("Analyze Pitch Differences", type="primary"):
            with st.spinner("Analyzing pitch differences..."):
                try:
                    # Perform 5-second segment analysis
                    segments_data = analyze_5second_segments(user_wav_path, ref_file_path)
                    
                    if segments_data:
                        st.success(f"Analysis complete! Found {len(segments_data)} segments with significant differences.")
                        
                        # Generate feedback
                        feedback = generate_segment_feedback(segments_data)
                        
                        # Display results
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.subheader("Analysis Results")
                            for segment in segments_data[:5]:  # Show first 5 segments
                                with st.expander(f"Segment {segment['segment_id']+1} ({segment['start_time']:.1f}s - {segment['end_time']:.1f}s)"):
                                    st.write(f"Issues found: {len(segment['differences'])}")
                                    for diff in segment['differences'][:3]:
                                        st.write(f"• {diff['message']}")
                        
                        with col2:
                            st.subheader("Visualization")
                            fig = create_segment_visualization(segments_data)
                            st.pyplot(fig)
                        
                        # Save analysis data
                        auth_system = AuthSystem()
                        analysis_data = {
                            'segments': segments_data,
                            'feedback': feedback,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        auth_system.save_analysis_data(
                            st.session_state['user_data']['user_id'],
                            ref_file_path,
                            user_wav_path,
                            json.dumps(analysis_data),
                            json.dumps({'total_segments': len(segments_data)}),
                            json.dumps(segments_data)
                        )
                        
                    else:
                        st.success("Excellent! No significant pitch differences detected.")
                        
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")

def show_qirat_recitation_mode():
    """Show QIRAT recitation mode with speech recognition"""
    st.header("QIRAT Recitation Mode")
    st.write("Practice Quran recitation with AI-powered pronunciation and Tajweed analysis.")
    
    if not QURAN_ASR_AVAILABLE:
        st.error("QIRAT Speech Recognition is not available. Please install required packages.")
        st.code("pip install openai-whisper arabic-reshaper python-bidi")
        return
    
    # Verse selection
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Select Verse")
        
        # Get surahs
        surahs = get_qirat_surahs()
        selected_surah_name = st.selectbox("Select Surah:", list(surahs.keys()))
        surah_id = surahs[selected_surah_name]
        
        # Get verses for selected surah
        verses = get_surah_verses(surah_id)
        selected_verse_name = st.selectbox("Select Verse:", list(verses.keys()))
        verse_id = verses[selected_verse_name]
        
        # Display selected verse
        if st.button("Load Verse"):
            try:
                qsr = QuranSpeechRecognition()
                verse_data = qsr.get_quran_verse(surah_id, verse_id)
                
                if 'error' not in verse_data:
                    st.session_state['current_verse'] = verse_data
                    st.success("Verse loaded successfully!")
                else:
                    st.error(f"Failed to load verse: {verse_data['error']}")
            except Exception as e:
                st.error(f"Error loading verse: {str(e)}")
    
    with col2:
        st.subheader("Record Your Recitation")
        
        # Audio recording
        class AudioProcessor(AudioProcessorBase):
            def __init__(self):
                self.frames = []
            def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
                pcm = frame.to_ndarray()
                self.frames.append(pcm)
                return frame
        
        audio_ctx = webrtc_streamer(
            key="qirat_audio",
            mode=WebRtcMode.SENDRECV,
            audio_receiver_size=1024,
            audio_processor_factory=AudioProcessor,
            media_stream_constraints={"audio": True},
        )
        
        if audio_ctx and audio_ctx.state.playing and hasattr(audio_ctx, 'audio_processor') and audio_ctx.audio_processor:
            frames = audio_ctx.audio_processor.frames
            if frames and len(frames) > 0:
                audio_data = np.concatenate(frames, axis=0)
                if audio_data.ndim > 1:
                    audio_data = audio_data.flatten()
                audio_data = audio_data.astype(np.float32)
                user_wav_path = f"qirat_recitation_{uuid.uuid4().hex[:8]}.wav"
                try:
                    sf.write(user_wav_path, audio_data, 48000)
                    st.session_state['qirat_audio_path'] = user_wav_path
                    st.success("Recitation recorded successfully!")
                    st.audio(user_wav_path, format='audio/wav')
                except Exception as e:
                    st.error(f"Failed to save audio: {e}")
            else:
                st.warning("No audio data recorded.")
    
    # Analysis section
    if 'current_verse' in st.session_state and 'qirat_audio_path' in st.session_state:
        st.subheader("Analyze Your Recitation")
        
        if st.button("Analyze Recitation", type="primary"):
            with st.spinner("Analyzing your recitation..."):
                try:
                    qsr = QuranSpeechRecognition()
                    verse_data = st.session_state['current_verse']
                    audio_path = st.session_state['qirat_audio_path']
                    
                    # Compare recitation
                    result = qsr.compare_recitation(audio_path, verse_data['surah'], verse_data['ayah'])
                    
                    if 'error' not in result:
                        # Display results
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.subheader("Analysis Results")
                            
                            # Overall scores
                            st.metric("Pronunciation Accuracy", f"{result['comparison']['accuracy_percentage']:.1f}%")
                            st.metric("Tajweed Score", f"{result['tajweed_analysis']['score']:.1f}/100")
                            st.metric("Confidence", f"{result['confidence']:.2f}")
                            
                            # Text comparison
                            st.subheader("Text Comparison")
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.write("Your Recitation:")
                                st.text(result['user_text'])
                            with col_b:
                                st.write("Correct Text:")
                                st.text(result['correct_text'])
                        
                        with col2:
                            st.subheader("Feedback")
                            
                            # Generate feedback
                            feedback = qsr.generate_feedback(result)
                            
                            if feedback['positive_feedback']:
                                st.success("Positive Feedback:")
                                for msg in feedback['positive_feedback']:
                                    st.write(f"• {msg}")
                            
                            if feedback['areas_for_improvement']:
                                st.warning("Areas for Improvement:")
                                for msg in feedback['areas_for_improvement']:
                                    st.write(f"• {msg}")
                            
                            if feedback['suggestions']:
                                st.info("Suggestions:")
                                for msg in feedback['suggestions']:
                                    st.write(f"• {msg}")
                        
                        # Save analysis
                        auth_system = AuthSystem()
                        analysis_data = {
                            'recitation_analysis': result,
                            'feedback': feedback,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        auth_system.save_analysis_data(
                            st.session_state['user_data']['user_id'],
                            f"Surah {verse_data['surah']}:{verse_data['ayah']}",
                            audio_path,
                            json.dumps(analysis_data),
                            json.dumps({
                                'pronunciation_score': result['comparison']['accuracy_percentage'],
                                'tajweed_score': result['tajweed_analysis']['score']
                            }),
                            json.dumps([])
                        )
                        
                    else:
                        st.error(f"Analysis failed: {result['error']}")
                        
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")

def show_tajweed_practice_mode():
    """Show Tajweed practice mode"""
    st.header("Tajweed Practice Mode")
    st.write("Learn and practice Tajweed rules with interactive exercises.")
    
    st.info("Tajweed Practice Mode is under development. Coming soon!")
    
    # Placeholder for Tajweed practice features
    st.subheader("Tajweed Rules Overview")
    
    tajweed_rules = {
        "Ghunnah": "Nasalization of ن and م when followed by certain letters",
        "Idgham": "Merging of ن with following letters",
        "Ikhfa": "Partial hiding of ن sound",
        "Qalqalah": "Bouncing sound for ق ط ب ج د",
        "Madd": "Elongation of vowels"
    }
    
    for rule, description in tajweed_rules.items():
        with st.expander(f"{rule}"):
            st.write(description)
            st.write("Practice exercises coming soon...")

def show_memorization_mode():
    """Show memorization mode"""
    st.header("Memorization Mode (Hifz)")
    st.write("Master Quran memorization with spaced repetition and progress tracking.")
    
    st.info("Memorization Mode is under development. Coming soon!")
    
    # Placeholder for memorization features
    st.subheader("Your Memorization Progress")
    st.write("Track your progress through different surahs and verses.")
    
    # Mock progress data
    progress_data = {
        "Al-Fatiha": {"memorized": 7, "total": 7, "last_review": "2024-01-15"},
        "Al-Baqarah": {"memorized": 45, "total": 286, "last_review": "2024-01-14"},
        "Ya-Sin": {"memorized": 0, "total": 83, "last_review": "Never"}
    }
    
    for surah, data in progress_data.items():
        progress = (data['memorized'] / data['total']) * 100
        st.write(f"{surah}: {data['memorized']}/{data['total']} verses ({progress:.1f}%)")
        st.progress(progress / 100)

def show_progress_tracking_mode():
    """Show progress tracking mode"""
    st.header("Progress Tracking")
    st.write("Monitor your learning progress and improvement over time.")
    
    # Get user's analysis history
    auth_system = AuthSystem()
    success, analyses = auth_system.get_user_analyses(st.session_state['user_data']['user_id'], limit=20)
    
    if success and analyses:
        st.subheader("Your Analysis History")
        
        # Create progress chart
        dates = []
        scores = []
        
        for analysis in analyses:
            if analysis.get('summary_stats'):
                try:
                    stats = json.loads(analysis['summary_stats'])
                    if 'accuracy_percentage' in stats:
                        dates.append(analysis['date'][:10])
                        scores.append(stats['accuracy_percentage'])
                except:
                    pass
        
        if dates and scores:
            # Create progress chart
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(dates, scores, marker='o', linewidth=2, markersize=6)
            ax.set_xlabel('Date')
            ax.set_ylabel('Accuracy Score (%)')
            ax.set_title('Your Learning Progress')
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            
            # Progress summary
            if len(scores) > 1:
                improvement = scores[-1] - scores[0]
                st.metric("Overall Improvement", f"{improvement:+.1f}%")
                st.metric("Best Score", f"{max(scores):.1f}%")
                st.metric("Average Score", f"{sum(scores)/len(scores):.1f}%")
        
        # Recent analyses
        st.subheader("Recent Analyses")
        for analysis in analyses[:5]:
            with st.expander(f"Analysis {analysis.get('id')} - {analysis.get('date', '')[:10]}"):
                st.write(f"Reference: {os.path.basename(analysis.get('reference_file', ''))}")
                if analysis.get('summary_stats'):
                    try:
                        stats = json.loads(analysis['summary_stats'])
                        if 'accuracy_percentage' in stats:
                            st.write(f"Accuracy: {stats['accuracy_percentage']:.1f}%")
                    except:
                        pass
    else:
        st.info("No analysis history found. Start practicing to see your progress!")

def main():
    """Main application entry point"""
    if not st.session_state['authenticated']:
        # Show authentication pages
        if st.session_state['show_register']:
            show_register_page()
        elif st.session_state['show_forgot_password']:
            show_forgot_password_page()
        else:
            show_login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()