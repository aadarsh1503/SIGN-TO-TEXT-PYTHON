@echo off
echo ========================================
echo   TensorFlow tf2xla Error Fix
echo ========================================
echo.

echo Step 1: Complete cleanup...
pip uninstall tensorflow tensorflow-intel keras tf-keras -y
conda remove tensorflow keras -y

echo.
echo Step 2: Installing compatible versions...
pip install tensorflow==2.15.0
pip install keras==2.15.0

echo.
echo Step 3: Installing other packages...
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install mediapipe==0.10.9
pip install pyttsx3==2.90
pip install pillow==10.0.0
pip install pyenchant==3.2.2

echo.
echo Step 4: Testing installation...
python -c "import tensorflow as tf; print('TensorFlow version:', tf.__version__)"
python -c "import keras; print('Keras version:', keras.__version__)"

echo.
echo ========================================
echo If still error, try CPU-only version:
echo pip install tensorflow-cpu==2.15.0
echo ========================================
pause