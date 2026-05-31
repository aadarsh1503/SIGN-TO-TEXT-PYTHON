"""
Sign Detection Server - Waits for frontend signal to start camera
"""
from flask import Flask, jsonify
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
CORS(app)

camera_active = False
detection_thread = None

def start_detection():
    """Start the sign detection application"""
    global camera_active
    camera_active = True
    print("Starting sign detection...")
    
    # Import and run the application
    import final_pred
    
@app.route('/api/start_camera', methods=['POST'])
def start_camera():
    global detection_thread, camera_active
    
    if camera_active:
        return jsonify({"message": "Camera already running"}), 200
    
    try:
        # Start detection in a separate thread
        detection_thread = threading.Thread(target=start_detection, daemon=True)
        detection_thread.start()
        
        return jsonify({
            "message": "Camera started successfully",
            "status": "running"
        }), 200
        
    except Exception as e:
        print(f"Error starting camera: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/camera_status', methods=['GET'])
def camera_status():
    return jsonify({
        "active": camera_active,
        "status": "running" if camera_active else "stopped"
    }), 200

if __name__ == "__main__":
    print("Sign Detection Server running on http://localhost:5001")
    print("Waiting for frontend signal to start camera...")
    app.run(debug=False, port=5001, threaded=True)
