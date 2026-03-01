from requests.exceptions import RequestException 
import requests
import face_recognition
import numpy as np
import cv2

# Configuration
from config import Config
API_BASE_URL = Config.API_BASE_URL

def get_face_encoding(frame):
    """
    Detects face and returns the 128-d encoding.
    Returns None if zero or multiple faces found.
    """
    rgb = frame[:, :, ::-1].copy()
    boxes = face_recognition.face_locations(rgb, model="hog")

    if len(boxes) == 0:
        return None

    if len(boxes) > 1:
        return None
        
    encodings = face_recognition.face_encodings(rgb, boxes)
    return encodings[0]

def check_reg_exists(regno):
    """
    Checks if regno is already in the database
    """
    try:
        res = requests.get(f"{API_BASE_URL}/check-student/{regno}")
        return res.status_code == 200  # Returns True if exists
    except Exception as e:
        print(f"Connection error: {e}")
        return False

def register_student_api(name, encoding, block,regno):
    """
    Sends registration data to the backend.
    """
    url = f"{API_BASE_URL}/register_student"
    payload = {
        "name": name,
        "face_encoding": encoding.tolist(),
        "block": block,
        "reg_no":regno.strip()
    }

    try:
        res = requests.post(url, json=payload, timeout=10)
        try:
            data = res.json()
        except ValueError:
            return None, 500
        return data, res.status_code

    except RequestException as e:
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

def draw_boxes(frame, boxes, name):
    if not name:
        name = "Unknown"

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

        label = name

        # get text size to fit label background
        (text_w, text_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)

        # Background rectangle above the box
        label_top = max(0, t-text_h-8)
        label_bottom = t

        cv2.rectangle(frame, (l, label_top), (l+text_w+8, label_bottom), (0, 255, 0), -1)

        # Put the text inside the label background
        cv2.putText(frame, label, (l+4, label_bottom - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)

        # background
        # cv2.rectangle(frame, (l, b - 25), (r, b), (0, 255, 0), cv2.FILLED)
        # cv2.putText(frame, label, (l+6, b-6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)