import serial
import time

class GateController:
    def __init__(self, port='COM3', baud_rate=9600):
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2) # Wait for Arduino to reset
            print(f"Connected to Arduino on {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Error connecting to Arduino: {e}")
            return False

    def open_gate(self):
        if self.ser and self.ser.is_open:
            print("Sending OPEN command...")
            self.ser.write(b"OPEN")
            return True
        else:
            print("Serial connection not open.")
            return False

    def close(self):
        if self.ser:
            self.ser.close()
