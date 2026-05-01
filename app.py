from flask import Flask, render_template, request, jsonify
import mediapipe as mp
import numpy as np
import base64
import cv2
import os
import urllib.request
import threading

app = Flask(__name__)

MODEL_PATH = "hand_landmarker.task"
if not os.path.exists(MODEL_PATH):
    print("Downloading hand landmarker model...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task",
        MODEL_PATH
    )
    print("Model downloaded.")

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)

landmarker = HandLandmarker.create_from_options(options)

def get_fingers_up(lm):
    return [
        lm[4].x  < lm[3].x,
        lm[8].y  < lm[6].y,
        lm[12].y < lm[10].y,
        lm[16].y < lm[14].y,
        lm[20].y < lm[18].y,
    ]

def recognize(lm):
    f = get_fingers_up(lm)
    thumb, index, middle, ring, pinky = f

    if not any(f):                                                       return "A"
    if not thumb and index and middle and ring and pinky:                return "B"
    if thumb and index and not middle and not ring and not pinky:        return "L"
    if not thumb and index and not middle and not ring and not pinky:    return "D"
    if not thumb and index and middle and not ring and not pinky:        return "V"
    if not thumb and not index and not middle and not ring and pinky:    return "I"
    if thumb and not index and not middle and not ring and pinky:        return "Y"
    if not thumb and index and middle and ring and not pinky:            return "W"
    if not thumb and index and middle and ring and pinky:                return "4"
    if thumb and index and middle and ring and pinky:                    return "5"
    return "?"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/detect", methods=["POST"])
def detect():
    data = request.json.get("image", "")
    _, encoded = data.split(",", 1)
    img_bytes = base64.b64decode(encoded)
    frame = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"letter": "", "fingers": [False]*5, "landmarks": []})

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = landmarker.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))

    if result.hand_landmarks:
        lm = result.hand_landmarks[0]
        h, w = frame.shape[:2]
        return jsonify({
            "letter": recognize(lm),
            "fingers": get_fingers_up(lm),
            "landmarks": [{"x": int(l.x*w), "y": int(l.y*h)} for l in lm]
        })

    return jsonify({"letter": "", "fingers": [False]*5, "landmarks": []})

@app.route("/quit", methods=["POST"])
def quit_app():
    def shutdown():
        import time; time.sleep(0.5)
        os._exit(0)
    threading.Thread(target=shutdown).start()
    return jsonify({"status": "shutting down"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)