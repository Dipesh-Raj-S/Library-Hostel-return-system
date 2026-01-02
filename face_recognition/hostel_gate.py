import cv2
import time
import requests
import sys
import os

# Add arduino directory to path to import serial_comms
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../arduino')))
from serial_comms import GateController
from utils import fetch_known_encodings, recognize_face

# Configuration
API_BASE_URL = "http://localhost:5000"
HOSTEL_ENTRY_ENDPOINT = f"{API_BASE_URL}/hostel_entry"
ARDUINO_PORT = 'COM3' # Change this to your actual port

def hostel_gate_loop():
    print("Initializing Hostel Gate System...")

    # Initialize Arduino Connection
    gate = GateController(port=ARDUINO_PORT)
    if not gate.connect():
        print("WARNING: Arduino not connected. Gate will not physically open.")
    
    # Fetch known faces
    print("Fetching known student encodings...")
    known_encodings = fetch_known_encodings()
    print(f"Loaded {len(known_encodings)} students.")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    last_recognition_time = 0
    RECOGNITION_COOLDOWN = 5

    print("Hostel Gate Active. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        student_id, name = recognize_face(small_frame, known_encodings)

        if student_id:
            cv2.putText(frame, f"Verified: {name}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            current_time = time.time()
            if current_time - last_recognition_time > RECOGNITION_COOLDOWN:
                print(f"Student {name} arrived at hostel...")
                try:
                    payload = {"student_id": student_id}
                    response = requests.post(HOSTEL_ENTRY_ENDPOINT, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"Entry Approved: {data.get('message')}")
                        if data.get('open_gate'):
                            gate.open_gate()
                    else:
                        print(f"Entry Error: {response.text}")

                except Exception as e:
                    print(f"Network error: {e}")
                
                last_recognition_time = current_time

        cv2.imshow('Hostel Gate', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    gate.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    hostel_gate_loop()
