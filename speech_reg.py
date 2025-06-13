import streamlit as st
import speech_recognition as sr
import time
from io import StringIO

# Initialize session state variables
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'transcript' not in st.session_state:
    st.session_state.transcript = ''
if 'audio_source' not in st.session_state:
    st.session_state.audio_source = None
if 'recognizer' not in st.session_state:
    st.session_state.recognizer = sr.Recognizer()

def transcribe_speech(api, language, wit_key=None):
    """Transcribe speech using the selected API with error handling"""
    try:
        if api == "Google":
            return st.session_state.recognizer.recognize_google(st.session_state.audio_data, language=language)
        elif api == "Sphinx":
            return st.session_state.recognizer.recognize_sphinx(st.session_state.audio_data, language=language)
        elif api == "Wit.ai":
            if not wit_key:
                raise ValueError("Wit.ai API key is required")
            return st.session_state.recognizer.recognize_wit(st.session_state.audio_data, key=wit_key)
    except sr.UnknownValueError:
        return "Error: Speech not understood"
    except sr.RequestError as e:
        return f"API Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

def start_recording():
    """Begin recording audio"""
    st.session_state.recording = True
    st.session_state.audio_source = sr.Microphone()
    with st.session_state.audio_source as source:
        st.session_state.recognizer.adjust_for_ambient_noise(source)
        st.session_state.audio_data = None

def stop_recording():
    """Stop recording and process audio"""
    if st.session_state.recording:
        st.session_state.recording = False
        with st.spinner("Processing audio..."):
            with st.session_state.audio_source as source:
                st.session_state.audio_data = st.session_state.recognizer.listen(source)
            st.session_state.transcript = transcribe_speech(
                st.session_state.selected_api,
                st.session_state.selected_language,
                st.session_state.wit_key
            )

def pause_recording():
    """Pause the current recording session"""
    if st.session_state.recording:
        st.session_state.recording = False
        st.experimental_rerun()

def main():
    st.title("Enhanced Speech Recognition App")
    
    # Settings sidebar
    with st.sidebar:
        st.header("Settings")
        
        # API selection
        st.session_state.selected_api = st.selectbox(
            "Speech Recognition API",
            ["Google", "Sphinx", "Wit.ai"],
            index=0
        )
        
        # Language selection
        st.session_state.selected_language = st.selectbox(
            "Spoken Language",
            ["en-US", "es-ES", "fr-FR", "de-DE", "it-IT", "ja-JP", "ko-KR", "zh-CN"],
            index=0
        )
        
        # Wit.ai API key input
        st.session_state.wit_key = None
        if st.session_state.selected_api == "Wit.ai":
            st.session_state.wit_key = st.text_input(
                "Wit.ai API Key",
                type="password",
                help="Get your key from https://wit.ai"
            )

    # Display controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Start Recording", disabled=st.session_state.recording):
            start_recording()
    
    with col2:
        if st.button("Pause", disabled=not st.session_state.recording):
            pause_recording()
    
    with col3:
        if st.button("Stop & Process", disabled=not st.session_state.recording):
            stop_recording()

    # Status indicator
    if st.session_state.recording:
        st.warning("Recording... Speak now (press Stop when finished)")
        

    # Display transcription
    st.subheader("Transcription Result")
    st.text_area("Output", value=st.session_state.transcript, height=150)

    # Save to file
    st.download_button(
        label="Save Transcription",
        data=StringIO(st.session_state.transcript).getvalue(),
        file_name="transcription.txt",
        mime="text/plain",
        disabled=not st.session_state.transcript
    )

    # Usage instructions
    with st.expander("Usage Instructions"):
        st.markdown("""
        1. **Select API & Language**: Choose from sidebar
        2. **Start Recording**: Click Start button and speak
        3. **Pause/Stop**: Use buttons to control recording
        4. **Save**: Download transcription when available
        
        **Supported APIs**:
        - Google (online, requires internet)
        - Sphinx (offline, English only)
        - Wit.ai (requires API key)
        """)

if __name__ == "__main__":
    main()