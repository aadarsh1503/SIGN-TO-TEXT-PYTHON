@echo off
echo Starting Sign Recognition API...
echo.

echo Installing requirements...
pip install -r sign_requirements.txt

echo.
echo Starting Flask API on port 5001...
python sign_recognition_api.py

pause