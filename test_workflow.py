import requests
import time
import json

BASE_URL = "http://localhost:5000"

def test_workflow():
    print("Starting Automated Workflow Test...")

    # 1. Register Student
    print("\n[1] Registering Test Student...")
    student_data = {
        "name": "Test Student",
        "face_encoding": [0.1] * 128 # Dummy encoding
    }
    res = requests.post(f"{BASE_URL}/register_student", json=student_data)
    if res.status_code == 201:
        student_id = res.json()['student_id']
        print(f"SUCCESS: Student registered with ID {student_id}")
    else:
        print(f"FAILED: {res.text}")
        return

    # 2. Library Exit
    print("\n[2] Simulating Library Exit...")
    exit_data = {
        "student_id": student_id,
        "duration_minutes": 0.1 # 6 seconds for testing
    }
    res = requests.post(f"{BASE_URL}/library_exit", json=exit_data)
    if res.status_code == 201:
        print("SUCCESS: Timer started.")
    else:
        print(f"FAILED: {res.text}")

    # 3. Check Active Timers
    print("\n[3] Checking Active Timers...")
    res = requests.get(f"{BASE_URL}/active_timers")
    timers = res.json()
    if len(timers) > 0:
        print(f"SUCCESS: Found {len(timers)} active timer(s).")
    else:
        print("FAILED: No active timers found.")

    # 4. Wait for Timer Expiry (Simulate Late)
    print("\n[4] Waiting for 10 seconds to simulate late arrival...")
    time.sleep(10)

    # 5. Check Alerts
    print("\n[5] Checking Alerts...")
    res = requests.get(f"{BASE_URL}/alerts")
    alerts = res.json()
    found_alert = False
    for alert in alerts:
        if alert['student_id'] == student_id:
            print("SUCCESS: Alert found for student.")
            found_alert = True
            break
    if not found_alert:
        print("FAILED: No alert found.")

    # 6. Hostel Entry
    print("\n[6] Simulating Hostel Entry...")
    entry_data = {"student_id": student_id}
    res = requests.post(f"{BASE_URL}/hostel_entry", json=entry_data)
    if res.status_code == 200:
        print("SUCCESS: Entry recorded.")
        print(f"Response: {res.json()}")
    else:
        print(f"FAILED: {res.text}")

if __name__ == "__main__":
    try:
        test_workflow()
    except Exception as e:
        print(f"Error: Is the backend server running? {e}")
