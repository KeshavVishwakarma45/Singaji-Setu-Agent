from google.cloud import speech
import queue
import threading
import os
from config.settings import get_service_account_credentials

class LiveTranscriptionService:
    """Real-time streaming transcription using Google Cloud Speech-to-Text"""
    
    def __init__(self):
        # Set credentials properly
        creds_path = get_service_account_credentials()
        if creds_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        
        self.client = speech.SpeechClient()
        self.audio_queue = queue.Queue()
        self.is_streaming = False
        self.transcript_callback = None
        
    def audio_generator(self):
        """Generator that yields audio chunks from queue"""
        while self.is_streaming:
            try:
                chunk = self.audio_queue.get(timeout=1)
                if chunk is None:
                    break
                yield chunk
            except queue.Empty:
                continue
    
    def start_streaming(self, callback, language_code='hi-IN'):
        """Start real-time streaming transcription"""
        self.is_streaming = True
        self.transcript_callback = callback
        
        # Streaming config
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code=language_code,
            enable_automatic_punctuation=True,
            model='latest_long',
        )
        
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True,
        )
        
        # Create streaming request generator
        def request_generator():
            for chunk in self.audio_generator():
                yield speech.StreamingRecognizeRequest(audio_content=chunk)
        
        # Start streaming in background thread
        def stream_audio():
            try:
                requests = request_generator()
                responses = self.client.streaming_recognize(streaming_config, requests)
                
                print('🎙️ Live streaming started...')
                for response in responses:
                    if not response.results:
                        continue
                    
                    result = response.results[0]
                    if not result.alternatives:
                        continue
                    
                    transcript = result.alternatives[0].transcript
                    is_final = result.is_final
                    
                    # Log for debugging
                    if is_final:
                        print(f'✅ Final: {transcript}')
                    else:
                        print(f'⏳ Interim: {transcript[:50]}...')
                    
                    # Send to callback
                    if self.transcript_callback:
                        self.transcript_callback(transcript, is_final)
                
                print('🎙️ Streaming ended normally')
                        
            except Exception as e:
                print(f'❌ Streaming error: {e}')
                import traceback
                traceback.print_exc()
                if self.transcript_callback:
                    self.transcript_callback(f'Error: {str(e)}', True)
        
        # Start thread
        self.stream_thread = threading.Thread(target=stream_audio)
        self.stream_thread.start()
    
    def add_audio_chunk(self, audio_bytes):
        """Add audio chunk to processing queue"""
        if self.is_streaming:
            self.audio_queue.put(audio_bytes)
    
    def stop_streaming(self):
        """Stop streaming transcription"""
        self.is_streaming = False
        self.audio_queue.put(None)  # Signal end
        if hasattr(self, 'stream_thread'):
            self.stream_thread.join(timeout=2)
