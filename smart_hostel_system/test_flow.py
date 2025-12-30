import requests
import time

BASE_URL = "http://localhost:5000"

print("🔄 Testing Full Flow...\n")

# 1️⃣ Register (already done ✅)
print("1️⃣ Student exists (ID: 2)\n")

# 2️⃣ Library Exit (FIXED - use student_id)
print("2️⃣ Starting Library Trip...")
trip_data = {"student_id": 2}  # ✅ Use ID instead of name
trip_resp = requests.post(f"{BASE_URL}/library_exit", json=trip_data)
print(f"✅ Trip: {trip_resp.json()}\n")

# 3️⃣ Check Dashboard
print("3️⃣ Checking Active Timers...")
time.sleep(2)
timers = requests.get(f"{BASE_URL}/active_timers").json()
print(f"✅ Dashboard shows: {len(timers)} active timers")
if timers:
    timer = timers[0]
    print(f"   👤 {timer.get('student_name')} | 🏢 {timer.get('student_block')} | ⏳ {timer.get('time_remaining')}")
