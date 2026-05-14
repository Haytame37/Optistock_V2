@echo off
echo ========================================
echo  OptiStock Solutions - Backend API
echo ========================================
echo.

REM Install dependencies
pip install -r requirements.txt

REM Initialize database
python database\init_db.py

REM Run FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
