#!/bin/bash
echo "========================================"
echo " OptiStock Solutions - Backend API"
echo "========================================"

pip install -r requirements.txt
python database/init_db.py
uvicorn main:app --reload --host 0.0.0.0 --port 8000
