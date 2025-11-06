#!/usr/bin/env python3
"""
Test script to debug transcription service issues
"""
import os
import sys
from io import BytesIO
import soundfile as sf
import numpy as np

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import validate_environment, get_gcp_project_id, GCS_BUCKET_NAME, GCP_LOCATION
from services.transcription_service import TranscriptionService
from services.gemini_service import GeminiService

def test_environment():
    """Test environment setup"""
    print("=== Testing Environment ===")
    
    # Check environment variables
    env_valid = validate_environment()
    print(f"Environment valid: {env_valid}")
    
    # Check project ID
    project_id = get_gcp_project_id()
    print(f"Project ID: {project_id}")
    
    # Check bucket name
    print(f"Bucket name: {GCS_BUCKET_NAME}")
    
    return env_valid and project_id

def test_transcription_service():
    """Test transcription service initialization"""
    print("\n=== Testing Transcription Service ===")
    
    try:
        project_id = get_gcp_project_id()
        service = TranscriptionService(
            gcs_bucket_name=GCS_BUCKET_NAME,
            gcp_project_id=project_id,
            gcp_location=GCP_LOCATION
        )
        
        print(f"Speech client initialized: {service.speech_client is not None}")
        print(f"Storage client initialized: {service.storage_client is not None}")
        
        return service
        
    except Exception as e:
        print(f"Transcription service error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_gemini_service():
    """Test Gemini service initialization"""
    print("\n=== Testing Gemini Service ===")
    
    try:
        service = GeminiService()
        print(f"Gemini LLM initialized: {service.llm is not None}")
        return service
        
    except Exception as e:
        print(f"Gemini service error: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_test_audio():
    """Create a simple test audio file"""
    print("\n=== Creating Test Audio ===")
    
    # Generate 5 seconds of sine wave (440 Hz)
    sample_rate = 16000
    duration = 5
    t = np.linspace(0, duration, sample_rate * duration, False)
    audio_data = 0.3 * np.sin(2 * np.pi * 440 * t)
    
    # Create BytesIO buffer
    buffer = BytesIO()
    sf.write(buffer, audio_data, sample_rate, format='WAV')
    buffer.seek(0)
    buffer.name = 'test_audio.wav'
    
    print(f"Test audio created: {len(audio_data)} samples at {sample_rate}Hz")
    return buffer

def test_transcription(service, audio_buffer):
    """Test actual transcription"""
    print("\n=== Testing Transcription ===")
    
    try:
        transcript = service.transcribe_full_file(audio_buffer, language_code='hi-IN')
        print(f"Transcription result: {transcript}")
        return transcript
        
    except Exception as e:
        print(f"Transcription error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("Singaji Setu Agent - Service Test")
    print("=" * 50)
    
    # Test 1: Environment
    if not test_environment():
        print("ERROR: Environment test failed. Check your .env file.")
        sys.exit(1)
    
    # Test 2: Services
    transcription_service = test_transcription_service()
    gemini_service = test_gemini_service()
    
    if not transcription_service:
        print("ERROR: Transcription service failed to initialize")
        sys.exit(1)
        
    if not gemini_service:
        print("ERROR: Gemini service failed to initialize")
        sys.exit(1)
    
    # Test 3: Audio processing
    test_audio = create_test_audio()
    
    # Test 4: Transcription (this will likely fail with sine wave, but tests the pipeline)
    transcript = test_transcription(transcription_service, test_audio)
    
    print("\n" + "=" * 50)
    print("Service test completed!")
    print("Note: Transcription may be empty for sine wave audio - this is expected.")