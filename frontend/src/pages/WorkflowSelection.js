import React from 'react';
import { useNavigate } from 'react-router-dom';

const WorkflowSelection = ({ onSelect }) => {
  const navigate = useNavigate();

  const handleSelect = (type) => {
    onSelect(type);
    if (type === 'live') {
      navigate('/live');
    } else {
      navigate('/input');
    }
  };

  return (
    <div className="workflow-selection">
      <h2>🎯 Step 1: Choose Your Audio Source</h2>
      <p className="subtitle">Select how you want to provide the farmer interview audio</p>
      
      <div className="workflow-cards">
        <div className="workflow-card green">
          <div className="card-icon">🎙️</div>
          <h3>Live Recording</h3>
          <p>Record directly in browser</p>
          <button 
            className="primary-btn"
            onClick={() => handleSelect('live')}
          >
            Start Recording
          </button>
        </div>

        <div className="workflow-card blue">
          <div className="card-icon">📁</div>
          <h3>Upload File</h3>
          <p>Upload existing audio file</p>
          <button 
            className="primary-btn"
            onClick={() => handleSelect('upload')}
          >
            Upload Audio
          </button>
        </div>
      </div>
    </div>
  );
};

export default WorkflowSelection;
