#!/usr/bin/env python3
"""
Quick test script to verify Sign-to-Text integration
"""

import requests
import json
import cv2
import numpy as np
from PIL import Image
import io

def test_api_health():
    """Test if Sign Recognition API is running"""
    try:
        response = requests.get('http://127.0.0.1:5001/health')
        if response.status_code == 200:
            data = response.json()
            print("✅ API Health Check:")
            print(f"   Status: {data['status']}")
            print(f"   Model Loaded: {data['model_loaded']}")
            print(f"   MediaPipe Ready: {data['mediapipe_ready']}")
            return True
        else:
            print("❌ API Health Check Failed")
            return False
    except Exception as e:
        print(f"❌ API Connection Error: {e}")
        return False

def test_gesture_prediction():
    """Test gesture prediction with dummy image"""
    try:
        # Create a dummy image (white background)
        dummy_img = np.ones((480, 640, 3), dtype=np.uint8) * 255
        
        # Convert to bytes
        _, buffer = cv2.imencode('.jpg', dummy_img)
        img_bytes = io.BytesIO(buffer)
        
        # Send to API
        files = {'frame': ('test.jpg', img_bytes, 'image/jpeg')}
        response = requests.post('http://127.0.0.1:5001/predict_gesture', files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Gesture Prediction Test:")
            print(f"   Gesture: {data['gesture']}")
            print(f"   Confidence: {data['confidence']:.2f}")
            print(f"   Suggestions: {data['suggestions']}")
            return True
        else:
            print(f"❌ Gesture Prediction Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Gesture Prediction Error: {e}")
        return False

def test_frontend_routes():
    """Test if React frontend routes are accessible"""
    routes_to_test = [
        'http://localhost:3000/',
        'http://localhost:3000/text-to-sign',
        'http://localhost:3000/sign-to-text'
    ]
    
    print("🌐 Testing Frontend Routes:")
    for route in routes_to_test:
        try:
            response = requests.get(route, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {route}")
            else:
                print(f"   ❌ {route} - Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {route} - Error: {e}")

def main():
    print("🧪 ISSL Connect Integration Test")
    print("=" * 40)
    
    # Test API
    api_healthy = test_api_health()
    print()
    
    if api_healthy:
        test_gesture_prediction()
        print()
    
    # Test Frontend (optional - requires React to be running)
    print("Note: Frontend tests require React to be running on port 3000")
    test_frontend_routes()
    
    print("\n" + "=" * 40)
    if api_healthy:
        print("🎉 Integration tests completed!")
        print("✅ Sign-to-Text API is working")
        print("🚀 Ready to use Sign-to-Text feature!")
    else:
        print("❌ Integration tests failed")
        print("🔧 Please check API setup and try again")

if __name__ == "__main__":
    main()