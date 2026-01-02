import cv2
from utils import get_face_encoding, register_student_api
from face_recognition import face_locations

DEFAULT_BLOCK = 'D'

def register_face():
    print("Student Registration")
    name = input("Enter student name: ")
    block = input("Enter block: ")
    
    if not block:
        block = DEFAULT_BLOCK

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

        # draw boxes around faces
        rgb = frame[:, :, ::-1]
        boxes = face_locations(rgb)

        for t, r, b, l in boxes:
            cv2.rectangle(frame, (l, t), (r, b), (0, 255, 0), 2)

        # warnings or hint
        message = None

        if len(boxes) == 0:
            message = "No face detected"
        elif len(boxes) > 1:
            message = "Multiple faces detected"
        else:
            # non-intrusive hint
            cv2.putText(frame, "Ensure only one face is visible", (20, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)

        if message:
            cv2.putText(frame, message, (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)

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
                res, status = register_student_api(name, encoding, block)
                
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
