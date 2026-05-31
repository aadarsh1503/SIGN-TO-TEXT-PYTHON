from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
import mediapipe as mp
import math
import io
from PIL import Image
import enchant

app = Flask(__name__)
CORS(app)

# Initialize spell checker
try:
    spell_checker = enchant.Dict("en-US")
except:
    spell_checker = None

# Load the trained model
try:
    model = keras.models.load_model('../cnn8grps_rad1_model.h5')
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def distance(x, y):
    return math.sqrt(((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2))

def process_landmarks(landmarks, img_width, img_height):
    """Convert MediaPipe landmarks to pixel coordinates"""
    pts = []
    for lm in landmarks.landmark:
        x = int(lm.x * img_width)
        y = int(lm.y * img_height)
        pts.append([x, y])
    return pts

def create_skeleton_image(pts, bbox):
    """Create skeleton image from hand landmarks"""
    white = np.ones((400, 400, 3), dtype=np.uint8) * 255
    
    if not pts or len(pts) < 21:
        return white
    
    x, y, w, h = bbox
    os = ((400 - w) // 2) - 15
    os1 = ((400 - h) // 2) - 15
    
    # Draw connections between landmarks
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),  # thumb
        (5, 6), (6, 7), (7, 8),          # index
        (9, 10), (10, 11), (11, 12),     # middle
        (13, 14), (14, 15), (15, 16),    # ring
        (17, 18), (18, 19), (19, 20),    # pinky
        (5, 9), (9, 13), (13, 17),       # palm connections
        (0, 5), (0, 17)                  # wrist connections
    ]
    
    # Draw lines
    for start, end in connections:
        if start < len(pts) and end < len(pts):
            start_point = (pts[start][0] + os, pts[start][1] + os1)
            end_point = (pts[end][0] + os, pts[end][1] + os1)
            cv2.line(white, start_point, end_point, (0, 255, 0), 3)
    
    # Draw circles for landmarks
    for i, pt in enumerate(pts):
        cv2.circle(white, (pt[0] + os, pt[1] + os1), 2, (0, 0, 255), 1)
    
    return white

def classify_gesture(ch1, ch2, pts):
    """Classify gesture based on model output and hand landmarks"""
    if not pts or len(pts) < 21:
        return "?"
    
    # Apply the same classification logic as the original code
    pl = [ch1, ch2]
    
    # Simplified version of the original classification rules
    # condition for [Aemnst]
    l = [[5,2],[5,3],[3,5],[3,6],[3,0],[3,2],[6,4],[6,1],[6,2],[6,6],[6,7],[6,0],[6,5],[4,1],[1,0],[1,1],[6,3],[1,6],[5,6],[5,1],[4,5],[1,4],[1,5],[2,0],[2,6],[4,6],[1,0],[5,7],[1,6],[6,1],[7,6],[2,5],[7,1],[5,4],[7,0],[7,5],[7,2]]
    if pl in l:
        if (pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 0
    
    # Apply subgroup classification
    if ch1 == 0:
        ch1 = 'S'
        if pts[4][0] < pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0]:
            ch1 = 'A'
        elif pts[4][1] > pts[8][1] and pts[4][1] > pts[12][1] and pts[4][1] > pts[16][1] and pts[4][1] > pts[20][1]:
            ch1 = 'E'
        elif pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][0] > pts[14][0] and pts[4][1] < pts[18][1]:
            ch1 = 'M'
        elif pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][1] < pts[18][1] and pts[4][1] < pts[14][1]:
            ch1 = 'N'
        elif pts[4][0] > pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0] and pts[4][1] < pts[14][1] and pts[4][1] < pts[18][1]:
            ch1 = 'T'
    
    elif ch1 == 2:
        if distance(pts[12], pts[4]) > 42:
            ch1 = 'C'
        else:
            ch1 = 'O'
    
    elif ch1 == 3:
        if distance(pts[8], pts[12]) > 72:
            ch1 = 'G'
        else:
            ch1 = 'H'
    
    elif ch1 == 7:
        if distance(pts[8], pts[4]) > 42:
            ch1 = 'Y'
        else:
            ch1 = 'J'
    
    elif ch1 == 4:
        ch1 = 'L'
    
    elif ch1 == 6:
        ch1 = 'X'
    
    elif ch1 == 5:
        if pts[4][0] > pts[12][0] and pts[4][0] > pts[16][0] and pts[4][0] > pts[20][0]:
            if pts[8][1] < pts[5][1]:
                ch1 = 'Z'
            else:
                ch1 = 'Q'
        else:
            ch1 = 'P'
    
    elif ch1 == 1:
        if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 'B'
        elif (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 'D'
        elif (pts[6][1] < pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 'F'
        elif (pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 'I'
        elif (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 'W'
        elif (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and pts[4][1] < pts[9][1]:
            ch1 = 'K'
        elif ((distance(pts[8], pts[12]) - distance(pts[6], pts[10])) < 8) and (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 'U'
        elif ((distance(pts[8], pts[12]) - distance(pts[6], pts[10])) >= 8) and (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[4][1] > pts[9][1]):
            ch1 = 'V'
        elif (pts[8][0] > pts[12][0]) and (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 'R'
    
    return str(ch1)

def get_word_suggestions(partial_word):
    """Get word suggestions for partial word"""
    if not spell_checker or not partial_word:
        return []
    
    suggestions = []
    try:
        # Get suggestions from spell checker
        if len(partial_word) >= 2:
            spell_suggestions = spell_checker.suggest(partial_word)
            suggestions.extend(spell_suggestions[:4])  # Top 4 suggestions
    except:
        pass
    
    return suggestions

@app.route('/predict_gesture', methods=['POST'])
def predict_gesture():
    try:
        if 'frame' not in request.files:
            return jsonify({'error': 'No frame provided'}), 400
        
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Read image from request
        file = request.files['frame']
        image_bytes = file.read()
        
        # Convert to OpenCV format
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        # Process frame with MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get hand landmarks
                h, w, c = frame.shape
                pts = process_landmarks(hand_landmarks, w, h)
                
                # Calculate bounding box
                x_coords = [pt[0] for pt in pts]
                y_coords = [pt[1] for pt in pts]
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                bbox = [x_min, y_min, x_max - x_min, y_max - y_min]
                
                # Create skeleton image
                skeleton_img = create_skeleton_image(pts, bbox)
                
                # Predict gesture
                img_array = skeleton_img.reshape(1, 400, 400, 3)
                img_array = img_array.astype('float32') / 255.0
                
                prediction = model.predict(img_array, verbose=0)
                prob = np.array(prediction[0], dtype='float32')
                
                # Get top predictions
                ch1 = np.argmax(prob)
                confidence = float(prob[ch1])
                prob[ch1] = 0
                ch2 = np.argmax(prob)
                
                # Classify gesture
                predicted_char = classify_gesture(ch1, ch2, pts)
                
                # Get word suggestions (dummy for now)
                suggestions = get_word_suggestions(predicted_char)
                
                return jsonify({
                    'gesture': predicted_char,
                    'confidence': confidence,
                    'suggestions': suggestions
                })
        
        return jsonify({
            'gesture': '',
            'confidence': 0.0,
            'suggestions': []
        })
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'mediapipe_ready': True
    })

if __name__ == '__main__':
    print("Starting Sign Recognition API...")
    print("Model loaded:", model is not None)
    app.run(host='127.0.0.1', port=5001, debug=True)