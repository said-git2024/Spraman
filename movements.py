import cv2
import mediapipe as mp
import numpy as np
import time

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Initialize webcam
cap = cv2.VideoCapture(0)

# Get frame size
success, temp_frame = cap.read()
if success:
    frame_height, frame_width, _ = temp_frame.shape
else:
    frame_height, frame_width = 480, 640  # Default fallback dimensions

# Variables for gesture detection
head_pos_history = []
history_length = 3  
current_command = "None"  
command_start_time = time.time()
command_cooldown = 0.8  

# Calibration
calibration_done = False
neutral_x = 0
neutral_y = 0
calibration_samples = []
calibration_sample_count = 30  

# FaceMesh Model Setup
with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh:
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Failed to capture image.")
            break
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(image_rgb)
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Draw face landmarks
                mp_drawing.draw_landmarks(
                    image=image, 
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None, 
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
                )
                
                # Get key landmarks
                nose_tip = face_landmarks.landmark[4]
                left_eye = face_landmarks.landmark[33]
                right_eye = face_landmarks.landmark[263]
                left_eye_top = face_landmarks.landmark[159]
                left_eye_bottom = face_landmarks.landmark[145]
                right_eye_top = face_landmarks.landmark[386]
                right_eye_bottom = face_landmarks.landmark[374]
                upper_lip = face_landmarks.landmark[13]
                lower_lip = face_landmarks.landmark[14]

                # Calculate face height (distance from forehead to chin)
                face_height = abs(face_landmarks.landmark[10].y - face_landmarks.landmark[152].y)

                # Compute head orientation
                eye_center_x = (left_eye.x + right_eye.x) / 2
                eye_center_y = (left_eye.y + right_eye.y) / 2
                x_orientation = nose_tip.x - eye_center_x
                y_orientation = nose_tip.y - eye_center_y

                # Calibration
                if not calibration_done:
                    cv2.putText(image, "Look straight for calibration", 
                               (10, frame_height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                    if len(calibration_samples) < calibration_sample_count:
                        calibration_samples.append((x_orientation, y_orientation))
                        cv2.putText(image, f"Calibrating: {len(calibration_samples)}/{calibration_sample_count}", 
                                   (10, frame_height - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    else:
                        # Average neutral position
                        neutral_x = sum(sample[0] for sample in calibration_samples) / len(calibration_samples)
                        neutral_y = sum(sample[1] for sample in calibration_samples) / len(calibration_samples)
                        calibration_done = True
                        print(f"Calibration complete. Neutral X: {neutral_x:.4f}, Neutral Y: {neutral_y:.4f}")
                
                else:
                    # Adjust head position
                    adjusted_x = x_orientation - neutral_x
                    adjusted_y = y_orientation - neutral_y

                    # Store in history for smooth detection
                    head_pos_history.append((adjusted_x, adjusted_y))
                    if len(head_pos_history) > history_length:
                        head_pos_history.pop(0)

                    avg_x = sum(pos[0] for pos in head_pos_history) / len(head_pos_history)
                    avg_y = sum(pos[1] for pos in head_pos_history) / len(head_pos_history)

                    # Eye blink detection
                    left_eye_dist = abs(left_eye_top.y - left_eye_bottom.y) / face_height
                    right_eye_dist = abs(right_eye_top.y - right_eye_bottom.y) / face_height

                    # Mouth open detection
                    mouth_dist = abs(upper_lip.y - lower_lip.y) / face_height

                    # Gesture thresholds (Updated for accuracy)
                    x_threshold = 0.015  
                    y_threshold = 0.015  
                    blink_threshold = 0.018
                    mouth_threshold = 0.05

                    # Determine gesture command
                    current_time = time.time()
                    new_command = "None"

                    if left_eye_dist < blink_threshold and right_eye_dist < blink_threshold:
                        new_command = "Eye Blink"
                    elif mouth_dist > mouth_threshold:
                        new_command = "Mouth Open"
                    elif avg_x < -x_threshold:
                        new_command = "Left"
                    elif avg_x > x_threshold:
                        new_command = "Right"
                    elif avg_y < -y_threshold:
                        new_command = "Up"
                    elif avg_y > y_threshold:
                        new_command = "Down"

                    # Prevent repeating the same command if not changed
                    if new_command != current_command and current_time - command_start_time > command_cooldown:
                        current_command = new_command
                        command_start_time = current_time
                        print(f"Command: {current_command}")

                    # Ensure "None" is printed when no action is performed
                    if new_command == "None":
                        print("Command: None")

                    # Display gesture results
                    cv2.putText(image, f"Command: {current_command}", (10, 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Show frame
        cv2.imshow("Face Gesture Commands", image)

        # Quit on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Cleanup
cap.release()
cv2.destroyAllWindows()
