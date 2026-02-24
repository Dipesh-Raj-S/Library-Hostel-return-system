/*
  Dual Servo Gate Control System - Non-Blocking Version
  Controls two servo motors for Hostel and Library gates
  
  Hardware Connections:
  - Hostel Gate Servo Signal -> Pin 9
  - Library Gate Servo Signal -> Pin 10
  - Both Servos GND -> Arduino GND
  - Both Servos VCC -> EXTERNAL 5V-6V (Do not use Arduino 5V pin for multiple servos!)
  
  Serial Commands:
  - "OPEN_HOSTEL" -> Opens hostel gate for 10 seconds
  - "OPEN_LIBRARY" -> Opens library gate for 10 seconds
*/

#include <Servo.h>

// Pin Definitions
const int HOSTEL_SERVO_PIN = 9;
const int LIBRARY_SERVO_PIN = 10;

// Servo Objects
Servo hostelGate;
Servo libraryGate;

// Gate Positions (in degrees)
const int GATE_CLOSED = 0;
const int GATE_OPEN = 90;

// Timing Constants
const unsigned long GATE_OPEN_DURATION = 1000; // 10 seconds

// State Variables
bool hostelGateActive = false;
unsigned long hostelGateStartTime = 0;

bool libraryGateActive = false;
unsigned long libraryGateStartTime = 0;

void setup() {
  Serial.begin(9600);
  
  // Attach servos to pins
  hostelGate.attach(HOSTEL_SERVO_PIN);
  libraryGate.attach(LIBRARY_SERVO_PIN);
  
  // Initialize both gates to closed position
  hostelGate.write(GATE_CLOSED);
  libraryGate.write(GATE_CLOSED);
  
  Serial.println("Dual Servo Gate Control System Ready (Non-Blocking)");
  Serial.println("Commands: OPEN_HOSTEL, OPEN_LIBRARY");
}

void loop() {
  // 1. Handle Serial Commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "OPEN_HOSTEL") {
      if (!hostelGateActive) {
        openHostelGate();
      } else {
        Serial.println("Hostel gate is already in operation");
      }
    } 
    else if (command == "OPEN_LIBRARY") {
      if (!libraryGateActive) {
        openLibraryGate();
      } else {
        Serial.println("Library gate is already in operation");
      }
    }
    else {
      Serial.println("Unknown command: " + command);
    }
  }

  // 2. Manage Hostel Gate Timing
  if (hostelGateActive) {
    if (millis() - hostelGateStartTime >= GATE_OPEN_DURATION) {
      closeHostelGate();
    }
  }

  // 3. Manage Library Gate Timing
  if (libraryGateActive) {
    if (millis() - libraryGateStartTime >= GATE_OPEN_DURATION) {
      closeLibraryGate();
    }
  }
}

void openHostelGate() {
  Serial.println("Opening Hostel Gate...");
  hostelGate.write(GATE_OPEN);
  hostelGateActive = true;
  delay(GATE_OPEN_DURATION);
}

void closeHostelGate() {
  hostelGate.write(GATE_CLOSED);
  hostelGateActive = false;
  Serial.println("Hostel Gate CLOSED");
  delay(GATE_OPEN_DURATION);
}

void openLibraryGate() {
  Serial.println("Opening Library Gate...");
  libraryGate.write(GATE_OPEN);
  libraryGateActive = true;
  delay(GATE_OPEN_DURATION);
}

void closeLibraryGate() {
  libraryGate.write(GATE_CLOSED);
  libraryGateActive = false;
  delay(GATE_OPEN_DURATION);
  Serial.println("Library Gate CLOSED");
}
