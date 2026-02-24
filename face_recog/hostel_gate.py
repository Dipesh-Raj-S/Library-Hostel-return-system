import cv2
import time
import requests
import sys
import os

from face_recog.utils import fetch_known_encodings, recognize_face, draw_boxes
from face_recognition import face_locations

# Configuration
from config import Config
API_BASE_URL = Config.API_BASE_URL
HOSTEL_ENTRY_ENDPOINT = Config.HOSTEL_ENTRY_ENDPOINT
ARDUINO_PORT = Config.ARDUINO_PORT

def hostel_gate_loop():
    print("Initializing Hostel Gate System...")
    
    # Fetch known faces
    print("Fetching known student encodings...")
    known_ids, known_encodings, known_names = fetch_known_encodings()
    print(f"Loaded {len(known_ids)} students.")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    last_recognition_time = {}
    RECOGNITION_COOLDOWN = 5

    print("Hostel Gate Active. Press 'q' to quit.")
    cv2.namedWindow("Hostel Gate")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        # performance optimization
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small = small_frame[:, :, ::-1]

        # Detect faces
        student_id, name = recognize_face(small_frame, known_ids, known_encodings, known_names)

        boxes = face_locations(rgb_small)
        draw_boxes(frame, boxes, name)
        
        if student_id:
            cv2.putText(frame, f"Verified: {name}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            now = time.time()
            last_seen = last_recognition_time.get(student_id, 0)
            if now - last_seen > RECOGNITION_COOLDOWN:
                print(f"Student {name} arrived at hostel...")
                try:
                    payload = {"student_id": student_id}
                    response = requests.post(HOSTEL_ENTRY_ENDPOINT, json=payload)
                    
                    if response.status_code == 200 or response.status_code == 201:
                        data = response.json()
                        print(f"Server: {data.get('message')}")
                    else:
                        print(f"Entry Error: {response.text}")

                except Exception as e:
                    print(f"Network error: {e}")
                
                last_recognition_time[student_id] = now

        cv2.imshow('Hostel Gate', frame)

        key = cv2.waitKey(1) & 0xFF
        if cv2.getWindowProperty("Hostel Gate", cv2.WND_PROP_VISIBLE) < 1:
            break
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    hostel_gate_loop()
