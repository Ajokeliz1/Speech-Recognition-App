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
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()

def transcribe_speech(api, language, wit_key=None):
    """Transcribe speech using the selected API with error handling"""
    try:
        if api == "Google":
            return st.session_state.recognizer.recognize_google(
                st.session_state.audio_data, 
                language=language
            )
        elif api == "Sphinx":
            return st.session_state.recognizer.recognize_sphinx(
                st.session_state.audio_data, 
                language=language
            )
        elif api == "Wit.ai":
            if not wit_key:
                return "Error: Wit.ai API key is required"
            return st.session_state.recognizer.recognize_wit(
                st.session_state.audio_data, 
                key=wit_key
            )
    except sr.UnknownValueError:
        return "Error: Could not understand audio"
    except sr.RequestError as e:
        return f"Error: API unavailable - {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

def start_recording():
    """Begin recording audio"""
    st.session_state.recording = True
    st.session_state.audio_source = sr.Microphone()
    st.session_state.recognizer = sr.Recognizer()

def stop_recording():
    """Stop recording and process audio"""
    if st.session_state.recording:
        st.session_state.recording = False
        with st.spinner("Processing audio..."):
            try:
                with st.session_state.audio_source as source:
                    st.session_state.audio_data = st.session_state.recognizer.listen(source)
                
                st.session_state.transcript = transcribe_speech(
                    st.session_state.selected_api,
                    st.session_state.selected_language,
                    st.session_state.wit_key
                )
            except Exception as e:
                st.session_state.transcript = f"Recording error: {str(e)}"

def pause_recording():
    """Pause the current recording session"""
    if st.session_state.recording:
        st.session_state.recording = False

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
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Recording", disabled=st.session_state.recording):
            start_recording()
    
    with col2:
        if st.button("Stop Recording", disabled=not st.session_state.recording):
            stop_recording()

    # Pause button
    if st.session_state.recording:
        if st.button("Pause Recording"):
            pause_recording()

    # Status indicator
    if st.session_state.recording:
        st.warning("Recording... Speak now (press Stop when finished)")
        
        # Create a live listening indicator
        indicator = st.empty()
        now = time.time()
        
        # Update indicator every 0.5 seconds
        if now - st.session_state.last_update > 0.5:
            if hasattr(st.session_state, 'indicator_state'):
                st.session_state.indicator_state = not st.session_state.indicator_state
            else:
                st.session_state.indicator_state = True
                
            st.session_state.last_update = now
        
        # Show blinking indicator
        if st.session_state.indicator_state:
            indicator.info("● Listening...")
        else:
            indicator.info("○ Listening...")
        
        # Rerun to update UI
        time.sleep(0.1)
        

    # Display transcription
    st.subheader("Transcription Result")
    st.text_area("Output", 
                value=st.session_state.transcript, 
                height=150,
                key="transcript_output")

    # Save to file
    if st.session_state.transcript:
        st.download_button(
            label="Save Transcription",
            data=st.session_state.transcript,
            file_name="transcription.txt",
            mime="text/plain"
        )

    # Usage instructions
    with st.expander("Usage Instructions"):
        st.markdown("""
        1. **Select API & Language**: Choose from sidebar
        2. **Start Recording**: Click Start button and speak
        3. **Stop**: Click Stop to process audio
        4. **Pause**: Temporarily stop recording
        5. **Save**: Download transcription when available
        
        **Supported APIs**:
        - Google (online, requires internet)
        - Sphinx (offline, limited language support)
        - Wit.ai (requires API key)
        
        **Note**: Recording may take a few seconds to start. 
        Speak clearly and ensure your microphone is working.
        """)

if __name__ == "__main__":
    main()