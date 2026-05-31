# Sign Detection Background Service
# Run this in Terminal 3: python sign_service.py

from flask import Flask, jsonify
from flask_cors import CORS
import threading
import os

# Pre-load heavy imports
print("🚀 Starting Sign Detection Service...")
print("📦 Loading dependencies...")

import numpy as np
import cv2
from keras.models import load_model
import mediapipe as mp

print("✅ Dependencies loaded!")

app = Flask(__name__)
CORS(app)

# Global state
model = None
model_loaded = False
gui_running = False

def load_model_background():
    """Load model in background"""
    global model, model_loaded
    try:
        print("🤖 Loading AI model...")
        model = load_model('cnn8grps_rad1_model.h5')
        model_loaded = True
        print("✅ Model loaded! Service ready for instant launch.")
    except Exception as e:
        print(f"❌ Error loading model: {e}")

# Start loading model immediately
threading.Thread(target=load_model_background, daemon=True).start()

@app.route('/status', methods=['GET'])
def status():
    """Check if service is ready"""
    return jsonify({
        "model_loaded": model_loaded,
        "gui_running": gui_running,
        "status": "ready" if model_loaded else "loading"
    })

@app.route('/launch', methods=['POST'])
def launch_gui():
    """Launch GUI window"""
    global gui_running
    
    if not model_loaded:
        return jsonify({
            "status": "error",
            "message": "Model still loading, please wait..."
        }), 503
    
    if gui_running:
        return jsonify({
            "status": "info",
            "message": "GUI already running"
        }), 200
    
    try:
        # Launch GUI
        import subprocess
        subprocess.Popen(['pythonw', 'final_pred.py'])
        gui_running = True
        
        return jsonify({
            "status": "success",
            "message": "GUI launched successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🎯 Sign Detection Service Running")
    print("="*50)
    print("📍 Service URL: http://localhost:5001")
    print("✅ Ready to launch GUI instantly!")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
