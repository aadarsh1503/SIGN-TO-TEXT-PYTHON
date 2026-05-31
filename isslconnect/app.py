from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import whisper
try:
    from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, TextClip, CompositeVideoClip
except ImportError:
    from moviepy import VideoFileClip, ImageClip, concatenate_videoclips, TextClip, CompositeVideoClip
from yt_dlp import YoutubeDL
import subprocess
import random
import glob
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

# Assuming the same constants and functions from your code
ISL_DATASET_PATH = os.getenv('ISL_DATASET_PATH', r"C:\Users\aadar\.cache\kagglehub\datasets\prathumarikeri\indian-sign-language-isl\versions\1\Indian")
OUTPUT_FOLDER = "output_v"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load Whisper model once at startup
print("Loading Whisper model...")
whisper_model = whisper.load_model("base")
print("Whisper model loaded!")

app = Flask(__name__)
CORS(app)

# Simple in-memory user storage (for demo - use database in production)
users_db = {}
camera_signal = {"start": False}  # Signal for camera to start

@app.route('/api/users/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({"error": "All fields required"}), 400
        
        if email in users_db:
            return jsonify({"error": "User already exists"}), 400
        
        users_db[email] = {
            'username': username,
            'email': email,
            'password': password  # In production, hash this!
        }
        
        return jsonify({
            "message": "User created successfully",
            "user": {"username": username, "email": email}
        }), 201
        
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        
        user = users_db.get(email)
        
        if not user or user['password'] != password:
            return jsonify({"error": "Invalid credentials"}), 401
        
        return jsonify({
            "message": "Login successful",
            "user": {"username": user['username'], "email": user['email']}
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/launch_sign_detection', methods=['POST'])
def launch_sign_detection():
    try:
        camera_signal["start"] = True
        return jsonify({"message": "Signal sent", "status": "running"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process_frame', methods=['POST'])
def process_frame():
    """Receives a video frame, runs MediaPipe + prediction, returns character/sentence/skeleton"""
    try:
        import numpy as np
        import cv2
        import math
        import base64
        import mediapipe as mp

        # Init state once
        if not hasattr(process_frame, 'model'):
            from keras.models import load_model as keras_load
            import enchant
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cnn8grps_rad1_model.h5')
            print("Loading model...")
            process_frame.model = keras_load(model_path)
            process_frame.model.predict(np.zeros((1,400,400,3)), verbose=0)
            print("Model ready!")
            process_frame.ddd = enchant.Dict("en-US")
            process_frame.sentence = ' '
            process_frame.prev_char = ''
            process_frame.count = -1
            process_frame.ten_prev = [' '] * 10
            # MediaPipe hands
            process_frame.mp_hands = mp.solutions.hands
            process_frame.hands = process_frame.mp_hands.Hands(
                static_image_mode=False, max_num_hands=1,
                min_detection_confidence=0.5, min_tracking_confidence=0.5,
                model_complexity=0
            )

        # Read frame
        file = request.files['frame']
        img_array = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if frame is None:
            return jsonify({"character": ""}), 200

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        # Run MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = process_frame.hands.process(rgb)

        if not results.multi_hand_landmarks:
            return jsonify({"character": "", "sentence": process_frame.sentence, "suggestions": ['','','',''], "skeleton": None}), 200

        hand_lms = results.multi_hand_landmarks[0]

        # Get landmark pixel coords
        pts = [[int(lm.x * w), int(lm.y * h)] for lm in hand_lms.landmark]

        # Crop hand region
        offset = 29
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        x1 = max(0, min(xs) - offset); y1 = max(0, min(ys) - offset)
        x2 = min(w, max(xs) + offset); y2 = min(h, max(ys) + offset)
        crop = frame[y1:y2, x1:x2]

        if crop.size == 0:
            return jsonify({"character": ""}), 200

        # Draw skeleton on white image (same as Python final_pred.py)
        white = np.ones((400, 400, 3), dtype=np.uint8) * 255
        cw, ch = x2-x1, y2-y1
        os_x = ((400 - cw) // 2) - 15
        os_y = ((400 - ch) // 2) - 15
        lpts = [[p[0]-x1, p[1]-y1] for p in pts]

        def draw_line(a, b):
            cv2.line(white, (lpts[a][0]+os_x, lpts[a][1]+os_y), (lpts[b][0]+os_x, lpts[b][1]+os_y), (0,255,0), 3)

        for t in range(0,4): draw_line(t, t+1)
        for t in range(5,8): draw_line(t, t+1)
        for t in range(9,12): draw_line(t, t+1)
        for t in range(13,16): draw_line(t, t+1)
        for t in range(17,20): draw_line(t, t+1)
        draw_line(5,9); draw_line(9,13); draw_line(13,17); draw_line(0,5); draw_line(0,17)
        for i in range(21):
            cv2.circle(white, (lpts[i][0]+os_x, lpts[i][1]+os_y), 2, (0,0,255), 1)

        # Encode skeleton as base64
        _, buf = cv2.imencode('.png', white)
        skeleton_b64 = base64.b64encode(buf).decode('utf-8')

        # Predict using model
        white_resized = cv2.resize(white, (400, 400)).reshape(1, 400, 400, 3)
        prob = np.array(process_frame.model.predict(white_resized, verbose=0)[0], dtype='float32')
        ch1 = int(np.argmax(prob)); prob[ch1] = 0
        ch2 = int(np.argmax(prob))
        pl = [ch1, ch2]

        def dist(a, b):
            return math.sqrt((pts[a][0]-pts[b][0])**2 + (pts[a][1]-pts[b][1])**2)

        # All group conditions (exact same as final_pred.py)
        if pl in [[5,2],[5,3],[3,5],[3,6],[3,0],[3,2],[6,4],[6,1],[6,2],[6,6],[6,7],[6,0],[6,5],[4,1],[1,0],[1,1],[6,3],[1,6],[5,6],[5,1],[4,5],[1,4],[1,5],[2,0],[2,6],[4,6],[5,7],[7,6],[2,5],[7,1],[5,4],[7,0],[7,5],[7,2]]:
            if pts[6][1]<pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1]: ch1=0
        if pl in [[2,2],[2,1]]:
            if pts[5][0]<pts[4][0]: ch1=0
        pl=[ch1,ch2]
        if pl in [[0,0],[0,6],[0,2],[0,5],[0,1],[0,7],[5,2],[7,6],[7,1]]:
            if pts[0][0]>pts[8][0] and pts[0][0]>pts[4][0] and pts[0][0]>pts[12][0] and pts[0][0]>pts[16][0] and pts[0][0]>pts[20][0] and pts[5][0]>pts[4][0]: ch1=2
        if pl in [[6,0],[6,6],[6,2]]:
            if dist(8,16)<52: ch1=2
        if pl in [[1,4],[1,5],[1,6],[1,3],[1,0]]:
            if pts[6][1]>pts[8][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and pts[0][0]<pts[8][0] and pts[0][0]<pts[12][0] and pts[0][0]<pts[16][0] and pts[0][0]<pts[20][0]: ch1=3
        if pl in [[4,6],[4,1],[4,5],[4,3],[4,7]]:
            if pts[4][0]>pts[0][0]: ch1=3
        if pl in [[5,3],[5,0],[5,7],[5,4],[5,2],[5,1],[5,5]]:
            if pts[2][1]+15<pts[16][1]: ch1=3
        if pl in [[6,4],[6,1],[6,2]]:
            if dist(4,11)>55: ch1=4
        if pl in [[1,4],[1,6],[1,1]]:
            if dist(4,11)>50 and pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1]: ch1=4
        if pl in [[3,6],[3,4]]:
            if pts[4][0]<pts[0][0]: ch1=4
        if pl in [[2,2],[2,5],[2,4]]:
            if pts[1][0]<pts[12][0]: ch1=4
        if pl in [[3,6],[3,5],[3,4]]:
            if pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and pts[4][1]>pts[10][1]: ch1=5
        if pl in [[3,2],[3,1],[3,6]]:
            if pts[4][1]+17>pts[8][1] and pts[4][1]+17>pts[12][1] and pts[4][1]+17>pts[16][1] and pts[4][1]+17>pts[20][1]: ch1=5
        if pl in [[4,4],[4,5],[4,2],[7,5],[7,6],[7,0]]:
            if pts[4][0]>pts[0][0]: ch1=5
        if pl in [[0,2],[0,6],[0,1],[0,5],[0,0],[0,7],[0,4],[0,3],[2,7]]:
            if pts[0][0]<pts[8][0] and pts[0][0]<pts[12][0] and pts[0][0]<pts[16][0] and pts[0][0]<pts[20][0]: ch1=5
        if pl in [[5,7],[5,2],[5,6]]:
            if pts[3][0]<pts[0][0]: ch1=7
        if pl in [[4,6],[4,2],[4,4],[4,1],[4,5],[4,7]]:
            if pts[6][1]<pts[8][1]: ch1=7
        if pl in [[6,7],[0,7],[0,1],[0,0],[6,4],[6,6],[6,5],[6,1]]:
            if pts[18][1]>pts[20][1]: ch1=7
        if pl in [[0,4],[0,2],[0,3],[0,1],[0,6]]:
            if pts[5][0]>pts[16][0]: ch1=6
        if pl in [[7,2]]:
            if pts[18][1]<pts[20][1] and pts[8][1]<pts[10][1]: ch1=6
        if pl in [[2,1],[2,2],[2,6],[2,7],[2,0]]:
            if dist(8,16)>50: ch1=6
        if pl in [[4,6],[4,2],[4,1],[4,4]]:
            if dist(4,11)<60: ch1=6
        if pl in [[1,4],[1,6],[1,0],[1,2]]:
            if pts[5][0]-pts[4][0]-15>0: ch1=6
        if pl in [[5,0],[5,1],[5,4],[5,5],[5,6],[6,1],[7,6],[0,2],[7,1],[7,4],[6,6],[7,2],[6,3],[6,4],[7,5]]:
            if pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1] and pts[18][1]>pts[20][1]: ch1=1
        if pl in [[6,1],[6,0],[0,3],[6,4],[2,2],[0,6],[6,2],[7,6],[4,6],[4,1],[4,2],[0,2],[7,1],[7,4],[6,6],[7,2],[7,5]]:
            if pts[6][1]<pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1] and pts[18][1]>pts[20][1]: ch1=1
        if pl in [[6,1],[6,0],[4,2],[4,1],[4,6],[4,4]]:
            if pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1] and pts[18][1]>pts[20][1]: ch1=1
        if pl in [[5,0],[3,4],[3,0],[3,1],[3,5],[5,5],[5,4],[5,1],[7,6]]:
            if pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and pts[2][0]<pts[0][0] and pts[4][1]>pts[14][1]: ch1=1
        if pl in [[4,1],[4,2],[4,4]]:
            if dist(4,11)<50 and pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1]: ch1=1
        if pl in [[3,4],[3,0],[3,1],[3,5],[3,6]]:
            if pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and pts[2][0]<pts[0][0] and pts[14][1]<pts[4][1]: ch1=1
        if pl in [[6,6],[6,4],[6,1],[6,2]]:
            if pts[5][0]-pts[4][0]-15<0: ch1=1
        if pl in [[5,4],[5,5],[5,1],[0,3],[0,7],[5,0],[0,2],[6,2],[7,5],[7,1],[7,6],[7,7]]:
            if pts[6][1]<pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]>pts[20][1]: ch1=1
        if pl in [[1,5],[1,7],[1,1],[1,6],[1,3],[1,0]]:
            if pts[4][0]<pts[5][0]+15 and pts[6][1]<pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]>pts[20][1]: ch1=7
        if pl in [[5,5],[5,0],[5,4],[5,1],[4,6],[4,1],[7,6],[3,0],[3,5]]:
            if pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and pts[4][1]>pts[14][1]: ch1=1
        if pl in [[3,5],[3,0],[3,6],[5,1],[4,1],[2,0],[5,0],[5,5]]:
            if not(pts[0][0]+13<pts[8][0] and pts[0][0]+13<pts[12][0] and pts[0][0]+13<pts[16][0] and pts[0][0]+13<pts[20][0]) and not(pts[0][0]>pts[8][0] and pts[0][0]>pts[12][0] and pts[0][0]>pts[16][0] and pts[0][0]>pts[20][0]) and dist(4,11)<50: ch1=1
        if pl in [[5,0],[5,5],[0,1]]:
            if pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1]: ch1=1

        # Subgroup classification
        if ch1==0:
            ch1='S'
            if pts[4][0]<pts[6][0] and pts[4][0]<pts[10][0] and pts[4][0]<pts[14][0] and pts[4][0]<pts[18][0]: ch1='A'
            if pts[4][0]>pts[6][0] and pts[4][0]<pts[10][0] and pts[4][0]<pts[14][0] and pts[4][0]<pts[18][0] and pts[4][1]<pts[14][1] and pts[4][1]<pts[18][1]: ch1='T'
            if pts[4][1]>pts[8][1] and pts[4][1]>pts[12][1] and pts[4][1]>pts[16][1] and pts[4][1]>pts[20][1]: ch1='E'
            if pts[4][0]>pts[6][0] and pts[4][0]>pts[10][0] and pts[4][0]>pts[14][0] and pts[4][1]<pts[18][1]: ch1='M'
            if pts[4][0]>pts[6][0] and pts[4][0]>pts[10][0] and pts[4][1]<pts[18][1] and pts[4][1]<pts[14][1]: ch1='N'
        if ch1==2: ch1='C' if dist(12,4)>42 else 'O'
        if ch1==3: ch1='G' if dist(8,12)>72 else 'H'
        if ch1==7: ch1='Y' if dist(8,4)>42 else 'J'
        if ch1==4: ch1='L'
        if ch1==6: ch1='X'
        if ch1==5:
            if pts[4][0]>pts[12][0] and pts[4][0]>pts[16][0] and pts[4][0]>pts[20][0]:
                ch1='Z' if pts[8][1]<pts[5][1] else 'Q'
            else: ch1='P'
        if ch1==1:
            if pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1] and pts[18][1]>pts[20][1]: ch1='B'
            if pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1]: ch1='D'
            if pts[6][1]<pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1] and pts[18][1]>pts[20][1]: ch1='F'
            if pts[6][1]<pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]>pts[20][1]: ch1='I'
            if pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1] and pts[18][1]<pts[20][1]: ch1='W'
            if pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and pts[4][1]<pts[9][1]: ch1='K'
            if (dist(8,12)-dist(6,10))<8 and pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1]: ch1='U'
            if (dist(8,12)-dist(6,10))>=8 and pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and pts[4][1]>pts[9][1]: ch1='V'
            if pts[8][0]>pts[12][0] and pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1]: ch1='R'

        if ch1 in [1,'E','S','X','Y','B']:
            if pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]>pts[20][1]: ch1=' '
        if ch1 in ['E','Y','B']:
            if pts[4][0]<pts[5][0] and pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1] and pts[18][1]>pts[20][1]: ch1='next'
        if pts[0][0]>pts[8][0] and pts[0][0]>pts[12][0] and pts[0][0]>pts[16][0] and pts[0][0]>pts[20][0] and pts[4][1]<pts[8][1] and pts[4][1]<pts[12][1] and pts[4][1]<pts[16][1] and pts[4][1]<pts[20][1] and pts[4][1]<pts[6][1] and pts[4][1]<pts[10][1] and pts[4][1]<pts[14][1] and pts[4][1]<pts[18][1]: ch1='Backspace'

        # Update sentence (same logic as final_pred.py)
        s = process_frame
        if ch1 == 'next' and s.prev_char != 'next':
            prev = s.ten_prev[(s.count-2)%10]
            if prev != 'next':
                if prev == 'Backspace': s.sentence = s.sentence[:-1]
                elif prev != 'Backspace': s.sentence += prev
            else:
                p2 = s.ten_prev[s.count%10]
                if p2 != 'Backspace': s.sentence += p2
        if ch1 == '  ' and s.prev_char != '  ':
            s.sentence += '  '
        s.prev_char = ch1
        s.count += 1
        s.ten_prev[s.count % 10] = ch1

        # Word suggestions
        word = s.sentence[s.sentence.rfind(' ')+1:]
        sugg = ['', '', '', '']
        if word.strip():
            try:
                sl = s.ddd.suggest(word)
                for i in range(min(4, len(sl))): sugg[i] = sl[i]
            except: pass

        return jsonify({
            "character": str(ch1),
            "sentence": s.sentence,
            "suggestions": sugg,
            "skeleton": skeleton_b64
        }), 200

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict_sign', methods=['POST'])
def predict_sign():
    try:
        import numpy as np
        import cv2
        import math
        from keras.models import load_model as keras_load

        if not hasattr(predict_sign, 'model'):
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cnn8grps_rad1_model.h5')
            print(f"Loading model from: {model_path}")
            predict_sign.model = keras_load(model_path)
            # Warm up
            import numpy as np_warm
            predict_sign.model.predict(np_warm.zeros((1,400,400,3)), verbose=0)
            print("Model loaded and warmed up!")
            predict_sign.sentence = ' '
            predict_sign.prev_char = ''
            predict_sign.count = -1
            predict_sign.ten_prev = [' '] * 10
            import enchant
            predict_sign.ddd = enchant.Dict("en-US")

        file = request.files['image']
        img_array = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        img = cv2.resize(img, (400, 400))

        import json
        landmarks = json.loads(request.form.get('landmarks', '[]'))
        if not landmarks:
            return jsonify({"character": ""}), 200

        pts = [[int(l['x'] * 480), int(l['y'] * 480)] for l in landmarks]

        # Scale factor vs original 400x400 cropped hand
        # Estimate hand size from bounding box to normalize distances
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        hand_w = max(xs) - min(xs); hand_h = max(ys) - min(ys)
        hand_size = max(hand_w, hand_h, 1)
        # In original Python, hand fills ~300px of 400px canvas, so scale = hand_size/300
        scale = hand_size / 300.0

        def dist(a, b):
            raw = math.sqrt((pts[a][0]-pts[b][0])**2 + (pts[a][1]-pts[b][1])**2)
            return raw / scale  # normalize to original scale

        white = img.reshape(1, 400, 400, 3)
        prob = np.array(predict_sign.model.predict(white, verbose=0)[0], dtype='float32')
        ch1 = int(np.argmax(prob)); prob[ch1] = 0
        ch2 = int(np.argmax(prob)); prob[ch2] = 0
        pl = [ch1, ch2]

        if pl in [[5,2],[5,3],[3,5],[3,6],[3,0],[3,2],[6,4],[6,1],[6,2],[6,6],[6,7],[6,0],[6,5],[4,1],[1,0],[1,1],[6,3],[1,6],[5,6],[5,1],[4,5],[1,4],[1,5],[2,0],[2,6],[4,6],[5,7],[7,6],[2,5],[7,1],[5,4],[7,0],[7,5],[7,2]]:
            if pts[6][1]<pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1]: ch1=0
        if pl in [[2,2],[2,1]]:
            if pts[5][0]<pts[4][0]: ch1=0
        pl=[ch1,ch2]
        if pl in [[0,0],[0,6],[0,2],[0,5],[0,1],[0,7],[5,2],[7,6],[7,1]]:
            if pts[0][0]>pts[8][0] and pts[0][0]>pts[4][0] and pts[0][0]>pts[12][0] and pts[0][0]>pts[16][0] and pts[0][0]>pts[20][0] and pts[5][0]>pts[4][0]: ch1=2
        if pl in [[6,0],[6,6],[6,2]]:
            if dist(8,16)<52: ch1=2
        if pl in [[1,4],[1,5],[1,6],[1,3],[1,0]]:
            if pts[6][1]>pts[8][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and pts[0][0]<pts[8][0] and pts[0][0]<pts[12][0] and pts[0][0]<pts[16][0] and pts[0][0]<pts[20][0]: ch1=3
        if pl in [[4,6],[4,1],[4,5],[4,3],[4,7]]:
            if pts[4][0]>pts[0][0]: ch1=3
        if pl in [[5,3],[5,0],[5,7],[5,4],[5,2],[5,1],[5,5]]:
            if pts[2][1]+15<pts[16][1]: ch1=3
        if pl in [[6,4],[6,1],[6,2]]:
            if dist(4,11)>55: ch1=4
        if pl in [[1,4],[1,6],[1,1]]:
            if dist(4,11)>50 and pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1]: ch1=4
        if pl in [[3,6],[3,4]]:
            if pts[4][0]<pts[0][0]: ch1=4
        if pl in [[2,2],[2,5],[2,4]]:
            if pts[1][0]<pts[12][0]: ch1=4
        if pl in [[3,6],[3,5],[3,4]]:
            if pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and pts[4][1]>pts[10][1]: ch1=5
        if pl in [[3,2],[3,1],[3,6]]:
            if pts[4][1]+17>pts[8][1] and pts[4][1]+17>pts[12][1] and pts[4][1]+17>pts[16][1] and pts[4][1]+17>pts[20][1]: ch1=5
        if pl in [[4,4],[4,5],[4,2],[7,5],[7,6],[7,0]]:
            if pts[4][0]>pts[0][0]: ch1=5
        if pl in [[0,2],[0,6],[0,1],[0,5],[0,0],[0,7],[0,4],[0,3],[2,7]]:
            if pts[0][0]<pts[8][0] and pts[0][0]<pts[12][0] and pts[0][0]<pts[16][0] and pts[0][0]<pts[20][0]: ch1=5
        if pl in [[5,7],[5,2],[5,6]]:
            if pts[3][0]<pts[0][0]: ch1=7
        if pl in [[4,6],[4,2],[4,4],[4,1],[4,5],[4,7]]:
            if pts[6][1]<pts[8][1]: ch1=7
        if pl in [[6,7],[0,7],[0,1],[0,0],[6,4],[6,6],[6,5],[6,1]]:
            if pts[18][1]>pts[20][1]: ch1=7
        if pl in [[0,4],[0,2],[0,3],[0,1],[0,6]]:
            if pts[5][0]>pts[16][0]: ch1=6
        if pl in [[7,2]]:
            if pts[18][1]<pts[20][1] and pts[8][1]<pts[10][1]: ch1=6
        if pl in [[2,1],[2,2],[2,6],[2,7],[2,0]]:
            if dist(8,16)>50: ch1=6
        if pl in [[4,6],[4,2],[4,1],[4,4]]:
            if dist(4,11)<60: ch1=6
        if pl in [[1,4],[1,6],[1,0],[1,2]]:
            if pts[5][0]-pts[4][0]-15>0: ch1=6
        if pl in [[5,0],[5,1],[5,4],[5,5],[5,6],[6,1],[7,6],[0,2],[7,1],[7,4],[6,6],[7,2],[6,3],[6,4],[7,5]]:
            if pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1] and pts[18][1]>pts[20][1]: ch1=1
        if pl in [[6,1],[6,0],[0,3],[6,4],[2,2],[0,6],[6,2],[7,6],[4,6],[4,1],[4,2],[0,2],[7,1],[7,4],[6,6],[7,2],[7,5]]:
            if pts[6][1]<pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1] and pts[18][1]>pts[20][1]: ch1=1
        if pl in [[6,1],[6,0],[4,2],[4,1],[4,6],[4,4]]:
            if pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1] and pts[18][1]>pts[20][1]: ch1=1
        if pl in [[5,0],[3,4],[3,0],[3,1],[3,5],[5,5],[5,4],[5,1],[7,6]]:
            if pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and pts[2][0]<pts[0][0] and pts[4][1]>pts[14][1]: ch1=1
        if pl in [[4,1],[4,2],[4,4]]:
            if dist(4,11)<50 and pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1]: ch1=1
        if pl in [[3,4],[3,0],[3,1],[3,5],[3,6]]:
            if pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and pts[2][0]<pts[0][0] and pts[14][1]<pts[4][1]: ch1=1
        if pl in [[6,6],[6,4],[6,1],[6,2]]:
            if pts[5][0]-pts[4][0]-15<0: ch1=1
        if pl in [[5,4],[5,5],[5,1],[0,3],[0,7],[5,0],[0,2],[6,2],[7,5],[7,1],[7,6],[7,7]]:
            if pts[6][1]<pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]>pts[20][1]: ch1=1
        if pl in [[1,5],[1,7],[1,1],[1,6],[1,3],[1,0]]:
            if pts[4][0]<pts[5][0]+15 and pts[6][1]<pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]>pts[20][1]: ch1=7
        if pl in [[5,5],[5,0],[5,4],[5,1],[4,6],[4,1],[7,6],[3,0],[3,5]]:
            if pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and pts[4][1]>pts[14][1]: ch1=1
        if pl in [[3,5],[3,0],[3,6],[5,1],[4,1],[2,0],[5,0],[5,5]]:
            if not(pts[0][0]+13<pts[8][0] and pts[0][0]+13<pts[12][0] and pts[0][0]+13<pts[16][0] and pts[0][0]+13<pts[20][0]) and not(pts[0][0]>pts[8][0] and pts[0][0]>pts[12][0] and pts[0][0]>pts[16][0] and pts[0][0]>pts[20][0]) and dist(4,11)<50: ch1=1
        if pl in [[5,0],[5,5],[0,1]]:
            if pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1]: ch1=1

        if ch1==0:
            ch1='S'
            if pts[4][0]<pts[6][0] and pts[4][0]<pts[10][0] and pts[4][0]<pts[14][0] and pts[4][0]<pts[18][0]: ch1='A'
            if pts[4][0]>pts[6][0] and pts[4][0]<pts[10][0] and pts[4][0]<pts[14][0] and pts[4][0]<pts[18][0] and pts[4][1]<pts[14][1] and pts[4][1]<pts[18][1]: ch1='T'
            if pts[4][1]>pts[8][1] and pts[4][1]>pts[12][1] and pts[4][1]>pts[16][1] and pts[4][1]>pts[20][1]: ch1='E'
            if pts[4][0]>pts[6][0] and pts[4][0]>pts[10][0] and pts[4][0]>pts[14][0] and pts[4][1]<pts[18][1]: ch1='M'
            if pts[4][0]>pts[6][0] and pts[4][0]>pts[10][0] and pts[4][1]<pts[18][1] and pts[4][1]<pts[14][1]: ch1='N'
        if ch1==2: ch1='C' if dist(12,4)>42 else 'O'
        if ch1==3: ch1='G' if dist(8,12)>72 else 'H'
        if ch1==7: ch1='Y' if dist(8,4)>42 else 'J'
        if ch1==4: ch1='L'
        if ch1==6: ch1='X'
        if ch1==5:
            if pts[4][0]>pts[12][0] and pts[4][0]>pts[16][0] and pts[4][0]>pts[20][0]:
                ch1='Z' if pts[8][1]<pts[5][1] else 'Q'
            else: ch1='P'
        if ch1==1:
            if pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1] and pts[18][1]>pts[20][1]: ch1='B'
            if pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1]: ch1='D'
            if pts[6][1]<pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1] and pts[18][1]>pts[20][1]: ch1='F'
            if pts[6][1]<pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]>pts[20][1]: ch1='I'
            if pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1] and pts[18][1]<pts[20][1]: ch1='W'
            if pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and pts[4][1]<pts[9][1]: ch1='K'
            if (dist(8,12)-dist(6,10))<8 and pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1]: ch1='U'
            if (dist(8,12)-dist(6,10))>=8 and pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1] and pts[4][1]>pts[9][1]: ch1='V'
            if pts[8][0]>pts[12][0] and pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]<pts[20][1]: ch1='R'

        if ch1 in [1,'E','S','X','Y','B']:
            if pts[6][1]>pts[8][1] and pts[10][1]<pts[12][1] and pts[14][1]<pts[16][1] and pts[18][1]>pts[20][1]: ch1=' '
        if ch1 in ['E','Y','B']:
            if pts[4][0]<pts[5][0] and pts[6][1]>pts[8][1] and pts[10][1]>pts[12][1] and pts[14][1]>pts[16][1] and pts[18][1]>pts[20][1]: ch1='next'
        if pts[0][0]>pts[8][0] and pts[0][0]>pts[12][0] and pts[0][0]>pts[16][0] and pts[0][0]>pts[20][0] and pts[4][1]<pts[8][1] and pts[4][1]<pts[12][1] and pts[4][1]<pts[16][1] and pts[4][1]<pts[20][1] and pts[4][1]<pts[6][1] and pts[4][1]<pts[10][1] and pts[4][1]<pts[14][1] and pts[4][1]<pts[18][1]: ch1='Backspace'

        s = predict_sign
        if ch1 == 'next' and s.prev_char != 'next':
            prev = s.ten_prev[(s.count-2)%10]
            if prev != 'next':
                if prev == 'Backspace': s.sentence = s.sentence[:-1]
                elif prev != 'Backspace': s.sentence += prev
            else:
                p2 = s.ten_prev[s.count%10]
                if p2 != 'Backspace': s.sentence += p2
        if ch1 == '  ' and s.prev_char != '  ':
            s.sentence += '  '

        s.prev_char = ch1
        s.count += 1
        s.ten_prev[s.count % 10] = ch1

        word = s.sentence[s.sentence.rfind(' ')+1:]
        sugg = ['', '', '', '']
        if word.strip():
            try:
                sl = s.ddd.suggest(word)
                for i in range(min(4, len(sl))): sugg[i] = sl[i]
            except: pass

        return jsonify({"character": str(ch1), "sentence": s.sentence, "suggestions": sugg}), 200

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/check_camera_signal', methods=['GET'])
def check_camera_signal():
    """Endpoint for final_pred.py to check if it should start camera"""
    return jsonify(camera_signal), 200

