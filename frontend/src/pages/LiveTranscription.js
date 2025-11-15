import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import io from 'socket.io-client';

const LiveTranscription = ({ updateSessionData }) => {
  const navigate = useNavigate();
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  
  const socketRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    // Create socket connection only once
    if (!socketRef.current) {
      console.log('🔌 Creating socket connection...');
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      socketRef.current = io(API_URL, {
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: 10,
        timeout: 60000,
        forceNew: true,
        upgrade: true,
        rememberUpgrade: false
      });
      
      socketRef.current.on('connect', () => {
        console.log('✅ Connected to server');
        setError(null);
      });
      
      socketRef.current.on('connected', (data) => {
        console.log('✅ Server ready:', data);
      });

      socketRef.current.on('stream_started', () => {
        console.log('🎙️ Stream started');
      });

      socketRef.current.on('transcript_update', (data) => {
        if (data.is_final) {
          setTranscript(data.full_transcript);
          setInterimTranscript('');
        } else {
          setInterimTranscript(data.transcript);
        }
      });

      socketRef.current.on('analysis_complete', (data) => {
        console.log('✅ Analysis complete received:', data);
        
        // Store in sessionStorage for reliability
        sessionStorage.setItem('transcript', data.transcript);
        sessionStorage.setItem('gemini_result', JSON.stringify(data.result));
        
        updateSessionData({
          transcript: data.transcript,
          gemini_result: data.result
        });
        
        setAnalyzing(false);
        
        // Go directly to results without popup
        navigate('/results');
      });

      socketRef.current.on('error', (data) => {
        console.error('❌ Error received:', data);
        setError(data.message);
        setAnalyzing(false);
      });

      socketRef.current.on('disconnect', (reason) => {
        console.log('⚠️ Socket disconnected:', reason);
        if (reason === 'io server disconnect') {
          socketRef.current.connect();
        }
      });

      socketRef.current.on('reconnect', (attemptNumber) => {
        console.log('🔄 Socket reconnected after', attemptNumber, 'attempts');
        setError(null);
      });
      
      socketRef.current.on('connect_error', (error) => {
        console.error('❌ Connection error:', error);
        setError('Connection failed. Retrying...');
      });
    }

    return () => {
      // Don't disconnect on unmount, keep connection alive
      console.log('Component unmounting, keeping socket alive');
    };
  }, [navigate, updateSessionData]);

  const startRecording = async () => {
    try {
      // Get microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000
        } 
      });
      
      streamRef.current = stream;
      
      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      
      // Start streaming to backend
      socketRef.current.emit('start_stream');
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          // Convert to base64 and send
          const reader = new FileReader();
          reader.onloadend = () => {
            const base64 = reader.result.split(',')[1];
            socketRef.current.emit('audio_data', { audio: base64 });
          };
          reader.readAsDataURL(event.data);
        }
      };
      
      // Send audio chunks every 250ms
      mediaRecorder.start(250);
      
      setIsRecording(true);
      setTranscript('');
      setInterimTranscript('');
      setError(null);
      
    } catch (err) {
      setError('Microphone error: ' + err.message);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      
      setIsRecording(false);
      setAnalyzing(true);
      
      // Tell backend to stop and analyze
      socketRef.current.emit('stop_stream');
    }
  };

  return (
    <div className="live-transcription">
      <h2>🎙️ Live Interview Transcription</h2>
      
      <div className="info-box green">
        <p><strong>✅ Real-Time GCP Transcription</strong></p>
        <p>Audio streams to backend → Google Cloud transcribes live → AI analyzes</p>
        <p>Works for Hindi & English - Production ready!</p>
      </div>

      {/* Live Transcript Display - Always Visible */}
      <div className="transcript-display">
        <h3>📝 Live Transcript</h3>
        <div className="transcript-box">
          {!transcript && !interimTranscript && !isRecording && (
            <p className="placeholder-text">Click "Start Live Recording" to begin...</p>
          )}
          {!transcript && !interimTranscript && isRecording && (
            <p className="placeholder-text">🎙️ Listening... Start speaking!</p>
          )}
          <p className="final-text">{transcript}</p>
          <p className="interim-text">{interimTranscript}</p>
        </div>
        {(transcript || interimTranscript) && (
          <div className="stats">
            <span>📝 Words: {transcript.split(' ').filter(w => w).length}</span>
            <span>🔤 Characters: {transcript.length}</span>
          </div>
        )}
      </div>

      {/* Recording Controls */}
      <div className="recording-controls">
        {!isRecording && !analyzing && (
          <button className="primary-btn start-btn" onClick={startRecording}>
            🎤 Start Live Recording
          </button>
        )}
        
        {isRecording && (
          <div className="recording-active">
            <div className="pulse-indicator">🔴 Recording...</div>
            <button className="primary-btn stop-btn" onClick={stopRecording}>
              ⏹️ Stop & Analyze
            </button>
          </div>
        )}

        {analyzing && (
          <div className="analyzing">
            <div className="spinner"></div>
            <p>Analyzing interview with AI...</p>
          </div>
        )}
      </div>

      {error && <div className="error-box">{error}</div>}



      <style jsx>{`
        .live-transcription {
          max-width: 900px;
          margin: 0 auto;
          padding: 20px;
        }

        .recording-controls {
          text-align: center;
          margin: 30px 0;
        }

        .start-btn {
          background: #10b981;
          font-size: 1.2em;
          padding: 15px 40px;
        }

        .recording-active {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 20px;
        }

        .pulse-indicator {
          font-size: 1.5em;
          animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        .stop-btn {
          background: #ef4444;
        }

        .analyzing {
          text-align: center;
        }

        .spinner {
          border: 4px solid #f3f3f3;
          border-top: 4px solid #3b82f6;
          border-radius: 50%;
          width: 40px;
          height: 40px;
          animation: spin 1s linear infinite;
          margin: 0 auto 10px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .transcript-display {
          margin: 30px 0;
          order: -1;
        }

        .transcript-box {
          background: #f9fafb;
          border: 2px solid #3b82f6;
          border-radius: 12px;
          padding: 25px;
          min-height: 400px;
          max-height: 600px;
          overflow-y: auto;
          overflow-x: hidden;
          font-size: 1.2em;
          line-height: 1.8;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
          word-wrap: break-word;
          white-space: pre-wrap;
        }

        .placeholder-text {
          color: #9ca3af;
          text-align: center;
          font-style: italic;
          margin: 150px 0;
        }

        .final-text {
          color: #1f2937;
          margin: 0;
          word-wrap: break-word;
          white-space: pre-wrap;
        }

        .interim-text {
          color: #6b7280;
          font-style: italic;
          margin: 0;
          word-wrap: break-word;
          white-space: pre-wrap;
        }

        .stats {
          display: flex;
          gap: 20px;
          margin-top: 10px;
          font-size: 0.9em;
          color: #6b7280;
        }


      `}</style>
    </div>
  );
};

export default LiveTranscription;
