@echo off
echo ========================================
echo   ISL Connect - Complete Startup
echo ========================================
echo.
echo Starting all services...
echo.

echo [1/3] Starting Sign Detection Service (Background)...
start "Sign Service" cmd /k "cd /d %~dp0 && python sign_service.py"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Backend (Port 3002)...
start "Backend" cmd /k "cd /d %~dp0 && python app.py"
timeout /t 3 /nobreak >nul

echo [3/3] Starting Frontend (Port 3001)...
start "Frontend" cmd /k "cd /d %~dp0 && npm start"

echo.
echo ========================================
echo   All Services Started!
echo ========================================
echo.
echo Sign Service: http://localhost:5001
echo Backend:      http://localhost:3002
echo Frontend:     http://localhost:3001
echo.
echo Press any key to exit...
pause >nul
