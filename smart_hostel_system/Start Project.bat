@echo off
REM === Go to project root ===
cd /d "C:\Users\dipes\OneDrive\Desktop\coding\MDP\Library-Hostel-return-system\smart_hostel_system"

REM === Activate virtual environment ===
call "venv\Scripts\activate.bat"

REM === Start Flask backend (Window 1) ===
start "Smart Hostel Backend" cmd /k "cd /d backend && python app.py"

REM === Start face recognition hostel gate (Window 2) ===
start "Hostel Gate Recognition" cmd /k "cd /d face_recognition && python hostel_gate.py"

REM === Optional: for library gate, uncomment this line ===
REM start "Library Gate Recognition" cmd /k "cd /d face_recognition && python library_gate.py"
