import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const Analysis = ({ sessionData, onComplete, updateSessionData }) => {
  const navigate = useNavigate();
  const [transcript, setTranscript] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (sessionData.transcript) {
      setTranscript(sessionData.transcript);
    }
  }, [sessionData]);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await api.post('/api/analyze', {
        transcript: transcript
      });

      if (res.data.success) {
        updateSessionData({ gemini_result: res.data.result });
        onComplete();
        navigate('/results');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="analysis">
      <h2>🤖 Step 4: AI Analysis</h2>

      <div className="info-box orange">
        <p><strong>📝 Review & Edit Transcript</strong></p>
        <p>Edit if necessary before running AI analysis</p>
      </div>

      <textarea
        className="transcript-editor"
        value={transcript}
        onChange={(e) => setTranscript(e.target.value)}
        rows={15}
        placeholder="Transcript will appear here..."
      />

      <button 
        className="primary-btn large"
        onClick={handleAnalyze}
        disabled={loading || !transcript}
      >
        {loading ? '🧠 Analyzing... Please wait' : '🚀 Generate Survey Data'}
      </button>

      {loading && (
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>AI is analyzing the transcript...</p>
        </div>
      )}

      {error && <div className="error-box">{error}</div>}
    </div>
  );
};

export default Analysis;
