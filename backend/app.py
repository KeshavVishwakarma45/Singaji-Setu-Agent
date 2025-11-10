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
    validate_environment,
)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["SECRET_KEY"] = "singaji-setu-secret"

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=10000000,
)

# Global state
app_state = {
    "audio_data": None,
    "sample_rate": None,
    "transcript": None,
    "gemini_result": None,
    "transcription_service": None,
    "gemini_service": None,
    "live_service": None,
    "live_transcript": "",
}


def get_default_schema():
    """Return comprehensive survey schema for farmer interviews"""
    return {
        "farmerDetail": {
            "name": "",
            "contact": "",
            "gender": "",
            "aadharNumber": "",
            "farmSize": "",
            "farmSizeUnit": "",
            "farmCount": "",
            "currentLocation": "",
            "state": "",
            "typeOfFarmer": "",
            "partTimeYearsOfExperience": "",
            "fullTimeYearsOfExperience": "",
            "familyType": "",
            "totalFamilyMembers": "",
            "familyMembersInFarming": "",
            "familyCaretaker": [],
            "userId": "",
            "image": "",
            "farmExperience": "",
            "isFormValid": ""
        },
        "farmerAdditionalInfo": {
            "farmerTechnologyAccess": [
                {
                    "appName": "",
                    "toolServiceUsed": [],
                    "purpose": "",
                    "source": "",
                    "govtSubsidy": "",
                    "socialMedia": [],
                    "smartphoneOwnership": "",
                    "ownedBy": "",
                    "isFormValid": ""
                }
            ],
            "farmerUpdateInformationSources": [
                {
                    "sourceType": "",
                    "sourceName": "",
                    "usedFor": [],
                    "frequency": "",
                    "isFormValid": ""
                }
            ],
            "farmerGovtBenefitsAndLosses": [
                {
                    "schemeName": "",
                    "availed": "",
                    "amount": "",
                    "benefitDescription": "",
                    "issueFaced": "",
                    "isFormValid": ""
                }
            ],
            "farmerOtherIncomeResources": [
                {
                    "sourceType": "",
                    "description": "",
                    "monthlyIncome": "",
                    "isFormValid": ""
                }
            ],
            "farmerStorage": [
                {
                    "facilityType": "",
                    "name": "",
                    "location": "",
                    "capacityQuintals": "",
                    "condition": "",
                    "govtAccess": "",
                    "coldStorageUsed": "",
                    "giveForRent": "",
                    "givenOnRent": "",
                    "monthlyEarnings": "",
                    "image": "",
                    "isFormValid": ""
                }
            ],
            "isFormValid": ""
        },
        "farmerFarmDetails": [
            {
                "farmerLandDetails1": [
                    {
                        "partNo": "",
                        "totalLandAcres": "",
                        "irrigatedAreaAcres": "",
                        "nonIrrigatedAreaAcres": "",
                        "soilType": [],
                        "topography": "",
                        "cropSuitability": [],
                        "khotLand": "",
                        "landType": "",
                        "typeOfFarm": "",
                        "khashraSurveyNumber": "",
                        "measurementUnit": "",
                        "ownedRented": "",
                        "location": "",
                        "distanceFromHomeKm": "",
                        "ownerType": "",
                        "isFormValid": ""
                    }
                ],
                "farmerLandDetails2": {
                    "khotLandCount": "",
                    "surveyNumber": "",
                    "ownershipName": "",
                    "ownedBy": "",
                    "labourPayoutMethod": "",
                    "soilImage": "",
                    "soilReportImage": "",
                    "soilTestingReportAvailable": "",
                    "farmPhoto": "",
                    "farmerPhoto": "",
                    "irrigationMethod": [],
                    "kccStatus": "",
                    "loanStatus": "",
                    "labourAvailability": "",
                    "hiredLabourPayment": "",
                    "farmingApproach": [],
                    "croppingPattern": [],
                    "primaryMarket": [],
                    "harvestingMethod": [],
                    "farmingType": [],
                    "isFormValid": ""
                },
                "farmerWaterManagement": [
                    {
                        "waterSource": [],
                        "usedFor": [],
                        "waterRetentionCapacity": "",
                        "drainageQuality": "",
                        "storageMethod": "",
                        "reliability": "",
                        "linkToLand": [],
                        "linkToCrops": [],
                        "is_active": "",
                        "isFormValid": ""
                    }
                ],
                "farmerCropDetail": [
                    {
                        "cultivationArea": "",
                        "cropName": "",
                        "season": "",
                        "changeEveryYear": "",
                        "cropVariety": "",
                        "seedSource": [],
                        "fertilizerUsed": [],
                        "pesticideUsed": [],
                        "seedingRate": "",
                        "seeding_unit": "",
                        "seedName": "",
                        "linkToLand": "",
                        "basicRequirement": "",
                        "isFormValid": ""
                    }
                ],
                "farmerFertilizer": [
                    {
                        "name": "",
                        "type": "",
                        "quantity": "",
                        "price": "",
                        "brandName": "",
                        "appliedRate": "",
                        "appliedStage": "",
                        "isFormValid": ""
                    }
                ],
                "farmerPesticide": [
                    {
                        "name": "",
                        "type": "",
                        "quantity": "",
                        "price": "",
                        "brandName": "",
                        "appliedRate": "",
                        "appliedStage": "",
                        "isFormValid": ""
                    }
                ],
                "farmerCropSellingDetails": [
                    {
                        "crop": "",
                        "season": "",
                        "quantity": "",
                        "rate": "",
                        "marketRate": "",
                        "soldTo": "",
                        "sellingMethod": "",
                        "directMarket": "",
                        "isFormValid": ""
                    }
                ],
                "farmerLivestock": [
                    {
                        "animalType": "",
                        "breedName": "",
                        "quantity": "",
                        "milkProduction": "",
                        "insuranceAvailable": "",
                        "insuranceCompany": "",
                        "milkSellingPlace": [],
                        "photo": "",
                        "isFormValid": ""
                    }
                ],
                "farmerEquipment": [
                    {
                        "equipment_type": "",
                        "brand_name": "",
                        "owner": "",
                        "storage_capacity": "",
                        "storage_unit": "",
                        "condition": "",
                        "image": "",
                        "provide_on_rent": "",
                        "isFormValid": ""
                    }
                ]
            }
        ]
    }


