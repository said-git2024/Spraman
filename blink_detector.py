import cv2
import dlib
import numpy as np
from scipy.spatial import distance

# Load dlib face detector and landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(r"C:\Users\LOQ\Documents\code\FLD\shape_predictor_68_face_landmarks.dat")

# Function to compute Eye Aspect Ratio (EAR)
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

# Blink detection parameters
BLINK_THRESHOLD = 0.24  # Adjust as needed
BLINK_FRAMES = 3  # Number of consecutive frames for a valid blink
frame_counter = 0
ear_values = []
EAR_SMOOTHING = 3  # Number of frames to average

cap = cv2.VideoCapture(0)

uio = 0  # Blink count

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)

        left_eye = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(36, 42)])
        right_eye = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(42, 48)])

        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)

        ear = (left_ear + right_ear) / 2.0  # Average of both eyes

        # Apply moving average to smooth EAR
        ear_values.append(ear)
        if len(ear_values) > EAR_SMOOTHING:
            ear_values.pop(0)  # Remove the oldest value
        smoothed_ear = np.mean(ear_values)

        # Blink detection with frame validation
        if smoothed_ear < BLINK_THRESHOLD:
            frame_counter += 1
            if frame_counter >= BLINK_FRAMES:
                cv2.putText(frame, "Blinking", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                uio += 1
                frame_counter = 0  # Reset counter after a blink
        else:
            frame_counter = 0  # Reset if eyes open again

    cv2.imshow("Blink Detector", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print(f"Total Blinks: {uio}")
        break

cap.release()
cv2.destroyAllWindows()
