#reflection analysis red color 

import cv2
import numpy as np
import pygame
import screen_brightness_control as sbc
import dlib
import time
import tkinter as tk
from tkinter import messagebox

#time 
trate=50

#time long
#t1,t2=3,1

#time short
t1,t2=3/trate,1/trate

# Function to maximize brightness
def maximize_brightness():
    sbc.set_brightness(100)

# Initialize dlib's face detector and landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(r"C:\Users\LOQ\Documents\code\FLD\shape_predictor_68_face_landmarks.dat")

# Initialize pygame for screen control
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

# Function to change screen color
def change_screen_color(color):
    screen.fill(color)
    pygame.display.update()

# Start webcam
cap = cv2.VideoCapture(0)

# Set initial screen brightness and color
maximize_brightness()
change_screen_color((255, 255, 255))  # Start with white

# Storage for redness changes
redness_results = []

# Function to detect redness in eye region
def detect_redness(frame, face):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    landmarks = predictor(gray, face)

    left_eye = (landmarks.part(36).x, landmarks.part(36).y)
    right_eye = (landmarks.part(45).x, landmarks.part(45).y)

    x1, y1 = min(left_eye[0], right_eye[0]), min(left_eye[1], right_eye[1])
    x2, y2 = max(left_eye[0], right_eye[0]), max(left_eye[1], right_eye[1])
    
    x1, y1, x2, y2 = max(x1, 0), max(y1, 0), min(x2, frame.shape[1]), min(y2, frame.shape[0])
    eye_region = frame[y1:y2, x1:x2]

    if eye_region.size > 0:
        hsv_eye = cv2.cvtColor(eye_region, cv2.COLOR_BGR2HSV)
        lower_red1, upper_red1 = np.array([0, 100, 100]), np.array([15, 255, 255])
        lower_red2, upper_red2 = np.array([165, 100, 100]), np.array([180, 255, 255])


        red_mask = cv2.bitwise_or(cv2.inRange(hsv_eye, lower_red1, upper_red1), 
                                  cv2.inRange(hsv_eye, lower_red2, upper_red2))
        
        red_pixels = np.sum(red_mask > 0)  # Count red pixels
        total_pixels = eye_region.shape[0] * eye_region.shape[1]  # Total eye region pixels

        if total_pixels == 0:  # Prevent division by zero
            return 0

        redness_ratio = red_pixels / total_pixels  # Normalize redness
        return redness_ratio
    return 0

# Function to capture redness during each phase
def capture_redness():
    time.sleep(1)  # Allow stabilization
    ret, frame = cap.read()
    if not ret:
        return 0

    faces = detector(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    if faces:
        return detect_redness(frame, faces[0])
    return 0

time.sleep(2)
# Controlled lighting cycle
for i in range(5):
    print(f"Test {i+1} starting with white screen...")
    change_screen_color((255, 255, 255))  # White
    time.sleep(t1)

    print(f"Test {i+1} switching to red screen...")
    change_screen_color((255, 0, 0))  # Red
    time.sleep(t2)  # Wait before measurement
    redness = capture_redness()
    
    if i == 3 or i == 4:  # Store results for 1st and 3rd test
        redness_results.append(redness)

    time.sleep(t2)  # Ensure full red exposure before next cycle

# Restore brightness and cleanup
sbc.set_brightness(30)
cap.release()
cv2.destroyAllWindows()
pygame.quit()

# **Threshold for reflection detection (normalized ratio)**
THRESHOLD = 0.70  # Adjust based on testing

# Determine test results
result_1 = "✅ Verified" if redness_results[0] >= THRESHOLD else "❌ Failed"
result_3 = "✅ Verified" if redness_results[1] >= THRESHOLD else "❌ Failed"

# Function to display the popup message
def show_popup():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showinfo("Reflection Analysis Completed", 
                        f"Test Results:\n\n"
                        f"1st Red Test: {result_1}\n"
                        f"3rd Red Test: {result_3}")

# Show popup
show_popup()

# Print results in console
print(f"Redness in first red test: {redness_results[0]:.2f} ({result_1})")
print(f"Redness in third red test: {redness_results[1]:.2f} ({result_3})")