def _clean_transcript(transcript):
    """Clean and improve transcript for better analysis"""
    if not transcript:
        return transcript
    
    # Remove extra spaces and normalize
    cleaned = ' '.join(transcript.split())
    
    # Fix common transcription issues
    replacements = {
        ' um ': ' ',
        ' uh ': ' ',
        ' er ': ' ',
        '  ': ' ',
        ' हाँ ': ' हाँ, ',
        ' नहीं ': ' नहीं, ',
        ' अच्छा ': ' अच्छा, '
    }
    
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    
    return cleaned.strip()


def init_services():
    try:
        if app_state["transcription_service"] is None:
            print("Initializing services...")

            if not validate_environment():
                print("ERROR: Environment validation failed")
                return False

            project_id = get_gcp_project_id()
            if not project_id:
                print("ERROR: GCP Project ID not found")
                return False

            print(f"Using project: {project_id}")
            print(f"Using bucket: {GCS_BUCKET_NAME}")

            app_state["transcription_service"] = TranscriptionService(
                gcs_bucket_name=GCS_BUCKET_NAME,
                gcp_project_id=project_id,
                gcp_location=GCP_LOCATION,
            )

            if not app_state["transcription_service"].speech_client:
                print("ERROR: Speech client initialization failed")
                return False

            app_state["gemini_service"] = GeminiService()
            print("Services initialized successfully")

        return True
    except Exception as e:
        print(f"ERROR: Service initialization error: {e}")
        return False


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@app.route("/api/test", methods=["POST"])
def test_endpoint():
    """Simple test endpoint"""
    try:
        print("Test endpoint called")
        print(f"Files in request: {list(request.files.keys())}")
        if "audio" in request.files:
            file = request.files["audio"]
            print(f"File received: {file.filename}, Size: {len(file.read())} bytes")
            return jsonify({"success": True, "message": "File upload working", "filename": file.filename})
        return jsonify({"success": True, "message": "Test endpoint working, no file"})
    except Exception as e:
        print(f"Test endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/test-transcription", methods=["POST"])
