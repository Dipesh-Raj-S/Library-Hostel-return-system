# Timed Entry and Return Monitoring System

A timed end-to-end system for tracking student travel times between the library and the hostel using face recognition, a backend, a dashboard, and Arduino-based gate control.

## Project Structure
- `backend/`: Flask server (API, Database, Scheduler).
- `face_recog/`: Python scripts for Client Laptops (Library & Hostel).
- `dashboard/`: Streamlit dashboard for the Warden.
- `arduino/`: Arduino sketch for Gate Control.

## Prerequisites
- Python 3.10
- Arduino IDE (to upload sketch)
- Webcam
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

3. **Upload Arduino Sketch:**
   - Open `arduino/gate_control/gate_control.ino` in Arduino IDE.
   - Select your Board and Port.
   - Upload.

4. **Create `.env` for configuration:**
   - Create file `.env` and copy the contents of `.env.example` into it
   - Update as necessary

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

### Step 5: Run Hostel Gate (Laptop B)
Open a new terminal:
```bash
python -m face_recog.hostel_gate
```

- When a face is recognized, the trip starts from Library->Hostel or vice versa.

For late alerts, add `NTFY_SRVR` and `NTFY_TOPIC` in `.env`. 

When a student exceeds the time limit, a notification is sent the to the specified `ntfy` URL.

## Authors

- [Dipesh Raj S](https://github.com/Dipesh-Raj-S) 
- [Siddharth Arumugam](https://github.com/0xMrNight)
- [R Madhumitha](https://github.com/madhu89-70)
