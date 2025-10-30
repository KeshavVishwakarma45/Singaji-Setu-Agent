import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const AudioInput = ({ workflowType, onComplete, updateSessionData }) => {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [audioURL, setAudioURL] = useState(null);
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Try to use WAV format if supported
      const options = { mimeType: 'audio/webm' };
      mediaRecorderRef.current = new MediaRecorder(stream, options);
      chunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(blob);
        setAudioURL(url);
        setFile(blob);
      };

      mediaRecorderRef.current.start();
      setRecording(true);
    } catch (err) {
      setError('Microphone access denied');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setRecording(false);
    }
  };

  const handleFileUpload = (e) => {
    const uploadedFile = e.target.files[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      setAudioURL(URL.createObjectURL(uploadedFile));
    }
  };

  const handleSubmit = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    // For recorded audio (blob), create proper file
    if (file instanceof Blob && !file.name) {
      formData.append('audio', file, 'recording.webm');
    } else {
      formData.append('audio', file);
    }

    try {
      const res = await api.post('/api/process', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (res.data.success) {
        updateSessionData({ 
          transcript: res.data.transcript,
          gemini_result: res.data.result
        });
        // Skip to results directly
        navigate('/results');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Processing failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="audio-input">
      <h2>Step 2: Provide Audio Input</h2>

      {workflowType === 'live' ? (
        <div className="live-recorder">
          <div className="info-box orange">
            <p><strong>⚠️ Live recording not supported in browser</strong></p>
            <p>Please use file upload instead (record on phone/computer first)</p>
          </div>
          <button className="primary-btn" onClick={() => navigate('/')}>
            ⬅️ Go Back
          </button>
        </div>
      ) : (
        <div className="file-uploader">
          <div className="format-info">
            <div className="info-box green">
              <p><strong>✅ Recommended Formats</strong></p>
              <p>WAV, FLAC for best quality</p>
            </div>
            <div className="info-box orange">
              <p><strong>⚠️ Note</strong></p>
              <p>M4A files need conversion first</p>
            </div>
          </div>

          <input 
            type="file" 
            accept="audio/*"
            onChange={handleFileUpload}
            className="file-input"
          />

          {audioURL && (
            <div className="audio-preview">
              <h4>🎵 Uploaded Audio Preview</h4>
              <audio controls src={audioURL} />
              <button 
                className="primary-btn" 
                onClick={handleSubmit}
                disabled={loading}
              >
                {loading ? 'Processing...' : 'Process and Continue ➡️'}
              </button>
            </div>
          )}
        </div>
      )}

      {error && <div className="error-box">{error}</div>}
    </div>
  );
};

export default AudioInput;
