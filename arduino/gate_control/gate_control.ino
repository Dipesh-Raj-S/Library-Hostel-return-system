#include <Servo.h>

/*
 * SMART DUAL-SERVO GATE CONTROL SYSTEM (v2)
 * -----------------------------------------
 * Hardware Connections:
 * - Hostel Gate Servo: Pin 9
 * - Library Gate Servo: Pin 10
 * - Serial Baud Rate: 9600
 * 
 * Logic:
 * - Commands: "OPEN_HOSTEL", "OPEN_LIBRARY"
 * - Automatically closes gate after 10 seconds
 * - Uses non-blocking timing with millis()
 * - Uses char arrays (no String class used)
 */

// --- Constants & Pin Definitions ---
const int PIN_HOSTEL_SERVO = 9;
const int PIN_LIBRARY_SERVO = 10;

const int POS_CLOSED = 0;
const int POS_OPEN = 90;
const unsigned long GATE_TIMEOUT = 10000; // 10 seconds

// --- Servo Objects ---
Servo hostelServo;
Servo libraryServo;

// --- Gate State Management ---
struct Gate {
    Servo& motor;
    int pin;
    bool isOpen;
    unsigned long startTime;
    const char* name;
};

// Initialize gate objects
Gate hostelGate = {hostelServo, PIN_HOSTEL_SERVO, false, 0, "Hostel Gate"};
Gate libraryGate = {libraryServo, PIN_LIBRARY_SERVO, false, 0, "Library Gate"};

// --- Serial Buffer ---
char cmdBuffer[32];
int bufferIndex = 0;

void setup() {
    Serial.begin(9600);
    
    // Initialize Servos
    hostelGate.motor.attach(hostelGate.pin);
    libraryGate.motor.attach(libraryGate.pin);
    
    // Set initial positions
    hostelGate.motor.write(POS_CLOSED);
    libraryGate.motor.write(POS_CLOSED);
    
    Serial.println("SYSTEM_BOOT: Dual Gate Controller Online");
    Serial.println("READY: Awaiting Commands...");
}

void loop() {
    // 1. Process Incoming Serial Data
    checkSerial();
    
    // 2. Manage Independent Gate Timers
    updateGate(hostelGate);
    updateGate(libraryGate);
}

/**
 * Reads serial data byte-by-byte and builds a command string.
 * Triggers execution when a newline is detected.
 */
void checkSerial() {
    while (Serial.available() > 0) {
        char inChar = (char)Serial.read();
        
        // Check for end-of-line characters
        if (inChar == '\n' || inChar == '\r') {
            if (bufferIndex > 0) {
                cmdBuffer[bufferIndex] = '\0'; // Null-terminate
                processCommand(cmdBuffer);
                bufferIndex = 0; // Clear buffer
            }
        } 
        // Add to buffer if there's room
        else if (bufferIndex < (sizeof(cmdBuffer) - 1)) {
            cmdBuffer[bufferIndex++] = inChar;
        }
    }
}

/**
 * Logic to map serial strings to gate actions.
 */
void processCommand(const char* cmd) {
    if (strcmp(cmd, "OPEN_HOSTEL") == 0) {
        openGate(hostelGate);
    } 
    else if (strcmp(cmd, "OPEN_LIBRARY") == 0) {
        openGate(libraryGate);
    } 
    else if (strcmp(cmd, "INVALID_MOVE") == 0) {
        Serial.println("Invalid movement attempt detected");
    }
    else {
        Serial.print("Unknown command: ");
        Serial.println(cmd);
    }
}

/**
 * Triggers the opening of a gate and starts its independent timer.
 */
void openGate(Gate &g) {
    if (!g.isOpen) {
        g.motor.write(POS_OPEN);
        g.isOpen = true;
        g.startTime = millis();
        
        Serial.print(g.name);
        Serial.println(" opened");
    } else {
        // If already open, reset the timer
        g.startTime = millis();
        Serial.print(g.name);
        Serial.println(" - Timer reset");
    }
}

/**
 * Checks if a gate's open duration has elapsed and closes it if so.
 */
void updateGate(Gate &g) {
    if (g.isOpen) {
        if (millis() - g.startTime >= GATE_TIMEOUT) {
            closeGate(g);
        }
    }
}

/**
 * Moves servo back to closed position and marks state.
 */
void closeGate(Gate &g) {
    g.motor.write(POS_CLOSED);
    g.isOpen = false;
    
    Serial.print(g.name);
    Serial.println(" closed");
}
