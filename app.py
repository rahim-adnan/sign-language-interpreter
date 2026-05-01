import cv2
import mediapipe as mp
import os
import urllib.request
import time
import numpy as np

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

MODEL_PATH = "hand_landmarker.task"
if not os.path.exists(MODEL_PATH):
    print("Downloading hand landmarker model...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task",
        MODEL_PATH
    )

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)

CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17)
]

# ── Colours (BGR) ──────────────────────────────────────────────
C_BG        = (18,  18,  18)
C_PANEL     = (30,  30,  30)
C_ACCENT    = (0,  210, 120)   # green
C_ACCENT2   = (0,  180, 255)   # blue
C_TEXT      = (240, 240, 240)
C_SUBTEXT   = (130, 130, 130)
C_YELLOW    = (0,  230, 255)
C_BAR_BG    = (50,  50,  50)

def get_fingers_up(lm):
    fingers = []
    fingers.append(lm[4].x < lm[3].x)
    fingers.append(lm[8].y  < lm[6].y)
    fingers.append(lm[12].y < lm[10].y)
    fingers.append(lm[16].y < lm[14].y)
    fingers.append(lm[20].y < lm[18].y)
    return fingers

def recognize(lm):
    f = get_fingers_up(lm)
    thumb, index, middle, ring, pinky = f
    if not any(f):                                               return "A"
    if not thumb and index and middle and ring and pinky:        return "B"
    if thumb and index and not middle and not ring and not pinky: return "L"
    if not thumb and index and not middle and not ring and not pinky: return "D"
    if not thumb and index and middle and not ring and not pinky: return "V"
    if not thumb and not index and not middle and not ring and pinky: return "I"
    if thumb and not index and not middle and not ring and pinky: return "Y"
    if not thumb and index and middle and ring and not pinky:    return "W"
    if all(f):                                                   return "5"
    return "?"

def draw_rounded_rect(img, x1, y1, x2, y2, color, radius=12, thickness=-1):
    """Draw a filled rounded rectangle."""
    cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, thickness)
    cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, thickness)
    cv2.circle(img, (x1 + radius, y1 + radius), radius, color, thickness)
    cv2.circle(img, (x2 - radius, y1 + radius), radius, color, thickness)
    cv2.circle(img, (x1 + radius, y2 - radius), radius, color, thickness)
    cv2.circle(img, (x2 - radius, y2 - radius), radius, color, thickness)

def draw_finger_indicators(panel, fingers, px, py):
    """Draw 5 finger up/down dots in the side panel."""
    labels = ["T", "I", "M", "R", "P"]
    for i, (label, up) in enumerate(zip(labels, fingers)):
        color = C_ACCENT if up else C_BAR_BG
        cx = px + i * 38
        cv2.circle(panel, (cx, py), 14, color, -1)
        cv2.putText(panel, label, (cx - 7, py + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, C_TEXT, 1)

# ── Layout ─────────────────────────────────────────────────────
CAM_W, CAM_H = 800, 600
PANEL_W = 280
WIN_W = CAM_W + PANEL_W
WIN_H = CAM_H

transcript = ""
last_letter = ""
last_add_time = 0
LETTER_DELAY = 1.5
history = []          # list of (letter, timestamp) for the log

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)

with HandLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (CAM_W, CAM_H))
        now = time.time()

        # ── Detect ──────────────────────────────────────────────
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = landmarker.detect(mp_image)

        current_letter = ""
        fingers = [False] * 5

        if result.hand_landmarks:
            for hand_landmark in result.hand_landmarks:
                pts = [(int(lm.x * CAM_W), int(lm.y * CAM_H)) for lm in hand_landmark]

                # Draw skeleton
                for a, b in CONNECTIONS:
                    cv2.line(frame, pts[a], pts[b], C_ACCENT, 2)
                for cx, cy in pts:
                    cv2.circle(frame, (cx, cy), 6, C_ACCENT, -1)
                    cv2.circle(frame, (cx, cy), 3, (255, 255, 255), -1)

                current_letter = recognize(hand_landmark)
                fingers = get_fingers_up(hand_landmark)

                # Add letter when hold completes
                needed = LETTER_DELAY
                hold = now - last_add_time
                if hold >= needed and current_letter != "?" and current_letter != last_letter:
                    transcript += current_letter
                    last_letter = current_letter
                    last_add_time = now
                    history.append(current_letter)
                    if len(history) > 8:
                        history.pop(0)
                elif hold >= needed and current_letter != "?" and current_letter == last_letter:
                    # allow repeat after double the delay
                    if hold >= needed * 2:
                        transcript += current_letter
                        last_add_time = now
                        history.append(current_letter)
                        if len(history) > 8:
                            history.pop(0)

        # ── Overlay on camera frame ──────────────────────────────
        # Top bar on video
        cv2.rectangle(frame, (0, 0), (CAM_W, 50), (0, 0, 0), -1)
        cv2.putText(frame, "ASL Sign Language Interpreter", (12, 33),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, C_ACCENT, 2)

        # Hold progress bar on video (bottom)
        if current_letter and current_letter != "?":
            hold = min(now - last_add_time, LETTER_DELAY)
            progress = hold / LETTER_DELAY
            bar_total = CAM_W - 40
            bar_filled = int(bar_total * progress)
            cv2.rectangle(frame, (20, CAM_H - 25), (20 + bar_total, CAM_H - 10), C_BAR_BG, -1)
            cv2.rectangle(frame, (20, CAM_H - 25), (20 + bar_filled, CAM_H - 10), C_ACCENT, -1)
            cv2.putText(frame, f"Holding: {current_letter}  ({int(progress*100)}%)",
                        (20, CAM_H - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_SUBTEXT, 1)

        # ── Side panel ──────────────────────────────────────────
        panel = np.full((WIN_H, PANEL_W, 3), C_PANEL, dtype=np.uint8)

        # Current letter display
        cv2.putText(panel, "DETECTED", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_SUBTEXT, 1)
        letter_display = current_letter if current_letter else "-"
        color = C_YELLOW if current_letter and current_letter != "?" else C_SUBTEXT
        cv2.putText(panel, letter_display, (90, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 5, color, 8)

        # Finger indicators
        cv2.putText(panel, "FINGERS", (20, 185),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, C_SUBTEXT, 1)
        draw_finger_indicators(panel, fingers, 30, 210)

        # Divider
        cv2.line(panel, (20, 240), (PANEL_W - 20, 240), C_BAR_BG, 1)

        # Recent letters log
        cv2.putText(panel, "RECENT", (20, 270),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, C_SUBTEXT, 1)
        for i, ch in enumerate(history[-6:]):
            alpha = 0.4 + 0.1 * i
            shade = tuple(int(c * alpha) for c in C_ACCENT2)
            cv2.putText(panel, ch, (20 + i * 38, 310),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, shade, 2)

        # Divider
        cv2.line(panel, (20, 330), (PANEL_W - 20, 330), C_BAR_BG, 1)

        # Transcript
        cv2.putText(panel, "TRANSCRIPT", (20, 360),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, C_SUBTEXT, 1)

        # Word-wrap transcript into 2 lines of ~14 chars
        words = transcript[-28:] if len(transcript) > 28 else transcript
        line1 = words[:14]
        line2 = words[14:]
        cv2.putText(panel, line1 + ("|" if not line2 else ""), (20, 395),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, C_TEXT, 2)
        if line2:
            cv2.putText(panel, line2 + "|", (20, 425),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, C_TEXT, 2)

        # Divider
        cv2.line(panel, (20, 450), (PANEL_W - 20, 450), C_BAR_BG, 1)

        # Controls
        cv2.putText(panel, "CONTROLS", (20, 478),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, C_SUBTEXT, 1)
        controls = ["SPACE  add space", "BKSP   delete", "C      clear all", "Q      quit"]
        for i, ctrl in enumerate(controls):
            cv2.putText(panel, ctrl, (20, 505 + i * 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, C_SUBTEXT, 1)

        # ── Combine frame + panel ────────────────────────────────
        canvas = np.zeros((WIN_H, WIN_W, 3), dtype=np.uint8)
        canvas[:, :CAM_W] = frame
        canvas[:, CAM_W:] = panel

        cv2.imshow("ASL Sign Language Interpreter", canvas)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            transcript += " "
        elif key == 8:   # backspace
            transcript = transcript[:-1]
        elif key == ord('c'):
            transcript = ""
            history = []

cap.release()
cv2.destroyAllWindows()
print("\n📝 Final transcript:", transcript)