@echo off
echo ========================================
echo   Sign Language - Anaconda Fix Script
echo ========================================
echo.

echo Step 1: Cleaning up existing installations...
pip uninstall tensorflow tensorflow-intel keras jax jaxlib -y
conda remove tensorflow keras -y

echo.
echo Step 2: Creating new conda environment...
conda create -n signlang python=3.9 -y

echo.
echo Step 3: Activating environment...
call conda activate signlang

echo.
echo Step 4: Installing packages...
pip install opencv-python==4.8.1.78
pip install numpy==1.26.4
pip install tensorflow==2.16.1
pip install keras==3.0.5
pip install mediapipe==0.10.14
pip install pyttsx3==2.90
pip install pillow==10.0.0
pip install pyenchant==3.2.2

echo.
echo Step 5: Testing installation...
python -c "import cv2, numpy, tensorflow, keras, mediapipe; print('All packages installed successfully!')"

echo.
echo ========================================
echo Installation Complete!
echo.
echo To run the application:
echo 1. conda activate signlang
echo 2. python final_pred.py
echo ========================================
pause