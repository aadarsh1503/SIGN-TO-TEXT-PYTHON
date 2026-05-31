@echo off
echo ========================================
echo   Starting ISSL Connect Full Application
echo ========================================
echo.

echo Step 1: Installing Sign Recognition API requirements...
pip install -r sign_requirements.txt

echo.
echo Step 2: Starting Sign Recognition API (Port 5001)...
start "Sign Recognition API" cmd /k "python sign_recognition_api.py"

echo.
echo Step 3: Waiting for API to start...
timeout /t 5

echo.
echo Step 4: Starting React Frontend (Port 3000)...
start "React Frontend" cmd /k "npm start"

echo.
echo Step 5: Starting Main Backend (Port 5000)...
start "Main Backend" cmd /k "python app.py"

echo.
echo ========================================
echo All services started!
echo.
echo Frontend: http://localhost:3000
echo Main Backend: http://localhost:5000  
echo Sign API: http://localhost:5001
echo ========================================
pause