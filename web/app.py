import cv2
import mediapipe as mp
import random
import threading
import time
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

# Initialize Mediapipe Face Mesh for detection
mp_face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

# Define actions
actions = ["Look Left", "Look Right", "Blink", "Open Mouth"]
selected_actions = random.sample(actions, 2)
action_index = 0
action_completed = {action: False for action in selected_actions}
current_action = ""
action_status = "Waiting"
timer_running = False
initial_nose_x = None  # Store initial nose position

# Video Capture
cap = cv2.VideoCapture(0)

def detect_action(frame):
    global action_completed, action_status, current_action, initial_nose_x

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = mp_face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        nose_x = landmarks[1].x  # Nose tip position
        
        # Set the initial nose position when an action starts
        if initial_nose_x is None and (current_action == "Look Left" or current_action == "Look Right"):
            initial_nose_x = nose_x

        # **Look Left Detection**
        if current_action == "Look Left" and not action_completed["Look Left"]:
            if nose_x - initial_nose_x > 0.06:  # Detects rightward movement
                action_completed["Look Left"] = True
                action_status = "Action Done"

        # **Look Right Detection**
        if current_action == "Look Right" and not action_completed["Look Right"]:
            if initial_nose_x - nose_x > 0.06:  # Detects leftward movement
                action_completed["Look Right"] = True
                action_status = "Action Done"

        # **Blink Detection**
        if current_action == "Blink" and not action_completed["Blink"]:
            left_eye_top = landmarks[159].y
            left_eye_bottom = landmarks[145].y
            right_eye_top = landmarks[386].y
            right_eye_bottom = landmarks[374].y
            eye_threshold = 0.02  
            
            if (abs(left_eye_top - left_eye_bottom) < eye_threshold and 
                abs(right_eye_top - right_eye_bottom) < eye_threshold):
                action_completed["Blink"] = True
                action_status = "Action Done"

        # **Open Mouth Detection**
        if current_action == "Open Mouth" and not action_completed["Open Mouth"]:
            upper_lip = landmarks[13].y
            lower_lip = landmarks[14].y
            if abs(upper_lip - lower_lip) > 0.05:  
                action_completed["Open Mouth"] = True
                action_status = "Action Done"

def video_feed():
    while True:
        success, frame = cap.read()
        if not success:
            continue

        detect_action(frame)

        # Draw face mesh
        results = mp_face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(frame, face_landmarks)

        # Show Action Text
        cv2.putText(frame, f"Action: {current_action}", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Status: {action_status}", (50, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # Encode frame
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(video_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start')
def start_liveness():
    global action_index, action_completed, current_action, action_status, timer_running, initial_nose_x

    action_index = 0
    action_completed = {action: False for action in selected_actions}
    
    def run_liveness():
        global action_index, current_action, action_status, timer_running, initial_nose_x

        for i in range(len(selected_actions)):
            current_action = selected_actions[action_index]
            action_status = "Waiting for action..."
            timer_running = True
            initial_nose_x = None  # Reset nose position for new action
            start_time = time.time()

            while time.time() - start_time < 5:
                if action_completed[current_action]:
                    break  # Stop waiting if user completes action
            
            # Check if action was completed
            if action_completed[current_action]:
                action_status = "Action Done"
            else:
                action_status = "Action Failed"

            time.sleep(2)  # Pause before showing next command
            action_index += 1

        # Check final result
        passed = sum(action_completed.values()) >= 2
        app.config['LIVENESS_RESULT'] = "Verified" if passed else "Failed"

    threading.Thread(target=run_liveness).start()
    return jsonify({"status": "Started", "actions": selected_actions})

@app.route('/status')
def action_status_update():
    return jsonify({"current_action": current_action, "status": action_status})

@app.route('/result')
def get_result():
    return jsonify({"result": app.config.get('LIVENESS_RESULT', "Pending")})

if __name__ == '__main__':
    app.run(debug=True)
