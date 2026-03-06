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

# optional local serial control (only used if Arduino is attached
# directly to the machine running this script).  The backend also
# contains its own serial controller, so this is not strictly
# necessary unless you moved the board to the client laptop.
try:
    import serial
except ImportError:
    serial = None


def trigger_local_arduino(cmd: str):
    """Send a raw command to the Arduino plugged into ARDUINO_PORT."""
    if serial is None:
        print("pyserial not installed; cannot talk to local Arduino")
        return
    try:
        ser = serial.Serial(ARDUINO_PORT, 9600, timeout=2)
        # wait a moment for the board to reset
        time.sleep(2)
        ser.write(cmd.encode('utf-8') + b"\n")
        ser.flush()
        # read any responses
        time.sleep(0.1)
        while ser.in_waiting > 0:
            print("Arduino(local):", ser.readline().decode('utf-8').strip())
        ser.close()
    except Exception as e:
        print(f"Local Arduino serial error: {e}")

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
                    response = requests.post(HOSTEL_ENTRY_ENDPOINT, json=payload, timeout=10)
                    
                    if response.status_code in (200, 201):
                        data = response.json()
                        print(f"Server: {data.get('message')}  open_gate={data.get('open_gate')}")
                        # if the backend tells us to open the gate and the board
                        # is connected locally, send the serial command here as
                        # well (this duplicates the backend behaviour but is
                        # handy when the board is hanging off the face laptop
                        # instead of the server).
                        if data.get('open_gate'):
                            # command depends on which gate this script controls
                            trigger_local_arduino("OPEN_HOSTEL")
                    else:
                        print(f"Entry Error: {response.status_code} {response.text}")

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
