@echo off
echo Installing Sign Language Recognition Dependencies...
echo.

echo Step 1: Installing core packages...
pip install opencv-python
pip install numpy==1.26.4
pip install tensorflow==2.16.1

echo.
echo Step 2: Installing MediaPipe...
pip install mediapipe==0.10.14

echo.
echo Step 3: Installing additional packages...
pip install pyttsx3
pip install pillow
pip install pyenchant

echo.
echo Step 4: Cleaning up conflicts...
pip uninstall jax jaxlib -y

echo.
echo Installation complete!
echo.
echo To run the application, use:
echo python final_pred.py
echo.
pause