def test_transcription():
    """Test transcription with a simple audio file"""
    try:
        if not init_services():
            return jsonify({"error": "Service initialization failed"}), 500

        if "audio" not in request.files:
            return jsonify({"error": "No audio file"}), 400

        file = request.files["audio"]
        file_content = file.read()

        print(f"Test transcription - File: {file.filename}, Size: {len(file_content)} bytes")

        # Create audio buffer
        audio_buffer = BytesIO(file_content)
        audio_buffer.name = file.filename

        # Test transcription
        transcript = app_state["transcription_service"].transcribe_full_file(
            audio_buffer, language_code="hi-IN"
        )

        return jsonify({
            "success": True,
            "transcript": transcript or "No speech detected",
            "file_info": {"name": file.filename, "size": len(file_content)}
        })

    except Exception as e:
        print(f"Test transcription error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/debug", methods=["GET"])
def debug_info():
    """Get debug information about the system"""
    try:
        debug_data = {
            "services_initialized": {
                "transcription": app_state["transcription_service"] is not None,
                "gemini": app_state["gemini_service"] is not None,
                "speech_client": app_state["transcription_service"].speech_client is not None if app_state["transcription_service"] else False,
                "storage_client": app_state["transcription_service"].storage_client is not None if app_state["transcription_service"] else False
            },
            "environment": {
                "gcs_bucket": GCS_BUCKET_NAME,
                "gcp_project": get_gcp_project_id(),
                "gcp_location": GCP_LOCATION
            },
            "dependencies": {
                "soundfile": True,
                "numpy": True,
                "scipy": True
            }
        }
        
        # Check librosa
        try:
            import librosa
            debug_data["dependencies"]["librosa"] = True
        except ImportError:
            debug_data["dependencies"]["librosa"] = False
        
        return jsonify(debug_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/gemini-transcribe", methods=["POST"])
def gemini_transcribe():
    """Fast transcription using Gemini AI (alternative method)"""
    try:
        if not init_services():
            return jsonify({"error": "Service initialization failed"}), 500

        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        file = request.files["audio"]
        if not file.filename:
            return jsonify({"error": "No file selected"}), 400

        # For now, return a message that this is a placeholder
        return jsonify({
            "success": False,
            "message": "Gemini transcription not yet implemented. Use regular transcription.",
            "file_info": {"name": file.filename}
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reset", methods=["POST"])
def reset_session():
    """Reset all session data"""
    global app_state
    # Keep services but reset data
    services_to_keep = {
        "transcription_service": app_state.get("transcription_service"),
        "gemini_service": app_state.get("gemini_service")
    }
    
    app_state = {
        "audio_data": None,
        "sample_rate": None,
        "transcript": None,
        "gemini_result": None,
        "transcription_service": services_to_keep["transcription_service"],
        "gemini_service": services_to_keep["gemini_service"],
        "live_service": None,
        "live_transcript": ""
    }
    return jsonify({"success": True, "message": "Session reset"})


@app.route("/api/process", methods=["POST"])
def process_audio():
    """Upload + Transcribe + Analyze in one go"""
    print("=== Process request received ===")
    try:
        print("Starting process_audio function...")
        print(f"Request method: {request.method}")
        print(f"Request files: {list(request.files.keys())}")
        print(f"Request form: {list(request.form.keys())}")

        # Initialize services first
        print("Initializing services...")
        if not init_services():
            print("Service initialization failed")
            return jsonify({"error": "Service initialization failed"}), 500
        print("✅ Services initialized successfully")

        print("Checking for audio file in request...")
        if "audio" not in request.files:
            print("No audio file in request")
            return jsonify({"error": "No audio file provided"}), 400

        file = request.files["audio"]
        if not file.filename:
            return jsonify({"error": "No file selected"}), 400

        print(f"Processing file: {file.filename}")

        # Read and validate file content
        file_content = file.read()
        print(f"File size: {len(file_content)} bytes")

        if len(file_content) == 0:
            return jsonify({"error": "Empty file uploaded"}), 400

        if len(file_content) < 1000:  # Less than 1KB
            return jsonify({"error": "File too small - may be corrupted or invalid"}), 400

        # Validate file format
        file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else 'unknown'
        supported_formats = ['wav', 'flac', 'mp3']
        
        if file_ext == 'm4a':
            return jsonify({
                "error": "M4A format not supported",
                "details": "Please convert your M4A file to WAV or MP3 format. You can use online converters or audio software."
            }), 400
            
        if file_ext not in supported_formats:
            return jsonify({
                "error": f"Unsupported file format: {file_ext}",
                "details": f"Supported formats: {', '.join(supported_formats)}"
            }), 400

        # Create BytesIO object for transcription
        audio_buffer = BytesIO(file_content)
        audio_buffer.name = file.filename

        # Transcribe with better error handling
        print(f"Starting transcription for {file_ext} file...")
        print(f"Audio buffer size: {len(file_content)} bytes")

        try:
            # Try Hindi first, then English as fallback
            transcript = None
            last_error = None
            
            for lang_code in ["hi-IN", "en-US"]:
                try:
                    print(f"Attempting transcription with {lang_code}...")
                    audio_buffer.seek(0)  # Reset buffer position
                    transcript = app_state["transcription_service"].transcribe_full_file(
                        audio_buffer, language_code=lang_code
                    )
                    if transcript and transcript.strip():
                        print(f"✅ Transcription successful with {lang_code}: {len(transcript)} characters")
                        break
                    else:
                        print(f"❌ No transcript with {lang_code}, trying next language...")
                except Exception as lang_error:
                    print(f"❌ Language {lang_code} failed: {lang_error}")
                    last_error = lang_error
                    continue
            
            if not transcript or not transcript.strip():
                error_details = f"Last error: {last_error}" if last_error else "No speech detected"
                return jsonify({
                    "error": "Transcription failed",
                    "details": error_details
                }), 400
                
        except Exception as transcription_error:
            print(f"Transcription exception: {transcription_error}")
            import traceback
            traceback.print_exc()
            
            error_msg = str(transcription_error)
            if "librosa" in error_msg:
                return jsonify({
                    "error": "MP3 format not supported",
                    "details": "Please convert your MP3 file to WAV format or use a WAV/FLAC file"
                }), 400
            elif "credentials" in error_msg.lower():
                return jsonify({
                    "error": "Google Cloud credentials issue",
                    "details": "Please check server configuration"
                }), 500
            else:
                return jsonify({
                    "error": f"Transcription failed: {error_msg}",
                    "details": "Please try with a different audio file or format"
                }), 500

        # Clean and improve transcript
        cleaned_transcript = _clean_transcript(transcript)
        app_state["transcript"] = cleaned_transcript
        
        print(f"Original transcript: {len(transcript)} chars")
        print(f"Cleaned transcript: {len(cleaned_transcript)} chars")

        # Save transcription to GCS bucket with metadata
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Transcription/transcript_{timestamp}.txt"

            transcription_content = f"""Transcription Details:
Timestamp: {timestamp}
File: {file.filename}
Size: {len(file_content)} bytes

--- TRANSCRIPT ---
{transcript}
--- END TRANSCRIPT ---"""

            bucket = app_state["transcription_service"].storage_client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(filename)
            blob.upload_from_string(
                transcription_content.encode("utf-8"),
                content_type="text/plain; charset=utf-8"
            )
            print(f"Transcription saved to GCS: {filename}")
        except Exception as e:
            print(f"Failed to save transcription to GCS: {e}")

        # Analyze with Gemini
        print("🤖 Starting enhanced AI analysis...")
        try:
            schema = get_default_schema()
            schema_json = json.dumps(schema, indent=2)
            
            print(f"📝 Analyzing transcript: {len(cleaned_transcript)} characters")
            print(f"🎯 Target schema fields: {len(schema_json.split('""'))} fields")

            result = app_state["gemini_service"].generate_json_payload(schema_json, cleaned_transcript)

            if not result:
                print("❌ Primary analysis failed, trying simplified extraction...")
                # Try with simpler prompt
                result = app_state["gemini_service"]._fallback_extraction(cleaned_transcript, schema_json)
                
            if not result:
                return jsonify({
                    "error": "AI analysis failed", 
                    "details": "Could not extract data from transcript. Please check audio quality."
                }), 500

            app_state["gemini_result"] = result
            print(f"✅ Analysis complete - extracted data for farmer survey")

            # Save analysis result to GCS
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"Transcription/analysis_{timestamp}.json"

                analysis_with_metadata = {
                    "metadata": {
                        "timestamp": timestamp,
                        "original_file": file.filename,
                        "transcript_length": len(transcript)
                    },
                    "transcript": transcript,
                    "analysis": result
                }

                bucket = app_state["transcription_service"].storage_client.bucket(GCS_BUCKET_NAME)
                blob = bucket.blob(filename)
                blob.upload_from_string(
                    json.dumps(analysis_with_metadata, indent=2, ensure_ascii=False).encode("utf-8"),
                    content_type="application/json; charset=utf-8"
                )
                print(f"Analysis result saved to GCS: {filename}")
            except Exception as e:
                print(f"Failed to save analysis to GCS: {e}")

            print("🎉 Process completed successfully!")
            
            # Validate result quality
            filled_count = _count_non_empty_fields(result)
            total_fields = _count_total_fields(get_default_schema())
            completion_rate = (filled_count / total_fields) * 100 if total_fields > 0 else 0
            
            print(f"📊 Data completion: {filled_count}/{total_fields} fields ({completion_rate:.1f}%)")
            
            return jsonify({
                "success": True, 
                "transcript": cleaned_transcript, 
                "result": result,
                "stats": {
                    "filled_fields": filled_count,
                    "total_fields": total_fields,
                    "completion_rate": f"{completion_rate:.1f}%"
                }
            })
            
        except Exception as analysis_error:
            print(f"Analysis error: {analysis_error}")
            return jsonify({
                "error": f"AI analysis failed: {str(analysis_error)}",
                "details": "The transcript was generated but AI analysis failed"
            }), 500

    except Exception as e:
        print(f"CRITICAL ERROR in process_audio: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

        error_msg = str(e)
        if "timeout" in error_msg.lower():
            return jsonify({
                "error": "Request timeout",
                "details": "The file is too large or processing took too long. Try a smaller file."
            }), 408
        elif "memory" in error_msg.lower():
            return jsonify({
                "error": "Memory error", 
                "details": "File too large for processing. Please use a smaller audio file."
            }), 413
        else:
            return jsonify({
                "error": f"Processing failed: {error_msg}",
                "error_type": type(e).__name__,
                "details": "Please try again with a different file or check server logs"
            }), 500


@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    try:
        print("=== Transcribe request ===")

        if app_state["audio_data"] is None:
            return jsonify({"error": "No audio data"}), 400

        # Create file-like object
        audio_file = BytesIO()
        sf.write(
            audio_file, app_state["audio_data"], app_state["sample_rate"], format="WAV"
        )
        audio_file.seek(0)
        audio_file.name = "audio.wav"

        # Transcribe
        transcript = app_state["transcription_service"].transcribe_full_file(
            audio_file, language_code="hi-IN"
        )

        if transcript:
            app_state["transcript"] = transcript
            print(f"Transcript: {len(transcript)} chars")

            return jsonify(
                {
                    "success": True,
                    "transcript": transcript,
                    "word_count": len(transcript.split()),
                }
            )

        return jsonify({"error": "Transcription failed"}), 500

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        print("=== Analyze request ===")

        data = request.json
        transcript = data.get("transcript") or app_state["transcript"]

        if not transcript:
            return jsonify({"error": "No transcript"}), 400

        # Update transcript if edited
        app_state["transcript"] = transcript

        # Get schema
        schema = get_default_schema()
        schema_json = json.dumps(schema, indent=2)

        # Generate payload
        result = app_state["gemini_service"].generate_json_payload(
            schema_json, transcript
        )

        if result:
            app_state["gemini_result"] = result
            print("Analysis complete")
            return jsonify({"success": True, "result": result})

        return jsonify({"error": "Analysis failed"}), 500

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/download/<file_type>", methods=["GET"])
def download_file(file_type):
    try:
        if file_type == "transcript":
            transcript = app_state["transcript"]
            if not transcript:
                return jsonify({"error": "No transcript found"}), 404

            buffer = BytesIO(transcript.encode("utf-8"))
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype="text/plain",
                as_attachment=True,
                download_name="transcript.txt",
            )

        elif file_type == "json":
            result = app_state["gemini_result"]
            if not result:
                return jsonify({"error": "No analysis result found"}), 404

            buffer = BytesIO(
                json.dumps(result, indent=2, ensure_ascii=False).encode("utf-8")
            )
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype="application/json",
                as_attachment=True,
                download_name="survey_data.json",
            )

        elif file_type == "audio":
            audio_data = app_state["audio_data"]
            sample_rate = app_state["sample_rate"]

            if audio_data is None:
                return jsonify({"error": "No audio data found"}), 404

            buffer = BytesIO()
            sf.write(buffer, audio_data, sample_rate, format="WAV")
            buffer.seek(0)

            return send_file(
                buffer,
                mimetype="audio/wav",
                as_attachment=True,
                download_name="recording.wav",
            )

        return jsonify({"error": "Invalid file type"}), 400

    except Exception as e:
        print(f"Download error: {e}")
        return jsonify({"error": str(e)}), 500


# WebSocket handlers for live transcription
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'status': 'ready', 'sid': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    if app_state.get('live_service'):
        try:
            app_state['live_service'].stop_streaming()
        except:
            pass

@socketio.on('start_stream')
def handle_start_stream():
    try:
        print('Starting live transcription stream')
        
        if not init_services():
            print('Failed to initialize services')
            socketio.emit('error', {'message': 'Failed to initialize services'})
            return
        
        app_state['live_transcript'] = ''
        app_state['live_service'] = LiveTranscriptionService()
        
        def on_transcript(text, is_final):
            if is_final:
                app_state['live_transcript'] += text + ' '
                print(f'Final: {text}')
                socketio.emit('transcript_update', {
                    'transcript': text,
                    'is_final': True,
                    'full_transcript': app_state['live_transcript']
                })
            else:
                socketio.emit('transcript_update', {
                    'transcript': text,
                    'is_final': False
                })
        
        app_state['live_service'].start_streaming(on_transcript, language_code='hi-IN')
        socketio.emit('stream_started', {'status': 'streaming'})
        
    except Exception as e:
        print(f'Error in start_stream: {e}')
        socketio.emit('error', {'message': f'Failed to start stream: {str(e)}'})

@socketio.on('audio_data')
def handle_audio_data(data):
    try:
        audio_bytes = base64.b64decode(data['audio'])
        if app_state['live_service']:
            app_state['live_service'].add_audio_chunk(audio_bytes)
    except Exception as e:
        print(f'Streaming error: {e}')
        socketio.emit('error', {'message': str(e)})

@socketio.on('stop_stream')
def handle_stop_stream():
    try:
        if app_state['live_service']:
            app_state['live_service'].stop_streaming()
        
        transcript = app_state['live_transcript'].strip()
        if not transcript:
            socketio.emit('error', {'message': 'No transcript generated'})
            return
        
        app_state['transcript'] = transcript
        
        # Save live transcript to GCS
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'Transcription/live_transcript_{timestamp}.txt'
            
            content = f"""Live Transcription:
Timestamp: {timestamp}
Language: Hindi (hi-IN)

--- TRANSCRIPT ---
{transcript}
--- END TRANSCRIPT ---"""
            
            bucket = app_state['transcription_service'].storage_client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(filename)
            blob.upload_from_string(content.encode('utf-8'), content_type='text/plain; charset=utf-8')
            print(f'Live transcript saved: {filename}')
        except Exception as e:
            print(f'Failed to save live transcript: {e}')
        
        # Analyze with Gemini
        schema = get_default_schema()
        result = app_state['gemini_service'].generate_json_payload(json.dumps(schema, indent=2), transcript)
        
        if result:
            app_state['gemini_result'] = result
            socketio.emit('analysis_complete', {'transcript': transcript, 'result': result})
        else:
            socketio.emit('error', {'message': 'Analysis failed'})
            
    except Exception as e:
        print(f'Stop stream error: {e}')
        socketio.emit('error', {'message': str(e)})

if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    print("Starting Singaji Setu Agent Backend...")
    print("Initializing services on startup...")
    
    if init_services():
        print("✅ Services initialized successfully")
    else:
        print("❌ Service initialization failed - check configuration")
    
    print("🚀 Server starting on http://localhost:5000")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
