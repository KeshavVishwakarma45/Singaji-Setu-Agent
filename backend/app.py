from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import json
import time
import uuid
from io import BytesIO
import soundfile as sf
import numpy as np
from werkzeug.utils import secure_filename
import base64

from services.transcription_service import TranscriptionService
from services.gemini_service import GeminiService
from services.live_transcription_service import LiveTranscriptionService
from config.settings import (
    GCS_BUCKET_NAME,
    get_gcp_project_id,
    GCP_LOCATION,
    validate_environment
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'singaji-setu-secret'

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, 
    cors_allowed_origins="*", 
    async_mode='threading', 
    logger=False, 
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=10000000
)

# Global state (like Streamlit session_state)
app_state = {
    'audio_data': None,
    'sample_rate': None,
    'transcript': None,
    'gemini_result': None,
    'transcription_service': None,
    'gemini_service': None,
    'live_service': None,
    'live_transcript': ''
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

@app.route('/api/reset', methods=['POST'])
def reset_session():
    """Reset all session data"""
    global app_state
    app_state = {
        'audio_data': None,
        'sample_rate': None,
        'transcript': None,
        'gemini_result': None,
        'transcription_service': app_state['transcription_service'],
        'gemini_service': app_state['gemini_service'],
        'live_service': None,
        'live_transcript': ''
    }
    return jsonify({'success': True, 'message': 'Session reset'})

@app.route('/api/process', methods=['POST'])
def process_audio():
    """Upload + Transcribe + Analyze in one go"""
    try:
        print("=== Process request (upload + transcribe + analyze) ===")
        init_services()
        
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file'}), 400
        
        file = request.files['audio']
        print(f"File: {file.filename}")
        
        # Read file content
        file_content = file.read()
        print(f"File size: {len(file_content)} bytes")
        
        # Save to temp file for transcription
        temp_path = f"temp_{int(time.time())}.webm"
        with open(temp_path, 'wb') as f:
            f.write(file_content)
        
        # Transcribe directly
        print("Transcribing...")
        with open(temp_path, 'rb') as f:
            transcript = app_state['transcription_service'].transcribe_full_file(
                f,
                language_code='hi-IN'
            )
        
        # Cleanup
        try:
            os.remove(temp_path)
        except:
            pass
        
        if not transcript:
            return jsonify({'error': 'Transcription failed'}), 500
        
        print(f"Transcript: {len(transcript)} chars")
        app_state['transcript'] = transcript
        
        # Analyze with Gemini
        print("Analyzing with AI...")
        schema = get_default_schema()
        schema_json = json.dumps(schema, indent=2)
        
        result = app_state['gemini_service'].generate_json_payload(schema_json, transcript)
        
        if not result:
            return jsonify({'error': 'Analysis failed'}), 500
        
        app_state['gemini_result'] = result
        print("Complete!")
        
        return jsonify({
            'success': True,
            'transcript': transcript,
            'result': result
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
        
        # Save transcript to GCS
        try:
            init_services()
            if app_state['transcription_service'] and app_state['transcription_service'].storage_client:
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'live_transcript_{timestamp}.txt'
                
                bucket = app_state['transcription_service'].storage_client.bucket(GCS_BUCKET_NAME)
                blob = bucket.blob(f'transcripts/{filename}')
                blob.upload_from_string(transcript, content_type='text/plain')
                print(f'✅ Transcript saved to GCS: {filename}')
        except Exception as e:
            print(f'⚠️ Failed to save to GCS: {e}')
        
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
                return jsonify({'error': 'No transcript found'}), 404
            
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
                return jsonify({'error': 'No analysis result found'}), 404
            
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
            
            audio_data = app_state['audio_data']
            sample_rate = app_state['sample_rate']
            
            buffer = BytesIO()
            sf.write(buffer, audio_data, sample_rate, format='WAV')
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype='audio/wav',
                as_attachment=True,
                download_name=f'interview_{int(time.time())}.wav'
            )
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_default_schema():
    """Default schema for farmer survey"""
    return {
        "farmerDetails": {
            "farmerName": "string (Full name of the farmer)",
            "village": "string (Village, Tehsil, and District if available)",
            "contactNumber": "string (10-digit mobile number, if provided)",
            "farmingExperienceYears": "number (Number of years in farming)",
            "householdSize": "number (Total number of family members)",
        },
        "farmDetails": {
            "totalLandSizeAcres": "number (Total acres of land owned or farmed)",
            "soilType": "string (e.g., 'Black', 'Red', 'Alluvial', 'Loam')",
            "primaryCrops": [
                "list of strings (Main crops grown, e.g., 'Wheat', 'Cotton')"
            ],
            "irrigationSource": "string (e.g., 'Canal', 'Well', 'Borewell', 'Rain-fed')",
        },
        "livestockDetails": {
            "hasLivestock": "boolean (Does the farmer own any farm animals?)",
            "animals": [
                {
                    "type": "string (e.g., 'Cow', 'Buffalo', 'Goat', 'Chicken')",
                    "count": "number (The number of animals of this type)",
                }
            ],
        },
        "challengesAndNeeds": {
            "mainChallenges": [
                "list of strings (Primary difficulties faced, e.g., 'Pest attacks', 'Low water', 'Market price')"
            ],
            "interestedInNewTech": "boolean (Is the farmer open to trying new technology or methods?)",
            "specificNeeds": [
                "list of strings (Specific help they are looking for, e.g., 'Loan information', 'Better seeds')"
            ],
        },
        "interviewMetadata": {
            "interviewerName": "string (Name of the person conducting the interview)",
            "interviewDate": "string (Date of the interview in YYYY-MM-DD format)",
            "summary": "string (A brief, 2-3 sentence summary of the entire conversation)",
        },
    }

@socketio.on('connect')
def handle_connect():
    print(f'✅ Client connected: {request.sid}')
    emit('connected', {'status': 'ready', 'sid': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'❌ Client disconnected: {request.sid}')
    # Cleanup live service if exists
    if app_state.get('live_service'):
        try:
            app_state['live_service'].stop_streaming()
        except:
            pass

@socketio.on('start_stream')
def handle_start_stream():
    print('🎙️ Starting GCP live transcription stream')
    app_state['live_transcript'] = ''
    
    # Create live service
    app_state['live_service'] = LiveTranscriptionService()
    
    # Callback for transcription results
    def on_transcript(text, is_final):
        if is_final:
            app_state['live_transcript'] += text + ' '
            print(f'📤 Sending final: {text}')
            socketio.emit('transcript_update', {
                'transcript': text,
                'is_final': True,
                'full_transcript': app_state['live_transcript']
            })
        else:
            print(f'📤 Sending interim: {text[:30]}...')
            socketio.emit('transcript_update', {
                'transcript': text,
                'is_final': False
            })
    
    # Start streaming
    app_state['live_service'].start_streaming(on_transcript, language_code='hi-IN')
    socketio.emit('stream_started', {'status': 'streaming'})

@socketio.on('audio_data')
def handle_audio_data(data):
    try:
        audio_bytes = base64.b64decode(data['audio'])
        
        # Send to live transcription service
        if app_state['live_service']:
            app_state['live_service'].add_audio_chunk(audio_bytes)
            
    except Exception as e:
        print(f'❌ Streaming error: {e}')
        import traceback
        traceback.print_exc()
        socketio.emit('error', {'message': str(e)})

@socketio.on('stop_stream')
def handle_stop_stream():
    print('⏹️ Stopping stream and analyzing...')
    
    try:
        # Stop live transcription
        if app_state['live_service']:
            app_state['live_service'].stop_streaming()
        
        transcript = app_state['live_transcript'].strip()
        
        if not transcript:
            print('⚠️ No transcript generated')
            socketio.emit('error', {'message': 'No transcript generated'})
            return
        
        print(f'📝 Final transcript: {len(transcript)} chars')
        app_state['transcript'] = transcript
        
        # Save to GCS
        try:
            init_services()
            if app_state['transcription_service'] and app_state['transcription_service'].storage_client:
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'live_transcript_{timestamp}.txt'
                
                bucket = app_state['transcription_service'].storage_client.bucket(GCS_BUCKET_NAME)
                blob = bucket.blob(f'transcripts/{filename}')
                blob.upload_from_string(transcript, content_type='text/plain')
                print(f'✅ Transcript saved to GCS: {filename}')
        except Exception as e:
            print(f'⚠️ Failed to save to GCS: {e}')
        
        # Analyze with Gemini
        print('🤖 Analyzing with AI...')
        schema = get_default_schema()
        schema_json = json.dumps(schema, indent=2)
        result = app_state['gemini_service'].generate_json_payload(schema_json, transcript)
        
        if not result:
            print('⚠️ Analysis failed')
            socketio.emit('error', {'message': 'Analysis failed'})
            return
        
        app_state['gemini_result'] = result
        print('✅ Complete!')
        
        socketio.emit('analysis_complete', {
            'transcript': transcript,
            'result': result
        })
            
    except Exception as e:
        print(f'❌ Analysis error: {e}')
        import traceback
        traceback.print_exc()
        socketio.emit('error', {'message': str(e)})

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    print("🌾 Starting Singaji Setu Agent with Live Streaming")
    
    # Get port from environment (Railway/Heroku) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    socketio.run(app, 
                debug=False, 
                host='0.0.0.0', 
                port=port, 
                use_reloader=False, 
                allow_unsafe_werkzeug=True)
