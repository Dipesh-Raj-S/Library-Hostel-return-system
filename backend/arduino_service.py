import sys
import os
from flask import current_app

# Add the parent directory of 'arduino' to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from arduino.serial_comms import GateController

_gate_controller = None

def get_gate_controller():
    """Returns the singleton instance of the GateController"""
    global _gate_controller
    if _gate_controller is None:
        port = current_app.config.get('ARDUINO_PORT', 'COM4')
        baud = current_app.config.get('ARDUINO_BAUD_RATE', 9600)
        
        print(f"Initializing Arduino Gate Controller on {port}...")
        _gate_controller = GateController(port=port, baud_rate=baud)
        if not _gate_controller.connect():
            print("ERROR: Failed to connect to Arduino. Hardware gates will not function.")
    return _gate_controller

def open_hostel_gate():
    """Command the Arduino to open the hostel gate"""
    controller = get_gate_controller()
    if controller and controller.ser and controller.ser.is_open:
        return controller.open_hostel_gate()
    return False

def open_library_gate():
    """Command the Arduino to open the library gate"""
    controller = get_gate_controller()
    if controller and controller.ser and controller.ser.is_open:
        return controller.open_library_gate()
    return False