@app.route('/api/reset_camera_signal', methods=['POST'])
def reset_camera_signal():
    """Reset the signal"""
    camera_signal["start"] = False
    return jsonify({"message": "Signal reset"}), 200

# Serve video files from output folder
@app.route('/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

@app.route('/text_to_sign', methods=['POST'])
def text_to_sign():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        print(f"Converting text to ISL: {text}")
        
        # Create ISL video from text
        output_filename = f"text_isl_{hash(text)}.mp4"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        isl_video = create_isl_video_from_text(text, output_path)
        
        if isl_video:
            video_url = f"http://127.0.0.1:5000/videos/{output_filename}"
            return jsonify({
                "message": "ISL video created successfully",
                "video_path": video_url,
                "text": text
            }), 200
        else:
            return jsonify({"error": "Failed to create ISL video"}), 500
            
    except Exception as e:
        print(f"Error in text_to_sign: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/process_video', methods=['POST'])
def process_video_request():
    try:
        # Retrieve the URL or search query from the request
        data = request.get_json()
        if 'url' in data:
            video_path = download_video_from_url(data['url'], OUTPUT_FOLDER)
        elif 'query' in data:
            video_path = search_and_download_video(data['query'], OUTPUT_FOLDER)
        else:
            return jsonify({"error": "No URL or query provided"}), 400

        if not video_path:
            return jsonify({"error": "Video download failed"}), 400

        # Transcribe the video
        transcription_result = transcribe_audio_with_whisper(video_path)
        
        if not transcription_result or not transcription_result.get('text'):
            print("Transcription failed. Returning original video...")
            video_filename = os.path.basename(video_path)
            video_url = f"http://127.0.0.1:5000/videos/{video_filename}"
            return jsonify({
                "message": "Video processed (transcription failed)", 
                "video_path": video_url,
                "transcription": ""
            }), 200
        
        transcription_text = transcription_result['text']
        print(f"Transcription: {transcription_text[:100]}...")
        
        # Create ISL video from transcribed text
        isl_video_filename = "isl_" + os.path.basename(video_path)
        isl_video_path = os.path.join(OUTPUT_FOLDER, isl_video_filename)
        
        isl_video = create_isl_video_from_text(transcription_text, isl_video_path)
        
        if isl_video:
            video_url = f"http://127.0.0.1:5000/videos/{isl_video_filename}"
        else:
            # Fallback to original video
            video_filename = os.path.basename(video_path)
            video_url = f"http://127.0.0.1:5000/videos/{video_filename}"
        
        return jsonify({
            "message": "ISL video created successfully", 
            "video_path": video_url,
            "transcription": transcription_text
        }), 200

    except Exception as e:
        print(f"Error processing video: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
def download_video_from_url(url, output_folder):
    try:
        options = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'noplaylist': True  # Only download single video, not playlist
        }
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            print(f"Video downloaded: {video_path}")
            return video_path
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

def search_and_download_video(query, output_folder):
    try:
        options = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'noplaylist': True
        }
        with YoutubeDL(options) as ydl:
            search_results = ydl.extract_info(f"ytsearch1:{query}", download=True)
            if search_results['entries']:
                video_info = search_results['entries'][0]
                video_path = ydl.prepare_filename(video_info)
                print(f"Video downloaded: {video_path}")
                return video_path
            else:
                print("No videos found for the search query.")
                return None
    except Exception as e:
        print(f"Error searching and downloading video: {e}")
        return None

def add_subtitles_to_video(video_path, transcription_result, output_path):
    """Add subtitles to video using FFmpeg"""
    try:
        print(f"Adding subtitles to video: {video_path}")
        
        # Get transcribed text
        text = transcription_result.get('text', '').strip()
        if not text:
            print("No text to add")
            return video_path
        
        # Create subtitle file (SRT format) with safe filename
        srt_filename = os.path.basename(output_path).replace('.mp4', '.srt')
        srt_path = os.path.join(OUTPUT_FOLDER, srt_filename)
        
        video = VideoFileClip(video_path)
        duration = video.duration
        video.close()
        
        # Simple subtitle: show full text for entire video duration
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write("1\n")
            f.write("00:00:00,000 --> " + format_time(duration) + "\n")
            f.write(text + "\n\n")
        
        # Escape paths for Windows
        srt_path_escaped = srt_path.replace('\\', '/').replace(':', '\\:')
        
        # Use FFmpeg to burn subtitles into video
        command = [
            'ffmpeg', '-i', video_path,
            '-vf', f"subtitles='{srt_path_escaped}':force_style='FontSize=24,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=3,Outline=2,Shadow=0,MarginV=50'",
            '-c:a', 'copy',
            '-y',
            output_path
        ]
        
        print(f"Running FFmpeg command...")
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Video with subtitles created: {output_path}")
            # Clean up subtitle file
            if os.path.exists(srt_path):
                os.remove(srt_path)
            return output_path
        else:
            print(f"FFmpeg failed, returning original video")
            print(f"Error: {result.stderr[:500]}")
            return video_path
            
    except Exception as e:
        print(f"Error adding subtitles: {e}")
        import traceback
        traceback.print_exc()
        return video_path

def format_time(seconds):
    """Convert seconds to SRT time format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def create_isl_video_from_text(text, output_path):
    """Create ISL sign language video from text using dataset images with captions"""
    try:
        print(f"Creating ISL video for text: {text[:50]}...")
        
        clips = []
        words = text.split()
        current_word = ""
        
        for word in words[:20]:  # Limit to first 20 words for performance
            word_clean = ''.join(c for c in word if c.isalnum()).upper()
            current_word = word_clean
            
            for char in word_clean:
                # Find ISL image for this character
                char_folder = os.path.join(ISL_DATASET_PATH, char)
                
                if os.path.exists(char_folder):
                    # Get random image from folder
                    images = glob.glob(os.path.join(char_folder, "*.jpg"))
                    if images:
                        img_path = random.choice(images)
                        # Create 2.5 second clip for each character (much slower)
                        # Resize to consistent 800x800 size
                        img_clip = ImageClip(img_path).set_duration(2.5).resize((800, 800))
                        
                        # Add text caption showing the letter and word
                        try:
                            txt_clip = TextClip(
                                f"{char}\n({current_word})",
                                font='Arial',
                                fontsize=60,
                                color='white',
                                bg_color='black',
                                size=(800, None)
                            ).set_duration(2.5).set_position(('center', 'bottom'))
                            
                            # Composite image with text
                            video_clip = CompositeVideoClip([img_clip, txt_clip])
                            clips.append(video_clip)
                        except:
                            # Fallback: just use image without text
                            clips.append(img_clip)
                        
                        print(f"Added ISL image for: {char}")
        
        if clips:
            # Concatenate all clips
            final_video = concatenate_videoclips(clips, method="compose")
            final_video.write_videofile(
                output_path,
                fps=20,
                codec='libx264',
                audio=False
            )
            final_video.close()
            print(f"ISL video created: {output_path}")
            return output_path
        else:
            print("No ISL images found for text")
            return None
            
    except Exception as e:
        print(f"Error creating ISL video: {e}")
        import traceback
        traceback.print_exc()
        return None

def transcribe_audio_with_whisper(video_path):
    """Transcribe audio using Whisper with word timestamps"""
    try:
        print(f"Transcribing with Whisper: {video_path}")
        result = whisper_model.transcribe(video_path, word_timestamps=True)
        print(f"Transcription complete: {result['text']}")
        return result
    except Exception as e:
        print(f"Whisper transcription error: {e}")
        return None

def process_video(input_video_path):
    print(f"Processing video: {input_video_path}")
    output_video_path = os.path.join(OUTPUT_FOLDER, "isl_" + os.path.basename(input_video_path))

    # Transcribe with Whisper
    transcription_result = transcribe_audio_with_whisper(input_video_path)
    
    if not transcription_result or not transcription_result.get('text'):
        print("Transcription failed. Returning original video...")
        return input_video_path
    
    print(f"Transcribed text: {transcription_result['text']}")
    
    # Add subtitles to video
    final_video = add_subtitles_to_video(input_video_path, transcription_result, output_video_path)
    
    return final_video

def main():
    print("Select an option:")
    print("1. Enter a YouTube URL")
    print("2. Search for a video on YouTube")
    choice = input("Enter your choice (1 or 2): ")

    if choice == "1":
        url = input("Enter the YouTube video URL: ")
        video_path = download_video_from_url(url, OUTPUT_FOLDER)
    elif choice == "2":
        query = input("Enter the search query: ")
        video_path = search_and_download_video(query, OUTPUT_FOLDER)
    else:
        print("Invalid choice. Exiting.")
        return

    if video_path:
        final_video = process_video(video_path)
        if final_video:
            print(f"Sign language video created: {final_video}")
        else:
            print("Failed to create sign language video.")
    else:
        print("No video processed.")
@app.route('/upload_video', methods=['POST'])
def upload_video():
    try:
        video_file = request.files['video']
        video_path = os.path.join(OUTPUT_FOLDER, video_file.filename)
        video_file.save(video_path)
        
        final_video = process_video(video_path)

        if final_video:
            return jsonify({"message": "Sign language video created", "video_path": final_video}), 200
        else:
            return jsonify({"error": "Failed to create sign language video"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/isl_image/<letter>', methods=['GET'])
def get_isl_image(letter):
    """Serve a random ISL image for a given letter"""
    try:
        letter = letter.upper()
        char_folder = os.path.join(ISL_DATASET_PATH, letter)
        
        if os.path.exists(char_folder):
            images = glob.glob(os.path.join(char_folder, "*.jpg"))
            if images:
                img_path = random.choice(images)
                return send_from_directory(os.path.dirname(img_path), os.path.basename(img_path))
        
        return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        print(f"Error serving ISL image: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=3002)
