# ISL Connect - Complete Setup Guide

## 🎯 Overview

ISL Connect is a complete sign language communication platform with two main features:
1. **Text to Sign**: Convert text/video to Indian Sign Language
2. **Sign to Text**: Convert sign language gestures to text

## 📁 Project Structure

```
isslconnect/
├── src/                          # React frontend
│   ├── components/
│   │   ├── LoginPage.jsx        # Login/Signup page
│   │   ├── TextToSign.jsx       # Text to ISL conversion
│   │   ├── SignToText.jsx       # Sign to Text launcher
│   │   └── AboutUs.jsx          # About page
│   └── App.js                   # Main routing
├── app.py                        # Flask backend (port 3002)
├── final_pred.py                 # Sign detection app (desktop)
├── cnn8grps_rad1_model.h5       # AI model for sign detection
├── white.jpg                     # Background for hand tracking
├── requirements_clean.txt        # Python dependencies
├── start_sign_detection.bat     # Launch sign detection
└── package.json                  # Node dependencies
```

## 🚀 Complete Installation

### Step 1: Install Python Dependencies
```bash
cd isslconnect
pip install -r requirements_clean.txt
```

**Required Packages:**
- numpy==1.26.4
- tensorflow==2.16.1
- keras==3.14.1
- mediapipe==0.10.14
- opencv-python==4.9.0.80
- pyttsx3
- pyenchant
- flask
- flask-cors
- whisper
- moviepy
- yt-dlp

### Step 2: Install Node Dependencies
```bash
npm install
```

### Step 3: Verify Files
Ensure these files exist in `isslconnect/`:
- ✅ `cnn8grps_rad1_model.h5` (AI model)
- ✅ `white.jpg` (hand tracking background)
- ✅ `final_pred.py` (sign detection app)

## 🎮 Running the Application

### Option 1: Run Everything Together

**Terminal 1 - Backend (Flask):**
```bash
cd isslconnect
python app.py
```
Backend runs on: http://localhost:3002

**Terminal 2 - Frontend (React):**
```bash
cd isslconnect
npm start
```
Frontend runs on: http://localhost:3001

### Option 2: Use the Web Interface

1. Open browser: http://localhost:3001
2. Create account (Signup)
3. Login with your credentials
4. Navigate using the navbar:
   - **Text to Sign**: Convert text/video to ISL
   - **Sign to Text**: Launch desktop app for gesture recognition

## 🤟 Using Sign to Text Feature

### From Web Interface:
1. Login to ISL Connect
2. Click "Sign to Text" in navbar
3. Click "Launch Application" button
4. Follow instructions to run: `python final_pred.py`

### Direct Launch:
```bash
cd isslconnect
python final_pred.py
```

Or double-click: `start_sign_detection.bat`

### Application Features:
- Real-time hand tracking with MediaPipe
- AI-powered gesture recognition (A-Z)
- Text-to-speech synthesis
- Word suggestions
- Special gestures: Space, Backspace, Next

## 📝 Using Text to Sign Feature

1. Login to ISL Connect
2. Click "Text to Sign" in navbar
3. Enter text in the input box
4. Click "Convert to ISL"
5. Watch the generated ISL video

## 🔐 Authentication

The app uses simple in-memory authentication:
- Create account with username, email, password
- Login to access features
- Logout to clear session

**Note:** User data is stored in memory (resets on server restart)

## 🎯 API Endpoints

### Backend (Port 3002)
- `POST /api/users/signup` - Create new user
- `POST /api/users/login` - Login user
- `POST /text_to_sign` - Convert text to ISL video
- `POST /process_video` - Process video with ISL
- `GET /videos/<filename>` - Serve generated videos
- `GET /isl_image/<letter>` - Get ISL image for letter

## 🔧 Troubleshooting

### Backend Not Starting
```bash
# Check if port 3002 is free
netstat -ano | findstr :3002

# Kill process if needed
taskkill /PID <process_id> /F

# Restart backend
python app.py
```

### Frontend Not Starting
```bash
# Check if port 3001 is free
netstat -ano | findstr :3001

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm start
```

### Sign Detection Not Working
```bash
# Reinstall dependencies
pip uninstall -y numpy tensorflow keras mediapipe
pip install -r requirements_clean.txt

# Verify model file exists
dir cnn8grps_rad1_model.h5

# Check camera permissions
# Grant Python camera access in Windows Settings
```

### CORS Errors
- Ensure backend is running on port 3002
- Check `package.json` proxy: `"proxy": "http://localhost:3002"`
- Verify CORS is enabled in `app.py`

## 📊 Port Configuration

| Service | Port | URL |
|---------|------|-----|
| React Frontend | 3001 | http://localhost:3001 |
| Flask Backend | 3002 | http://localhost:3002 |
| Sign Detection | Desktop App | Tkinter GUI |

## 💡 Tips

### For Best Sign Detection:
- Good lighting on your hand
- Plain background
- Hand 1-2 feet from camera
- Make gestures slowly
- Hold each gesture for 1-2 seconds

### For Text to ISL:
- Keep text concise
- Use simple words
- Wait for video generation
- Videos saved in `output_v/` folder

## 🎓 Features Summary

### ✅ Implemented
- User authentication (signup/login)
- Text to ISL video conversion
- Sign to text detection (desktop app)
- Real-time hand tracking
- Text-to-speech
- Word suggestions
- Video processing with Whisper
- YouTube video download and conversion

### 🔄 Architecture
- **Frontend**: React (port 3001)
- **Backend**: Flask (port 3002)
- **Sign Detection**: Python Tkinter (desktop)
- **AI Models**: CNN + MediaPipe + Whisper

## 📚 Documentation Files

- `SIGN_TO_TEXT_GUIDE.md` - Detailed sign detection guide
- `COMPLETE_SETUP.md` - This file
- `TROUBLESHOOTING.md` - Common issues (root folder)
- `README.md` - Project overview (root folder)

## 🆘 Getting Help

If you encounter issues:
1. Check this guide first
2. Read `TROUBLESHOOTING.md`
3. Verify all dependencies are installed
4. Check Python version (3.12 required)
5. Ensure camera permissions are granted

---

**Everything is ready! Start the backend and frontend, then enjoy ISL Connect! 🚀**
