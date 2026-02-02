import cv2
import time
import requests
import sys
import os

# Add arduino directory to path to import serial_comms
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../arduino')))
# from serial_comms import GateController
from utils import fetch_known_encodings, recognize_face, draw_boxes
from face_recognition import face_locations

# Configuration
API_BASE_URL = "http://localhost:5000"
HOSTEL_ENTRY_ENDPOINT = f"{API_BASE_URL}/hostel_entry"
# ARDUINO_PORT = 'COM3' # Change this to your actual port

def hostel_gate_loop():
    print("Initializing Hostel Gate System...")

    # Initialize Arduino Connection
    # gate = GateController(port=ARDUINO_PORT)
    # if not gate.connect():
    #     print("WARNING: Arduino not connected. Gate will not physically open.")
    
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
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"Entry Approved: {data.get('message')}")
                        # if data.get('open_gate'):
                        #     gate.open_gate()
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
    # gate.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    hostel_gate_loop()
