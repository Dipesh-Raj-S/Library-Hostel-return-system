import requests
import json
import time

BASE_URL = "http://localhost:5000"

def verify_system():
    # Wait for server to start
    print("Waiting for server...")
    time.sleep(5) 

    # 1. Register Student (Block A - should be 15 mins)
    print("Registering Student (Block A)...")
    timestamp = int(time.time())
    payload = {
        "name": f"Test Student A_{timestamp}",
        "face_encoding": [0.1] * 128, # Dummy encoding
        "block": "A"
    }
    try:
        response = requests.post(f"{BASE_URL}/register_student", json=payload)
        if response.status_code == 201:
            student_id = response.json()['student_id']
            print(f"Success: Student registered with ID {student_id}")
        else:
            print(f"Failed: {response.text}")
            return
    except Exception as e:
        print(f"Error connecting: {e}")
        return

    # 2. Start Trip
    print("Starting Trip...")
    payload = {"student_id": student_id}
    response = requests.post(f"{BASE_URL}/library_exit", json=payload)
    if response.status_code == 201:
        data = response.json()
        trip_id = data['trip_id']
        expected_end_time = data['expected_end_time']
        print(f"Success: Trip started. Expected End: {expected_end_time}")
        
        # Verify duration
        # We can't easily parse ISO in simple print, but we can check if it worked
        print("Trip started successfully.")
    else:
        print(f"Failed to start trip: {response.text}")
        return

    # 3. Check Active Timers
    print("Checking Active Timers...")
    response = requests.get(f"{BASE_URL}/active_timers")
    if response.status_code == 200:
        timers = response.json()
        found = False
        for t in timers:
            if t['student_id'] == student_id:
                print(f"Timer object: {t}")
                if 'student_block' in t:
                    print(f"Found active timer for {t['student_name']} (Block {t['student_block']})")
                else:
                    print(f"Active timer found but 'student_block' MISSING. Keys: {t.keys()}")
                print(f"Status: {t['status']}")
                found = True
                break
        if not found:
            print("Error: Student not found in active timers.")
    else:
        print("Failed to fetch active timers.")

if __name__ == "__main__":
    verify_system()
