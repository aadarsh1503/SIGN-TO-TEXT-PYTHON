@echo off
echo ========================================
echo   Installing EXACT Working Versions
echo   (Same as working system)
echo ========================================
echo.

echo Step 1: Complete cleanup...
pip uninstall tensorflow tensorflow-intel keras tf-keras -y
pip uninstall opencv-python opencv-contrib-python -y
pip uninstall mediapipe numpy -y
conda remove tensorflow keras opencv numpy mediapipe -y

echo.
echo Step 2: Installing EXACT working versions...
pip install numpy==1.26.4
pip install tensorflow==2.16.1
pip install tensorflow-intel==2.16.1
pip install keras==3.14.1
pip install opencv-python==4.9.0.80
pip install opencv-contrib-python==4.13.0.92
pip install mediapipe==0.10.14

echo.
echo Step 3: Installing other packages...
pip install pyttsx3==2.90
pip install pillow==10.0.0
pip install pyenchant==3.2.2

echo.
echo Step 4: Fixing conflicts...
pip uninstall jax jaxlib -y

echo.
echo Step 5: Testing installation...
python -c "import tensorflow as tf; print('TensorFlow:', tf.__version__)"
python -c "import keras; print('Keras:', keras.__version__)"
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import mediapipe as mp; print('MediaPipe: OK')"
python -c "import numpy as np; print('NumPy:', np.__version__)"

echo.
echo ========================================
echo Installation Complete!
echo Same versions as working system installed
echo ========================================
pause