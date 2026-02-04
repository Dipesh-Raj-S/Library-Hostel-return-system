import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def register_student(name, block):
    url = f"{BASE_URL}/register_student"
    data = {
        "name": name,
        "block": block,
        "face_encoding": [0.1] * 128 
    }
    response = requests.post(url, json=data)
    print(f"Register {name}: {response.status_code} - {response.json()}")
    return response.json().get('student_id')

def scan_hostel(student_id):
    url = f"{BASE_URL}/scan_hostel"
    data = {"student_id": student_id}
    response = requests.post(url, json=data)
    print(f"Scan Hostel (ID {student_id}): {response.status_code} - {response.json()}")
    return response.json()

def scan_library(student_id):
    url = f"{BASE_URL}/scan_library"
    data = {"student_id": student_id}
    response = requests.post(url, json=data)
    print(f"Scan Library (ID {student_id}): {response.status_code} - {response.json()}")
    return response.json()

def check_timers():
    url = f"{BASE_URL}/active_timers"
    response = requests.get(url)
    print(f"Active Timers: {json.dumps(response.json(), indent=2)}")

def main():
    print("--- Starting Verification Flow ---")
    
    # 1. Register Student
    sid = register_student("Test Student", "A")
    if not sid:
        print("Failed to register student.")
        return

    # 2. Scan at Hostel -> Start H->L
    print("\n--- Moving: Hostel -> Library ---")
    scan_hostel(sid)
    check_timers()

    # 3. Simulate time pass (optional)
    # time.sleep(2)
    
    # 4. Scan at Library -> Stop H->L
    print("\n--- Arrived: Library ---")
    scan_library(sid)
    check_timers()

    # 5. Scan at Library -> Start L->H
    print("\n--- Moving: Library -> Hostel ---")
    scan_library(sid)
    check_timers()

    # 6. Scan at Hostel -> Stop L->H
    print("\n--- Arrived: Hostel ---")
    scan_hostel(sid)
    check_timers()

if __name__ == "__main__":
    main()
