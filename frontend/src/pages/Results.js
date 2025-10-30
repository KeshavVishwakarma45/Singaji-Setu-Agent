import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Results = ({ sessionData }) => {
  const [activeTab, setActiveTab] = useState('json');
  const [result, setResult] = useState(null);

  useEffect(() => {
    // Try sessionData first, then sessionStorage as backup
    if (sessionData.gemini_result) {
      setResult(sessionData.gemini_result);
    } else {
      // Fallback to sessionStorage
      const storedResult = sessionStorage.getItem('gemini_result');
      if (storedResult) {
        try {
          setResult(JSON.parse(storedResult));
        } catch (e) {
          console.error('Failed to parse stored result:', e);
        }
      }
    }
  }, [sessionData]);

  const handleDownload = async (fileType) => {
    try {
      const res = await api.get(`/api/download/${fileType}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      
      const extensions = { transcript: 'txt', json: 'json', audio: 'wav' };
      link.setAttribute('download', `${fileType}_${Date.now()}.${extensions[fileType]}`);
      
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  if (!result) {
    return <div className="loading-container">Loading results...</div>;
  }

  const farmerName = result.farmerDetails?.farmerName || 'N/A';
  const summary = result.interviewMetadata?.summary || 'No summary available';

  return (
    <div className="results">
      <h2>🎉 Step 5: Complete!</h2>

      <div className="success-box">
        <h3>✅ Processing Complete!</h3>
        <p>Your farmer interview has been fully processed. All data is ready for download.</p>
      </div>

      <div className="summary-box">
        <h4>📋 Summary for: {farmerName}</h4>
        <p>{summary}</p>
      </div>

      <div className="tabs">
        <button 
          className={activeTab === 'json' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('json')}
        >
          📊 Survey Data (JSON)
        </button>
        <button 
          className={activeTab === 'transcript' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('transcript')}
        >
          📄 Transcript
        </button>
        <button 
          className={activeTab === 'audio' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('audio')}
        >
          🎵 Audio
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'json' && (
          <div>
            <pre className="json-display">
              {JSON.stringify(result, null, 2)}
            </pre>
            <button 
              className="download-btn"
              onClick={() => handleDownload('json')}
            >
              📥 Download JSON
            </button>
          </div>
        )}

        {activeTab === 'transcript' && (
          <div>
            <pre className="transcript-display">
              {sessionData.transcript || sessionStorage.getItem('transcript') || 'No transcript available'}
            </pre>
            <button 
              className="download-btn"
              onClick={() => handleDownload('transcript')}
            >
              📄 Download Transcript
            </button>
          </div>
        )}

        {activeTab === 'audio' && (
          <div>
            <p>Audio file is available for download</p>
            <button 
              className="download-btn"
              onClick={() => handleDownload('audio')}
            >
              🎵 Download Audio
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Results;
