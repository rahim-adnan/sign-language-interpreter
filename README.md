# 🤟 ASL Sign Language Interpreter

A real-time American Sign Language (ASL) interpreter built with Python, MediaPipe, and OpenCV. It detects your hand via webcam, identifies ASL letters from your finger positions, and builds a live transcript as you sign.

---

## Demo

> Hold a sign for ~1.5 seconds → the letter locks in → transcript builds up in real time.

![demo placeholder](https://via.placeholder.com/800x400?text=Add+a+screenshot+or+GIF+here)

---

## Features

- 🖐️ Real-time hand landmark detection (21 points) via MediaPipe
- 🔤 Recognizes ASL letters: A, B, D, I, L, V, W, Y and more
- 📊 Live finger state indicators (which fingers are up/down)
- 📝 Live transcript with word-wrap display
- ⏱️ Hold-to-confirm system prevents accidental letter spam
- 🎨 Clean dark UI with side panel — no browser needed

---

## Supported Signs

| Sign | Letter | Description |
|------|--------|-------------|
| ✊ Fist | A | All fingers closed |
| 🖐️ Flat hand | B | All 4 fingers up, thumb tucked |
| ☝️ Index only | D | Only index finger up |
| 🤙 Thumb + pinky | Y | Thumb and pinky extended |
| ✌️ Index + middle | V | Peace sign |
| 🤘 Index + pinky | I | Pinky only up |
| 👆 Thumb + index | L | L shape |
| 🖖 Three fingers | W | Index, middle, ring up |

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/sign-language-interpreter.git
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
pip install mediapipe==0.10.33 opencv-python numpy
```

### 4. Run the app

```bash
python app.py
```

The hand landmarker model (`hand_landmarker.task`) will download automatically on first run (~8 MB).

---

## Controls

| Key | Action |
|-----|--------|
| `Space` | Add a space to transcript |
| `Backspace` | Delete last character |
| `C` | Clear entire transcript |
| `Q` | Quit and print final transcript |

---

## Project Structure

```
sign-language-interpreter/
│
├── app.py                  # Main application
├── hand_landmarker.task    # MediaPipe model (auto-downloaded)
└── README.md
```

---

## How It Works

1. **Webcam capture** — OpenCV grabs each frame from your camera
2. **Hand detection** — MediaPipe finds 21 landmark points on your hand
3. **Finger state** — each finger is checked: is the tip higher than the knuckle?
4. **Gesture mapping** — the combination of up/down fingers maps to an ASL letter
5. **Hold to confirm** — a progress bar fills over 1.5s, then the letter is added to the transcript

---

## Built With

- [MediaPipe](https://mediapipe.dev/) — hand landmark detection
- [OpenCV](https://opencv.org/) — webcam capture and UI rendering
- [NumPy](https://numpy.org/) — frame compositing

---

## Author

**Rahim Adnan**  
[Portfolio](https://rahim-adnan.github.io) · [GitHub](https://github.com/YOUR_USERNAME)

---

## License

MIT — free to use and modify.