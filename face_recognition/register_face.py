import cv2
import time
from utils import get_face_encoding, register_student_api

def register_face():
    print("Starting Face Registration...")
    name = input("Enter Student Name: ")
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Press 's' to capture face, 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow('Register Face', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            print("Capturing...")
            encoding = get_face_encoding(frame)
            
            if encoding is not None:
                print(f"Face encoded for {name}. Sending to server...")
                response, status = register_student_api(name, encoding)
                
                if status == 201:
                    print(f"Success! Student ID: {response.get('student_id')}")
                    break
                else:
                    print(f"Registration failed: {response}")
            else:
                print("Try again.")
        
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    register_face()
