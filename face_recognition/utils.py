from requests.exceptions import RequestException 
import requests
import face_recognition
import cv2
import numpy as np

# Configuration
API_BASE_URL = "http://localhost:5000" 

def get_face_encoding(frame):
    """
    Detects face and returns the 128-d encoding.
    Returns None if zero or multiple faces found.
    """
    rgb = frame[:, :, ::-1].copy()
    boxes = face_recognition.face_locations(rgb, model="hog")

    if len(boxes) == 0:
        print("No face detected.")
        return None

    if len(boxes) > 1:
        print("Multiple faces detected. Please ensure only one person is in frame.")
        return None
        
    encodings = face_recognition.face_encodings(rgb, boxes)
    return encodings[0]

def register_student_api(name, encoding, block):
    """
    Sends registration data to the backend.
    """
    url = f"{API_BASE_URL}/register_student"
    payload = {
        "name": name,
        "face_encoding": encoding.tolist(),
        "block": block
    }

    try:
        res = requests.post(url, json=payload, timeout=10)
        try:
            data = res.json()
        except ValueError:
            print("Server did not return JSON:", res.text)
            return None, 500
        return data, res.status_code

    except RequestException as e:
        print(f"Error connecting to backend: {e}")
        return None, 500

def fetch_known_encodings():
    """
    Fetches all stored faces from backend.
    Returns known_ids, known_names, known_encodings.
    """
    url = f"{API_BASE_URL}/get_encodings"

    try:
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            print(f"Failed to fetch encodings: {res.status_code}")
            return [], [], []
        
        data = res.json()
        known_ids, known_names, known_encodings = [], [], []

        for student_id, info in data.items():
            known_ids.append(int(student_id))
            known_encodings.append(np.array(info["encoding"], dtype=np.float64))
            known_names.append(info["name"])

        return known_ids, known_names, known_encodings
        
    except RequestException as e:
        print(f"Error connecting to backend: {e}")
        return [], [], []

def recognize_face(image, student_ids, names, encodings):
    """
    Matches the face in the image against known encodings.
    Returns (student_id, name) if match found, else (None, None).
    """
    if not encodings:
        return None, None

    known_encodings = np.array(encodings)

    unknown_encoding = get_face_encoding(image)
    if unknown_encoding is None:
        return None, None

    face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)
    best = np.argmin(face_distances)

    # tolerance
    if face_distances[best] <= 0.5:
        return student_ids[best], names[best]

    return None, None
