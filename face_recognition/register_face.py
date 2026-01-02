import cv2
from utils import get_face_encoding, register_student_api

def register_face():
    print("Starting Face Registration...")
    name = input("Enter Student Name: ")
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Press 's' to capture face, 'q' to quit.")
    cv2.namedWindow("Register Face")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        frame = cv2.flip(frame, 1)   # lateral inversion
        cv2.imshow('Register Face', frame)

        key = cv2.waitKey(1) & 0xFF

        # exit if X is clicked
        if cv2.getWindowProperty("Register Face", cv2.WND_PROP_VISIBLE) < 1: 
            break 

        if key == ord('s'):
            print("Capturing...")
            encoding = get_face_encoding(frame)
            
            if encoding is not None:
                print(f"Face encoded for {name}. Sending to server...")
                res, status = register_student_api(name, encoding)
                
                if status == 201:
                    print(f"Success! Student ID: {res.get('student_id')}")
                    break
                else:
                    print(f"Registration failed: {res}")
            else:
                print("Try again.")
        
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    register_face()
