# ISL Connect - Quick Start Guide

## 🚀 Fast Startup with Background Service

### Architecture
```
Terminal 1: Sign Detection Service (Port 5001) - Pre-loads model
Terminal 2: Backend API (Port 3002)
Terminal 3: Frontend React (Port 3001)
```

### Benefits
- ✅ **Instant Launch**: Model pre-loaded in background
- ✅ **Fast Response**: GUI opens immediately when clicked
- ✅ **No Waiting**: No model loading delay

---

## Method 1: Automatic Startup (Recommended)

### Windows
```bash
cd isslconnect
START_ALL.bat
```

This will open 3 terminal windows automatically!

---

## Method 2: Manual Startup

### Terminal 1: Sign Detection Service
```bash
cd isslconnect
python sign_service.py
```
**Wait for**: `✅ Model loaded! Service ready for instant launch.`

### Terminal 2: Backend
```bash
cd isslconnect
python app.py
```
**Wait for**: `Running on http://127.0.0.1:3002`

### Terminal 3: Frontend
```bash
cd isslconnect
npm start
```
**Opens**: Browser at http://localhost:3001

---

## How It Works

### 1. Sign Service (Background)
- Runs on port 5001
- Pre-loads AI model (takes 5-10 seconds)
- Stays ready in background
- No GUI window yet

### 2. User Clicks "Launch Application"
- Frontend → Backend → Sign Service
- Service launches GUI instantly (already loaded!)
- Camera window opens immediately

### 3. Benefits
- **First time**: Fast (model already loaded)
- **Subsequent times**: Instant
- **No CMD window**: Clean experience

---

## Service Status

Check if service is ready:
```bash
curl http://localhost:5001/status
```

Response:
```json
{
  "model_loaded": true,
  "gui_running": false,
  "status": "ready"
}
```

---

## Troubleshooting

### Service Not Starting
```bash
# Check if port 5001 is free
netstat -ano | findstr :5001

# Install missing package
pip install flask flask-cors requests
```

### Model Loading Slow
- First time: 5-10 seconds (normal)
- Check: `cnn8grps_rad1_model.h5` exists
- Size: ~13MB

### GUI Not Opening
1. Check service status: `curl http://localhost:5001/status`
2. Ensure `model_loaded: true`
3. Check `final_pred.py` exists

---

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│  Terminal 1: Sign Service (Port 5001)  │
│  - Pre-loads AI model                   │
│  - Waits for launch command             │
│  - Ready for instant GUI launch         │
└─────────────────────────────────────────┘
                    ↑
                    │ HTTP Request
                    │
┌─────────────────────────────────────────┐
│  Terminal 2: Backend (Port 3002)       │
│  - Handles API requests                 │
│  - Forwards launch to service           │
└─────────────────────────────────────────┘
                    ↑
                    │ API Call
                    │
┌─────────────────────────────────────────┐
│  Terminal 3: Frontend (Port 3001)      │
│  - User clicks "Launch Application"     │
│  - Sends request to backend             │
└─────────────────────────────────────────┘
```

---

## Complete Workflow

1. **Startup** (One time)
   ```
   Terminal 1: python sign_service.py  → Model loads (5-10s)
   Terminal 2: python app.py           → Backend ready
   Terminal 3: npm start               → Frontend opens
   ```

2. **User Action**
   ```
   User clicks "Launch Application"
   → Frontend → Backend → Sign Service
   → GUI opens instantly! (< 1 second)
   ```

3. **Result**
   - Camera window opens
   - Hand tracking active
   - Text detection working
   - All features ready!

---

## Tips

1. **Keep Service Running**: Leave Terminal 1 open always
2. **Restart Service**: Only if model needs reload
3. **Multiple Launches**: Service handles multiple GUI instances
4. **Clean Shutdown**: Close all terminals when done

---

**Enjoy instant sign language detection! 🤟**
