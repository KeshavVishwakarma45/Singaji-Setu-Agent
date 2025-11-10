@echo off
echo Starting Singaji Setu Agent...
echo.

echo Starting Backend Server...
cd backend
start "Backend" cmd /k "venv\Scripts\activate && python app.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
cd ..\frontend
start "Frontend" cmd /k "npm start"

echo.
echo Both servers are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
pause