import serial
import time

class GateController:
    def __init__(self, port='COM4', baud_rate=9600):
        """
        Initialize Gate Controller for dual servo system
        
        Args:
            port: COM port where Arduino is connected (default: COM4)
            baud_rate: Serial communication speed (default: 9600)
        """
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None

    def connect(self):
        """Establish serial connection with Arduino"""
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            print(f"Connected to Arduino on {self.port}")
            
            # Read initial message from Arduino
            if self.ser.in_waiting > 0:
                response = self.ser.readline().decode('utf-8').strip()
                print(f"Arduino: {response}")
            
            return True
        except serial.SerialException as e:
            print(f"Error connecting to Arduino: {e}")
            return False

    def open_hostel_gate(self):
        """Send command to open hostel gate for 10 seconds"""
        if self.ser and self.ser.is_open:
            print("Sending OPEN_HOSTEL command...")
            self.ser.write(b"OPEN_HOSTEL\n")
            self.ser.flush()
            
            # Read confirmation messages
            time.sleep(0.1)
            while self.ser.in_waiting > 0:
                response = self.ser.readline().decode('utf-8').strip()
                print(f"Arduino: {response}")
            
            return True
        else:
            print("Serial connection not open.")
            return False

    def open_library_gate(self):
        """Send command to open library gate for 10 seconds"""
        if self.ser and self.ser.is_open:
            print("Sending OPEN_LIBRARY command...")
            self.ser.write(b"OPEN_LIBRARY\n")
            self.ser.flush()
            
            # Read confirmation messages
            time.sleep(0.1)
            while self.ser.in_waiting > 0:
                response = self.ser.readline().decode('utf-8').strip()
                print(f"Arduino: {response}")
            
            return True
        else:
            print("Serial connection not open.")
            return False

    def close(self):
        """Close serial connection"""
        if self.ser:
            self.ser.close()
            print("Serial connection closed.")
