# Auto-Launch Sign Detection - Quick Guide

## 🎯 What's New?

Now you can launch the Sign Language Detection application **automatically** from the web interface with just one click!

## 🚀 How It Works

### Step 1: Start Backend
```bash
cd isslconnect
python app.py
```
Backend runs on: http://localhost:3002

### Step 2: Start Frontend
```bash
cd isslconnect
npm start
```
Frontend runs on: http://localhost:3001

### Step 3: Use the Application
1. Open browser: http://localhost:3001
2. Login/Signup
3. Click "Sign to Text" in navbar
4. Click the **"Launch Application"** button
5. ✅ A new desktop window will open automatically!

## 🎨 Features

### Automatic Launch
- No need to manually run `python final_pred.py`
- Click button → Application opens
- New console window with the app

### Status Messages
- ✅ Success: "Application launched! A new window should open."
- ❌ Error: Shows error message if something goes wrong

### Button States
- **Normal**: "Launch Application"
- **Loading**: "Launching..." (button disabled)
- **After Launch**: Returns to normal after 3 seconds

## 🔧 Technical Details

### Backend Endpoint
```
POST /api/launch_sign_detection
```

**Response:**
```json
{
  "message": "Sign detection application launched successfully",
  "status": "running"
}
```

### How It Launches
- Uses Python `subprocess.Popen()`
- Creates new console window (Windows)
- Runs in background without blocking
- Independent process from backend

### File Structure
```
isslconnect/
├── app.py                    # Backend with launch endpoint
├── final_pred.py             # Sign detection app
├── src/
│   └── components/
│       └── SignToText.jsx    # Frontend with launch button
```

## 🐛 Troubleshooting

### Button Doesn't Work
- Check if backend is running on port 3002
- Open browser console (F12) for errors
- Verify `final_pred.py` exists in isslconnect folder

### Window Doesn't Open
- Check if Python is in system PATH
- Verify all dependencies are installed
- Look for error message in status display

### Multiple Windows Open
- Each button click launches a new instance
- Close previous windows before launching again
- Or just use the already open window

## 💡 Tips

1. **First Time Setup**: Make sure dependencies are installed
   ```bash
   pip install -r requirements_clean.txt
   ```

2. **Camera Permissions**: Grant camera access when prompted

3. **Close Windows**: Close the detection window when done to free resources

4. **Relaunch**: You can click the button multiple times if needed

## 📝 Comparison

### Before (Manual)
1. Open terminal
2. Navigate to isslconnect
3. Run: `python final_pred.py`
4. Wait for window to open

### After (Automatic) ✨
1. Click "Launch Application" button
2. Done! Window opens automatically

## 🎓 What Happens Behind the Scenes

1. Frontend sends POST request to `/api/launch_sign_detection`
2. Backend receives request
3. Backend runs: `subprocess.Popen(['python', 'final_pred.py'])`
4. New console window opens with the application
5. Backend returns success response
6. Frontend shows success message

## ✅ Benefits

- **Faster**: One click vs multiple terminal commands
- **Easier**: No need to remember commands
- **User-Friendly**: Non-technical users can use it
- **Integrated**: Seamless experience within the web app

---

**Enjoy the automatic launch feature! 🚀**
