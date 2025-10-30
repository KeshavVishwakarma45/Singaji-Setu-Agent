import React from 'react';

const Sidebar = ({ currentStep, completedSteps = [], onReset }) => {
  const steps = [
    { id: 'workflow', name: '1. Audio Source' },
    { id: 'input', name: '2. Record / Upload' },
    { id: 'transcribe', name: '3. Transcribe' },
    { id: 'analyze', name: '4. Analyze' },
    { id: 'export', name: '5. Export' }
  ];


  
  return (
    <div className="sidebar">
      <div className="steps-container">
        {steps.map((step, index) => {
          const isCompleted = completedSteps.includes(step.id);
          const isCurrent = step.id === currentStep;
          
          return (
            <div key={step.id} className="step-item">
              {isCompleted && <span>☑️ {step.name}</span>}
              {isCurrent && !isCompleted && <span>➡️ <strong>{step.name}</strong></span>}
              {!isCurrent && !isCompleted && <span>⏳ <em>{step.name}</em></span>}
            </div>
          );
        })}
      </div>
      
      <button className="reset-btn" onClick={onReset}>
        🔄 Start Over
      </button>
    </div>
  );
};

export default Sidebar;
