# Troubleshooting Guide - Common Errors

## Error 1: ModuleNotFoundError: tensorflow.python.trackable

**Problem:** TensorFlow installation corrupted or version mismatch in Anaconda

### Solution Steps:

#### Step 1: Complete Cleanup
```bash
# Uninstall all conflicting packages
pip uninstall tensorflow tensorflow-intel keras -y
pip uninstall jax jaxlib -y
conda remove tensorflow keras -y
```

#### Step 2: Fresh Installation
```bash
# Install specific compatible versions
pip install tensorflow==2.16.1
pip install keras==3.0.5
```

#### Step 3: If still not working, try Conda installation
```bash
conda install tensorflow=2.16.1 -c conda-forge
```

#### Step 4: Alternative - Use CPU-only TensorFlow
```bash
pip install tensorflow-cpu==2.16.1
```

## Error 2: Anaconda Environment Issues

### Solution: Create New Environment
```bash
# Create new conda environment
conda create -n signlang python=3.9
conda activate signlang

# Install packages in new environment
pip install opencv-python
pip install numpy==1.26.4
pip install tensorflow==2.16.1
pip install mediapipe==0.10.14
pip install pyttsx3
pip install pillow
pip install pyenchant
```

## Error 3: Import Errors

### Quick Fix Commands:
```bash
# Reset pip cache
pip cache purge

# Reinstall with force
pip install --force-reinstall --no-cache-dir tensorflow==2.16.1

# Check installation
python -c "import tensorflow as tf; print(tf.__version__)"
```

## Error 4: Keras Backend Issues

### Solution:
```bash
# Set environment variable
set TF_ENABLE_ONEDNN_OPTS=0

# Or add to Python code:
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
```

## Complete Fresh Setup (Recommended)

### For Anaconda Users:
```bash
# 1. Create new environment
conda create -n signlang python=3.9 -y
conda activate signlang

# 2. Install packages
pip install opencv-python==4.8.1.78
pip install numpy==1.26.4
pip install tensorflow==2.16.1
pip install mediapipe==0.10.14
pip install pyttsx3==2.90
pip install pillow==10.0.0
pip install pyenchant==3.2.2

# 3. Test installation
python -c "import cv2, numpy, tensorflow, mediapipe; print('Success!')"

# 4. Run application
python final_pred.py
```

### For Regular Python:
```bash
# 1. Create virtual environment
python -m venv signlang_env
signlang_env\Scripts\activate

# 2. Install packages (same as above)
# 3. Run application
```

## System-Specific Fixes

### Windows + Anaconda:
- Use Anaconda Prompt (not regular CMD)
- Activate environment before installing
- Use `conda install` for core packages

### If nothing works:
1. Uninstall Anaconda completely
2. Install fresh Python 3.9 from python.org
3. Follow regular installation steps

---

**Most Common Fix:** Create new conda environment with Python 3.9