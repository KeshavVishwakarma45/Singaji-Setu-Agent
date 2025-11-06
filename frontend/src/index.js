import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/App.css';
import App from './App';
import ErrorBoundary from './components/ErrorBoundary';

try {
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(
    <React.StrictMode>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </React.StrictMode>
  );
} catch (error) {
  console.error('Failed to render app:', error);
  document.getElementById('root').innerHTML = `
    <div style="padding: 20px; text-align: center;">
      <h1>🌾 Singaji Setu AGENT</h1>
      <p>Loading failed. Error: ${error.message}</p>
      <button onclick="window.location.reload()">Reload</button>
    </div>
  `;
}
