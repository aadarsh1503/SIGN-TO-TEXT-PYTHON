@echo off
echo ========================================
echo   Fixing NumPy Version Conflict
echo ========================================
echo.

echo Step 1: Fixing NumPy version...
pip install "numpy<2" --force-reinstall
pip install numpy==1.26.4 --force-reinstall

echo.
echo Step 2: Reinstalling TensorFlow with correct NumPy...
pip install tensorflow==2.16.1 --force-reinstall
pip install keras==3.14.1 --force-reinstall

echo.
echo Step 3: Testing versions...
python -c "import numpy; print('NumPy version:', numpy.__version__)"
python -c "import tensorflow; print('TensorFlow version:', tensorflow.__version__)"

echo.
echo Step 4: Testing final_pred.py...
python -c "from keras.models import load_model; print('Keras import: SUCCESS')"

echo.
echo ========================================
echo NumPy conflict fixed!
echo Now try: python final_pred.py
echo ========================================
pause