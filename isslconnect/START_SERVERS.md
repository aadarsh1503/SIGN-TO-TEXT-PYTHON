# Quick Start Guide - ISL Connect

## Starting the Application

### Step 1: Start Backend Server
Open a terminal in the `isslconnect` folder and run:
```bash
python app.py
```
The backend will start on `http://localhost:3002`

### Step 2: Start Frontend (React)
Open another terminal in the `isslconnect` folder and run:
```bash
npm start
```
The frontend will start on `http://localhost:3001`

### Step 3: Use the Application
1. Open your browser and go to `http://localhost:3001`
2. Sign up or log in
3. Navigate to "Sign to Text" page
4. Click "Launch Application" button
5. The desktop sign detection window will open automatically
6. Show your hand gestures to the camera

## Troubleshooting

### If the application hangs when showing hand:
- Make sure you're running the latest version (background service removed)
- Close any other instances of the sign detection app
- Restart both backend and frontend servers

### If "Launch Application" doesn't work:
- Check that backend is running on port 3002
- Make sure `pythonw` is available (comes with Python on Windows)
- Check backend terminal for error messages

### If camera doesn't open:
- Grant camera permissions to Python
- Make sure no other application is using the camera
- Check if `final_pred.py`, `white.jpg`, and `cnn8grps_rad1_model.h5` exist in isslconnect folder

## Files Required in isslconnect folder:
- ✅ final_pred.py (sign detection application)
- ✅ white.jpg (background image for hand skeleton)
- ✅ cnn8grps_rad1_model.h5 (trained model)
- ✅ app.py (Flask backend)
- ✅ package.json (React frontend config)

## What Was Fixed:
- ❌ Removed background service that caused double model loading
- ✅ Direct launch approach using `pythonw`
- ✅ Correct working directory set for file access
- ✅ Removed abandoned service imports
- ✅ Clean architecture without pre-loading
