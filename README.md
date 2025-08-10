This line is written by KI
# Spraman
🔐 Face Liveness Detection A multi-factor face liveness detection system using blink detection, reflection analysis, and movement verification to prevent spoofing and ensure real user presence.

# 👁️ Intelligent Liveness Detection System

A robust, multi-modal liveness detection system that utilizes computer vision techniques like blink detection, reflection analysis, facial gestures, and a web-based interactive demo using Flask and MediaPipe. Designed to prevent spoofing attempts and enhance security in real-time facial verification systems.

---

## 📌 Project Overview

This system verifies user liveness using multiple methods:

- 🔴 **Red light reflection test** (for screen spoofing defense)
- 👁️ **Eye blink detection** using EAR (Eye Aspect Ratio)
- 🧠 **Gesture recognition** via facial mesh (blink, mouth open, head movement)
- 🌐 **Web-based interactive demo** with randomized challenges

---

## ✨ Features

- ✅ Real-time blink detection  
- ✅ Red-screen eye reflection analysis  
- ✅ Head and facial gesture recognition  
- ✅ Randomized user challenge interface  
- ✅ Flask-based web interface with live video feed  
- ✅ Calibration for improved gesture accuracy  
- ✅ User feedback and visual cues  

---

## 🔧 Technologies Used

- Python 3  
- OpenCV  
- dlib (for facial landmarks)  
- MediaPipe (face mesh + gesture tracking)  
- Flask (web interface)  
- Pygame (screen control for brightness/reflection)  
- Screen Brightness Control (`screen_brightness_control`)  
- Tkinter (popup message UI)  
- HTML / JavaScript (for simple web interface)  

---

## ⚙️ How It Works

### 🔴 1. Red-Screen Reflection Detection

- Switches screen background to red using `pygame`
- Uses `dlib` to isolate the eye region
- Calculates red pixel ratio from HSV color space
- Detects light reflection intensity in the eyes

### 👁️ 2. Blink Detection (EAR Method)

- Calculates Eye Aspect Ratio (EAR) from facial landmarks
- Detects a blink when EAR falls below a threshold
- Smooths EAR with moving average for better accuracy

### 🧠 3. Gesture Recognition (MediaPipe Face Mesh)

- Tracks facial landmarks using MediaPipe
- Measures:
  - Head direction (left/right/up/down)
  - Eye blinks
  - Mouth openness
- Interprets them as commands or challenges

### 🌐 4. Web Interface

- Flask server serves live webcam feed
- Generates 2 random actions
- Waits for user to complete them in real time
- Uses MediaPipe for real-time tracking

---

## 🚀 Setup Instructions

1. **Clone the repository**

    ```bash
    git clone https://github.com/your-repo/liveness-detection.git
    cd liveness-detection
    ```

2. **Install requirements**

    ```bash
    pip install -r requirements.txt
    ```

3. **Download Dlib model**

    - Download `shape_predictor_68_face_landmarks.dat`
    - Extract and place it in your project directory
    - Update the path in the code if necessary

4. **Run the scripts**

    - **Blink detection**  
        ```bash
        python blink_detector.py
        ```

    - **Reflection test**  
        ```bash
        python reflection_test.py
        ```

    - **Gesture-based demo**  
        ```bash
        python gesture_command.py
        ```

    - **Web interface**  
        ```bash
        python app.py
        ```

---

## 🎮 Usage

- Run the desired verification module
- For web mode, visit:  
  [http://127.0.0.1:5000](http://127.0.0.1:5000)  
- Click “Start” to begin the liveness test
- Perform actions shown on screen (e.g., blink, open mouth, etc.)

---

## 🔮 Future Improvements

- Add spoof attack detection (photo or video replay)
- Support mobile camera integration
- Improve robustness under different lighting conditions
- Expand gesture library (e.g., nod, tilt)
- Add face anti-spoofing CNN models
- Save test logs and timestamps
- Deploy on cloud (Heroku, Firebase, GCP)

---




