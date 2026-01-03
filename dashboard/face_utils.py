from requests.exceptions import RequestException
import requests
import face_recognition
import numpy as np

API_BASE_URL = "http://localhost:5000"

def get_face_encoding(frame):
    """
    Detects exactly one face and returns the 128-d encoding.
    Returns None if zero or multiple faces are found.
    """
    rgb = frame[:, :, ::-1].copy()
    boxes = face_recognition.face_locations(rgb, model="hog")

    if len(boxes) != 1:
        return None

    encodings = face_recognition.face_encodings(rgb, boxes)
    return encodings[0]


def register_student_api(name, encoding, block):
    """
    Sends registration data to backend.
    Returns (response_json, status_code)
    """
    url = f"{API_BASE_URL}/register_student"
    payload = {
        "name": name,
        "face_encoding": encoding.tolist(),
        "block": block
    }

    try:
        res = requests.post(url, json=payload, timeout=10)
        data = res.json()
        return data, res.status_code

    except (RequestException, ValueError):
        return None, 500


def fetch_known_encodings():
    """
    Fetches all stored faces from backend.
    Returns (ids, names, encodings)
    """
    url = f"{API_BASE_URL}/get_encodings"

    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            return [], [], []

        data = res.json()
        ids, names, encodings = [], [], []

        for student_id, info in data.items():
            ids.append(int(student_id))
            names.append(info["name"])
            encodings.append(np.array(info["encoding"], dtype=np.float64))

        return ids, names, encodings

    except RequestException:
        return [], [], []


def recognize_face(image, student_ids, names, encodings):
    """
    Matches a face against known encodings.
    Returns (student_id, name) or (None, None)
    """
    if not encodings:
        return None, None

    unknown = get_face_encoding(image)
    if unknown is None:
        return None, None

    known = np.array(encodings)
    distances = face_recognition.face_distance(known, unknown)
    best = np.argmin(distances)

    if distances[best] <= 0.5:
        return student_ids[best], names[best]

    return None, None
