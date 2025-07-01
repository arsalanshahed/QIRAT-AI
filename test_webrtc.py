import streamlit as st
from streamlit_webrtc import webrtc_streamer

st.title("Test WebRTC")
webrtc_streamer(key="test")