from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import time
from io import BytesIO
import soundfile as sf
import numpy as np

from services.transcription_service import TranscriptionService
from services.gemini_service import GeminiService
from config.settings import (
    GCS_BUCKET_NAME,
    get_gcp_project_id,
    GCP_LOCATION,
    validate_environment
)

app = Flask(__name__)
CORS(app)

# Global storage (like Streamlit session_state)
app_state = {
    'audio_data': None,
    'sample_rate': None,
    'transcript': None,
    'gemini_result': None,
    'transcription_service': None,
    'gemini_service': None
}

def init_services():
    if app_state['transcription_service'] is None:
        if not validate_environment():
            return False
        
        project_id = get_gcp_project_id()
        if not project_id:
            return False
        
        app_state['transcription_service'] = TranscriptionService(
            gcs_bucket_name=GCS_BUCKET_NAME,
            gcp_project_id=project_id,
            gcp_location=GCP_LOCATION
        )
        app_state['gemini_service'] = GeminiService()
    return True

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

@app.route('/api/upload', methods=['POST'])
def upload_audio():
    try:
        print("=== Upload request ===")
        init_services()
        
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file'}), 400
        
        file = request.files['audio']
        print(f"File: {file.filename}")
        
        # Save temporarily
        temp_path = f"temp_audio_{int(time.time())}.wav"
        file.save(temp_path)
        
        # Read audio
        audio_data, sample_rate = sf.read(temp_path)
        print(f"Loaded: {len(audio_data)} samples at {sample_rate}Hz")
        
        # Convert to mono
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
        
        # Store in app state
        app_state['audio_data'] = audio_data
        app_state['sample_rate'] = sample_rate
        
        # Cleanup
        os.remove(temp_path)
        
        duration = len(audio_data) / sample_rate
        print(f"Success! Duration: {duration}s")
        
        return jsonify({
            'success': True,
            'duration': duration,
            'sample_rate': int(sample_rate)
        })
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    try:
        print("=== Transcribe request ===")
        
        if app_state['audio_data'] is None:
            return jsonify({'error': 'No audio data'}), 400
        
        # Create file-like object
        audio_file = BytesIO()
        sf.write(audio_file, app_state['audio_data'], app_state['sample_rate'], format='WAV')
        audio_file.seek(0)
        audio_file.name = 'audio.wav'
        
        # Transcribe
        transcript = app_state['transcription_service'].transcribe_full_file(
            audio_file,
            language_code='hi-IN'
        )
        
        if transcript:
            app_state['transcript'] = transcript
            print(f"Transcript: {len(transcript)} chars")
            
            return jsonify({
                'success': True,
                'transcript': transcript,
                'word_count': len(transcript.split())
            })
        
        return jsonify({'error': 'Transcription failed'}), 500
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        print("=== Analyze request ===")
        
        data = request.json
        transcript = data.get('transcript') or app_state['transcript']
        
        if not transcript:
            return jsonify({'error': 'No transcript'}), 400
        
        # Update transcript if edited
        app_state['transcript'] = transcript
        
        # Get schema
        schema = get_default_schema()
        schema_json = json.dumps(schema, indent=2)
        
        # Generate payload
        result = app_state['gemini_service'].generate_json_payload(schema_json, transcript)
        
        if result:
            app_state['gemini_result'] = result
            print("Analysis complete")
            return jsonify({'success': True, 'result': result})
        
        return jsonify({'error': 'Analysis failed'}), 500
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<file_type>', methods=['GET'])
def download_file(file_type):
    try:
        if file_type == 'transcript':
            transcript = app_state['transcript']
            if not transcript:
                return jsonify({'error': 'No transcript'}), 404
            
            buffer = BytesIO(transcript.encode('utf-8'))
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype='text/plain',
                as_attachment=True,
                download_name=f'transcript_{int(time.time())}.txt'
            )
        
        elif file_type == 'json':
            result = app_state['gemini_result']
            if not result:
                return jsonify({'error': 'No result'}), 404
            
            json_str = json.dumps(result, indent=2, ensure_ascii=False)
            buffer = BytesIO(json_str.encode('utf-8'))
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype='application/json',
                as_attachment=True,
                download_name=f'survey_{int(time.time())}.json'
            )
        
        elif file_type == 'audio':
            if app_state['audio_data'] is None:
                return jsonify({'error': 'No audio'}), 404
            
            buffer = BytesIO()
            sf.write(buffer, app_state['audio_data'], app_state['sample_rate'], format='WAV')
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype='audio/wav',
                as_attachment=True,
                download_name=f'interview_{int(time.time())}.wav'
            )
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

def get_default_schema():
    return {
        "farmerDetails": {
            "farmerName": "string",
            "village": "string",
            "contactNumber": "string",
            "farmingExperienceYears": "number",
            "householdSize": "number",
        },
        "farmDetails": {
            "totalLandSizeAcres": "number",
            "soilType": "string",
            "primaryCrops": ["list of strings"],
            "irrigationSource": "string",
        },
        "livestockDetails": {
            "hasLivestock": "boolean",
            "animals": [{"type": "string", "count": "number"}],
        },
        "challengesAndNeeds": {
            "mainChallenges": ["list of strings"],
            "interestedInNewTech": "boolean",
            "specificNeeds": ["list of strings"],
        },
        "interviewMetadata": {
            "interviewerName": "string",
            "interviewDate": "string",
            "summary": "string",
        },
    }

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    print("🌾 Starting Singaji Setu Agent - Simple Version")
    app.run(debug=True, host='0.0.0.0', port=5000)
