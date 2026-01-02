import cv2
import time
import requests
from utils import fetch_known_encodings, recognize_face
from face_recognition import face_locations

# Configuration
API_BASE_URL = "http://localhost:5000"
LIBRARY_EXIT_ENDPOINT = f"{API_BASE_URL}/library_exit"

def library_gate_loop():
    print("Initializing library gate system...")
    
    # Fetch known faces
    print("Fetching known student encodings...")
    known_ids, known_encodings, known_names = fetch_known_encodings()
    print(f"Loaded {len(known_ids)} students.")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    last_recognition_time = {}
    RECOGNITION_COOLDOWN = 5 # Seconds between API calls for the same person

    print("Library Gate Active. Press 'q' to quit.")
    cv2.namedWindow("Library Gate")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)

        # performance optimization
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small = small_frame[:, :, ::-1]

        # Detect faces
        boxes = face_locations(rgb_small)

        student_id, name = recognize_face(small_frame, known_ids, known_encodings, known_names)

        # draw boxes
        for (t, r, b, l) in boxes:
            # scale back to full size
            t *= 2
            r *= 2
            b *= 2
            l *= 2

            # increase box padding
            pad = int((b-t) * 0.10)
            t = max(0, t-pad)
            b += pad

            # draw rectangle
            cv2.rectangle(frame, (l, t), (r, b), (0, 255, 0), 2)

            label = name if student_id else "Unknown"

            # get text size to fit label background
            (text_w, text_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)

            # Background rectangle above the box
            label_top = max(0, t-text_h-8)
            label_bottom = t

            cv2.rectangle(frame, (l, label_top), (l+text_w+8, label_bottom), (0, 255, 0), -1)

            # Put the text inside the label background
            cv2.putText(frame, label, (l+4, label_bottom - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)

            # # background
            # cv2.rectangle(frame, (l, b - 25), (r, b), (0, 255, 0), cv2.FILLED)
            # cv2.putText(frame, label, (l+6, b-6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        if student_id:
            now = time.time()
            last_seen = last_recognition_time.get(student_id, 0)
            if now - last_seen > RECOGNITION_COOLDOWN:
                print(f"Student {name} exiting library...")

                try:
                    TRIP_TIME = 10 # to change 

                    payload = {"student_id": student_id, "duration_minutes": TRIP_TIME} 
                    res = requests.post(LIBRARY_EXIT_ENDPOINT, json=payload, timeout=10)

                    if res.status_code == 201:
                        print(f"Timer started for {name}. Expected arrival in {TRIP_TIME} min.")
                    elif res.status_code == 200:
                        print(f"Timer already active for {name}.")
                    else:
                        print(f"Server error: {res.text}")

                except Exception as e:
                    print(f"Network error: {e}")
                
                last_recognition_time[student_id] = now

        cv2.imshow('Library Gate', frame)

        key = cv2.waitKey(1) & 0xFF
        if cv2.getWindowProperty("Library Gate", cv2.WND_PROP_VISIBLE) < 1:
            break
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    library_gate_loop()
