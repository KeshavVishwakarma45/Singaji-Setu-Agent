@echo off
cd backend
echo Activating virtual environment...
call venv\Scripts\activate
echo Starting backend server...
python app.py
pause