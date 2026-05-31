# Sign Language to Text - User Guide

## 🚀 Quick Start

### Method 1: Using Batch File (Windows)
1. Navigate to `isslconnect` folder
2. Double-click `start_sign_detection.bat`
3. The application window will open

### Method 2: Using Command Line
```bash
cd isslconnect
python final_pred.py
```

## 📋 Prerequisites

### Required Software
- Python 3.12
- Webcam (built-in or external)

### Required Dependencies
Install all dependencies using:
```bash
pip install -r requirements_clean.txt
```

### Required Files (Already in isslconnect folder)
- `final_pred.py` - Main application
- `cnn8grps_rad1_model.h5` - Trained AI model
- `white.jpg` - Background image for hand tracking

## 🎯 How to Use

### Starting the Application
1. Run `python final_pred.py` from the isslconnect folder
2. A window titled "Sign Language To Text Conversion" will open
3. Your webcam will activate automatically

### Making Gestures
1. Position your hand clearly in front of the camera
2. Make sign language gestures for letters A-Z
3. The detected character will appear in the "Character" box
4. Use the "next" gesture (specific hand position) to add the character to the sentence

### Special Gestures
- **Space**: Add a space between words
- **Next**: Confirm and add the current character to sentence
- **Backspace**: Remove the last character

### Using the Interface
- **Character Box**: Shows the currently detected gesture
- **Sentence Box**: Shows the complete text you've created
- **Suggestions**: Shows word suggestions based on what you've typed
- **Speak Button**: Converts your text to speech
- **Clear Button**: Clears all text and starts fresh
- **Suggestion Buttons**: Click to auto-complete words

## 💡 Tips for Best Results

1. **Lighting**: Ensure good, even lighting on your hand
2. **Background**: Use a plain background for better detection
3. **Distance**: Keep your hand 1-2 feet from the camera
4. **Speed**: Make gestures slowly and hold for 1-2 seconds
5. **Clarity**: Keep your hand fully visible and fingers clear

## 🔧 Troubleshooting

### Camera Not Working
- Check if another application is using the camera
- Grant camera permissions to Python
- Try restarting the application

### Model Not Loading
- Ensure `cnn8grps_rad1_model.h5` is in the isslconnect folder
- Check if Keras and TensorFlow are properly installed

### Poor Detection Accuracy
- Improve lighting conditions
- Clean your camera lens
- Make gestures more clearly and slowly
- Ensure your entire hand is visible

### Dependencies Error
```bash
# Reinstall dependencies
pip uninstall -y numpy tensorflow keras mediapipe opencv-python
pip install -r requirements_clean.txt
```

## 📦 Package Versions (Working Configuration)
- numpy==1.26.4
- tensorflow==2.16.1
- keras==3.14.1
- mediapipe==0.10.14
- opencv-python==4.9.0.80
- pyttsx3 (latest)
- pyenchant (latest)

## 🎨 Application Features

### Real-time Hand Tracking
- Uses MediaPipe for hand landmark detection
- Tracks 21 hand landmarks in real-time
- Draws hand skeleton on white background

### AI-Powered Recognition
- CNN model trained on 8 gesture groups
- Recognizes all 26 English alphabet letters
- High accuracy with proper lighting

### Text-to-Speech
- Built-in speech synthesis
- Adjustable speech rate
- Clear pronunciation

### Word Suggestions
- English dictionary integration
- Up to 4 word suggestions
- Click to auto-complete

## 🔗 Integration with ISL Connect

The Sign to Text feature is integrated into the ISL Connect web application:

1. Login to ISL Connect (http://localhost:3001)
2. Click "Sign to Text" in the navigation bar
3. Follow the instructions to launch the desktop application
4. The desktop app runs independently with full features

## 📝 Notes

- The application uses Tkinter for the GUI (desktop application)
- It cannot run directly in a web browser
- Camera access is required for gesture detection
- The model file is approximately 50MB in size

## 🆘 Support

If you encounter issues:
1. Check `TROUBLESHOOTING.md` in the root folder
2. Ensure all dependencies are correctly installed
3. Verify Python version is 3.12
4. Check camera permissions

## 🎓 Supported Gestures

The application recognizes:
- **Letters**: A-Z (American Sign Language alphabet)
- **Special**: Space, Backspace, Next (confirm)
- **Groups**: 8 main gesture groups for classification

---

**Enjoy using Sign Language to Text! 🤟**
