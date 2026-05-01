# 🤟 ASL Sign Language Interpreter

A real-time American Sign Language (ASL) interpreter that runs in your browser. It uses your webcam to detect hand gestures and builds a live transcript as you sign.

**Live Demo:** [sign-language-interpreter-1-bg66.onrender.com](https://sign-language-interpreter-1-bg66.onrender.com)

---

## Preview

![App Screenshot](screenshot.png)

---

## Features

- Real-time hand landmark detection using MediaPipe
- Recognizes ASL letters and numbers: A, B, D, I, L, V, W, Y, 1, 2, 3, 4, 5
- Hold-to-confirm system: hold a sign for 1.5 seconds to add the letter
- Live progress bar so you know when a letter will be added
- Built-in sign reference guide always visible on screen
- Space, Delete, Clear and Copy buttons to edit your transcript
- Clean dark UI that runs entirely in the browser

---

## Supported Signs

| Letter | How to sign it |
|--------|----------------|
| A | Fist, all fingers closed |
| B | 4 fingers up, thumb tucked in |
| D | Only index finger up |
| I | Only pinky up |
| L | Thumb and index up, L shape |
| V | Index and middle up, peace sign |
| W | Index, middle and ring up |
| Y | Thumb and pinky out |
| 1 | Index finger only |
| 2 | Index and middle |
| 3 | Index, middle and ring |
| 4 | Four fingers, no thumb |
| 5 | All five fingers open |

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/rahim-adnan/sign-language-interpreter.git
cd sign-language-interpreter
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser. The hand landmarker model downloads automatically on first run (~8 MB).

---

## How It Works

1. Your browser captures webcam frames and sends them to the Flask server
2. MediaPipe detects 21 hand landmark points on each frame
3. The server checks which fingers are up or down
4. The finger combination maps to an ASL letter
5. Hold a sign for 1.5 seconds and the letter is added to the transcript

---

## Project Structure

```
sign-language-interpreter/
├── app.py                  # Flask server and gesture recognition
├── Dockerfile              # Container config for deployment
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Browser UI
├── hand_landmarker.task    # MediaPipe model (auto-downloaded)
└── README.md
```

---

## Built With

- [MediaPipe](https://mediapipe.dev) — hand landmark detection
- [OpenCV](https://opencv.org) — image processing
- [Flask](https://flask.palletsprojects.com) — web server
- [NumPy](https://numpy.org) — frame processing

---

## Author

**Rahim Adnan**
[Portfolio](https://rahim-adnan.github.io) . [GitHub](https://github.com/rahim-adnan)

---

## License

MIT — free to use and modify.