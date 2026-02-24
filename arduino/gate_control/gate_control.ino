#include <Servo.h>

/*
  Smart Dual-Servo Gate Control System
  ------------------------------------
  Pinout:
  - Hostel Gate Servo: Pin 9
  - Library Gate Servo: Pin 10
  - Serial Baud Rate: 9600
  
  Features:
  - Non-blocking timing using millis() (No delay() calls)
  - Memory efficient: No String class used (uses char arrays and strcmp)
  - Automatic closing after 10 seconds
*/

// Pin Definitions
const int HOSTEL_SERVO_PIN = 9;
const int LIBRARY_SERVO_PIN = 10;

// Servo Objects
Servo hostelServo;
Servo libraryServo;

// Gate Configurations
const int CLOSED_POSITION = 0;
const int OPEN_POSITION = 90;
const unsigned long AUTO_CLOSE_DELAY = 10000; // 10 seconds

// Gate State Tracker
struct GateState {
  Servo& servo;
  bool active;
  unsigned long startTime;
  const char* label;
};

// Initialize gate states
GateState hostel = {hostelServo, false, 0, "Hostel Gate"};
GateState library = {libraryServo, false, 0, "Library Gate"};

// Serial Command Buffer
char serialBuffer[32];
int bufferPos = 0;

void setup() {
  // Initialize Serial
  Serial.begin(9600);
  
  // Attach Servos
  hostel.servo.attach(HOSTEL_SERVO_PIN);
  library.servo.attach(LIBRARY_SERVO_PIN);
  
  // Set initial CLOSED position
  hostel.servo.write(CLOSED_POSITION);
  library.servo.write(CLOSED_POSITION);
  
  Serial.println("SYSTEM_READY: Dual Gate Control Online");
}

void loop() {
  handleSerialInput();
  updateGateTimers();
}

/**
 * Reads serial input and processes commands when a newline is received.
 * Uses char arrays to avoid String class overhead.
 */
void handleSerialInput() {
  while (Serial.available() > 0) {
    char inChar = Serial.read();
    
    // Check for end of command (Newline or Carriage Return)
    if (inChar == '\n' || inChar == '\r') {
      if (bufferPos > 0) {
        serialBuffer[bufferPos] = '\0'; // Null-terminate
        executeCommand(serialBuffer);
        bufferPos = 0; // Reset for next command
      }
    } 
    // Fill buffer if there is space
    else if (bufferPos < (sizeof(serialBuffer) - 1)) {
      serialBuffer[bufferPos++] = inChar;
    }
  }
}

/**
 * Parses and executes recognized commands.
 */
void executeCommand(const char* cmd) {
  if (strcmp(cmd, "OPEN_HOSTEL") == 0) {
    openGate(hostel);
  } 
  else if (strcmp(cmd, "OPEN_LIBRARY") == 0) {
    openGate(library);
  } 
  else if (strcmp(cmd, "INVALID_MOVE") == 0) {
    Serial.println("Invalid movement attempt");
  } 
  else {
    Serial.print("Unknown command: ");
    Serial.println(cmd);
  }
}

/**
 * Opens a specific gate and starts the timer.
 */
void openGate(GateState& gate) {
  if (!gate.active) {
    gate.servo.write(OPEN_POSITION);
    gate.active = true;
    gate.startTime = millis();
    
    Serial.print(gate.label);
    Serial.println(" opened");
  } else {
    // Reset timer if command received while already open
    gate.startTime = millis();
    Serial.print(gate.label);
    Serial.println(" timer reset");
  }
}

/**
 * Checks if gates need to be closed based on the elapsed time.
 * This is non-blocking.
 */
void updateGateTimers() {
  unsigned long currentTime = millis();
  
  // Check Hostel Gate
  if (hostel.active && (currentTime - hostel.startTime >= AUTO_CLOSE_DELAY)) {
    closeGate(hostel);
  }
  
  // Check Library Gate
  if (library.active && (currentTime - library.startTime >= AUTO_CLOSE_DELAY)) {
    closeGate(library);
  }
}

/**
 * Closes a specific gate.
 */
void closeGate(GateState& gate) {
  gate.servo.write(CLOSED_POSITION);
  gate.active = false;
  
  Serial.print(gate.label);
  Serial.println(" closed");
}
