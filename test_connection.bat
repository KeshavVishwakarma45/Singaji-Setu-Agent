@echo off
echo Testing Singaji Setu Agent Connection...
echo.

echo 1. Testing Backend Health Check...
curl -s http://localhost:5000/api/health
if %errorlevel% neq 0 (
    echo ❌ Backend not responding on port 5000
    echo Make sure backend is running: cd backend && python app.py
) else (
    echo ✅ Backend is running
)

echo.
echo 2. Testing Frontend...
curl -s http://localhost:3000 > nul
if %errorlevel% neq 0 (
    echo ❌ Frontend not responding on port 3000
    echo Make sure frontend is running: cd frontend && npm start
) else (
    echo ✅ Frontend is running
)

echo.
echo 3. Connection Summary:
echo Backend should be at: http://localhost:5000
echo Frontend should be at: http://localhost:3000
echo.
pause