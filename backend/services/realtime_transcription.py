# services/realtime_transcription.py
import streamlit as st
from google.cloud import speech
import pyaudio
import queue
import threading
from config.settings import get_service_account_credentials
import os

class RealtimeTranscription:
    """Real-time audio transcription using Google Cloud Speech-to-Text streaming."""
    
    def __init__(self):
        self.creds_path = get_service_account_credentials()
        if self.creds_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.creds_path
            self.client = speech.SpeechClient()
        else:
            self.client = None
        
        # Audio recording parameters
        self.RATE = 16000
        self.CHUNK = int(self.RATE / 10)  # 100ms chunks
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.transcript_parts = []
        
    def audio_generator(self):
        """Generator that yields audio chunks from the queue."""
        while self.is_recording:
            chunk = self.audio_queue.get()
            if chunk is None:
                return
            yield chunk
    
    def start_streaming(self, language_code="hi-IN"):
        """Start real-time streaming transcription."""
        if not self.client:
            st.error("Speech client not initialized")
            return
        
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.RATE,
            language_code=language_code,
            enable_automatic_punctuation=True,
        )
        
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True
        )
        
        audio_generator = self.audio_generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )
        
        responses = self.client.streaming_recognize(streaming_config, requests)
        
        return responses
