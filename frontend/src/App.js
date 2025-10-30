import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import WorkflowSelection from './pages/WorkflowSelection';
import AudioInput from './pages/AudioInput';
import LiveTranscription from './pages/LiveTranscription';
import Transcription from './pages/Transcription';
import Analysis from './pages/Analysis';
import Results from './pages/Results';
import Sidebar from './components/Sidebar';
import api from './services/api';

function AppContent() {
  const location = useLocation();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState('workflow');
  const [workflowType, setWorkflowType] = useState(null);
  const [sessionData, setSessionData] = useState({});

  // Update currentStep and completedSteps based on route
  useEffect(() => {
    const path = location.pathname;
    if (path === '/' || path === '/workflow') {
      setCurrentStep('workflow');
    } else if (path === '/input') {
      setCurrentStep('input');
    } else if (path === '/live') {
      setCurrentStep('input');
    } else if (path === '/transcribe') {
      setCurrentStep('transcribe');
    } else if (path === '/analyze') {
      setCurrentStep('analyze');
    } else if (path === '/results') {
      setCurrentStep('export');
    }
  }, [location.pathname]);

  // Calculate completed steps based on current route
  const getCompletedSteps = () => {
    const path = location.pathname;
    if (path === '/input' || path === '/live') return ['workflow'];
    if (path === '/transcribe') return ['workflow', 'input'];
    if (path === '/analyze') return ['workflow', 'input', 'transcribe'];
    if (path === '/results') return ['workflow', 'input', 'transcribe', 'analyze'];
    return [];
  };

  const updateSessionData = (data) => {
    setSessionData(prev => ({ ...prev, ...data }));
  };

  const handleReset = async () => {
    try {
      await api.post('/api/reset');
    } catch (error) {
      console.error('Reset failed:', error);
    }
    // Force complete reload
    sessionStorage.clear();
    localStorage.clear();
    window.location.href = '/';
  };

  return (
      <div className="app-container">
        <header className="app-header">
          <h1>🌾 Singaji Setu AGENT</h1>
          <p>Intelligent processing of farmer interview surveys from audio recordings</p>
        </header>
        
        <div className="main-content">
          <Sidebar currentStep={currentStep} completedSteps={getCompletedSteps()} onReset={handleReset} />
          
          <div className="content-area">
            <Routes>
              <Route 
                path="/" 
                element={
                  <WorkflowSelection 
                    onSelect={(type) => {
                      setWorkflowType(type);
                      setCurrentStep('input');
                    }} 
                  />
                } 
              />
              <Route 
                path="/input" 
                element={
                  <AudioInput 
                    workflowType={workflowType}
                    onComplete={() => setCurrentStep('transcribe')}
                    updateSessionData={updateSessionData}
                  />
                } 
              />
              <Route 
                path="/live" 
                element={
                  <LiveTranscription 
                    updateSessionData={updateSessionData}
                  />
                } 
              />
              <Route 
                path="/transcribe" 
                element={
                  <Transcription 
                    onComplete={() => setCurrentStep('analyze')}
                    updateSessionData={updateSessionData}
                  />
                } 
              />
              <Route 
                path="/analyze" 
                element={
                  <Analysis 
                    sessionData={sessionData}
                    onComplete={() => setCurrentStep('export')}
                    updateSessionData={updateSessionData}
                  />
                } 
              />
              <Route 
                path="/results" 
                element={
                  <Results 
                    sessionData={sessionData}
                  />
                } 
              />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </div>
        </div>
      </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
