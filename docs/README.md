# Smart Timed Hostel Return System

A complete end-to-end system for tracking student return times from the library to the hostel using face recognition, a Flask backend, a Streamlit dashboard, and Arduino-based gate control.

## Project Structure
- `backend/`: Flask server (API, Database, Scheduler).
- `face_recog/`: Python scripts for Client Laptops (Library & Hostel).
- `dashboard/`: Streamlit dashboard for the Warden.
- `arduino/`: Arduino sketch for Gate Control.

## Prerequisites
- Python 3.10
- Arduino IDE (to upload sketch)
- Webcam (for testing)
- Arduino UNO + Relay (optional, for hardware demo)

## Installation

1. **Clone/Download the project.**

2. **Install Python Dependencies:**
   It is recommended to use a virtual environment.
   ```bash
   # Backend
   pip install -r backend/requirements.txt
   
   # Face Recognition
   pip install -r face_recog/requirements.txt
   
   # Dashboard
   pip install -r dashboard/requirements.txt
   ```
   *(Note: You can install all in one go if you prefer)*

3. **Upload Arduino Sketch:**
   - Open `arduino/gate_control/gate_control.ino` in Arduino IDE.
   - Select your Board and Port.
   - Upload.

## How to Run

### Step 1: Start the Backend Server
Open a terminal:
```bash
cd backend
python app.py
```
*Server runs on http://localhost:5000*

### Step 2: Start the Warden Dashboard
Open a new terminal:
```bash
python -m streamlit run dashboard/app.py
```
*Dashboard opens in your browser.*

### Step 3: Register a Student
Open a new terminal:
```bash
python -m face_recog.register_face
```
- Enter name.
- Look at the camera and press 's' to save.

### Step 4: Run Library Gate (Laptop A)
Open a new terminal:
```bash
python -m face_recog.library_gate
```
- When it recognizes you, it starts the timer.

### Step 5: Run Hostel Gate (Laptop B)
Open a new terminal:
```bash
python -m face_recog.hostel_gate
```
- Ensure Arduino is connected (update COM port in `hostel_gate.py` if needed).
- When it recognizes you, it stops the timer and opens the gate.

## Testing the Timer
- By default, the timer is set to **1 minute** in `library_gate.py` for testing purposes.
- If you wait >1 minute between Library Exit and Hostel Entry, the Dashboard will show an Alert.
