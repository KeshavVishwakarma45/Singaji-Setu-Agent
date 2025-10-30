import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const Transcription = ({ onComplete, updateSessionData }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleTranscribe = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await api.post('/api/transcribe');
      
      if (res.data.success) {
        updateSessionData({ 
          transcript: res.data.transcript,
          word_count: res.data.word_count
        });
        onComplete();
        navigate('/analyze');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Transcription failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="transcription">
      <h2>📝 Step 3: Review Transcription</h2>

      <div className="info-box blue">
        <p><strong>✅ Audio is ready for transcription</strong></p>
        <p>This may take a few minutes for long recordings</p>
      </div>

      <button 
        className="primary-btn large"
        onClick={handleTranscribe}
        disabled={loading}
      >
        {loading ? '🤖 Transcribing... Please wait' : '🎙️ Start Transcription'}
      </button>

      {loading && (
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Processing audio... This may take a few minutes</p>
        </div>
      )}

      {error && <div className="error-box">{error}</div>}
    </div>
  );
};

export default Transcription;
