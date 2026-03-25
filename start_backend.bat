@echo off
echo =========================================
echo Starting TruthLens API Settings Locally
echo =========================================
set USE_SQLITE=True
python -m uvicorn main:app --reload --port 8000
