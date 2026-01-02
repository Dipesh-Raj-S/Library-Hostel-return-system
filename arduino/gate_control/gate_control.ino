/*
  Smart Hostel Gate Control
  Listens for "OPEN" command over Serial and activates a relay.
*/

const int RELAY_PIN = 7; // Connect Relay Signal Pin to Digital Pin 7

void setup() {
  Serial.begin(9600);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW); // Ensure relay is off initially
  Serial.println("Gate Control System Ready");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove whitespace

    if (command == "OPEN") {
      Serial.println("Opening Gate...");
      digitalWrite(RELAY_PIN, HIGH); // Activate Relay
      delay(2000);                   // Keep open for 2 seconds
      digitalWrite(RELAY_PIN, LOW);  // Deactivate Relay
      Serial.println("Gate Closed");
    }
  }
}
