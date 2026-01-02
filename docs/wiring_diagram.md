# Arduino Wiring Diagram

## Components
- Arduino UNO (or Nano)
- 5V Relay Module (Single Channel)
- Jumper Wires
- USB Cable (for connection to Laptop B)
- Electronic Door Lock (12V) + Power Supply (Optional, for simulation just Relay is enough)

## Connections

| Arduino Pin | Relay Module Pin | Description |
|-------------|------------------|-------------|
| 5V          | VCC              | Power       |
| GND         | GND              | Ground      |
| D7          | IN               | Signal      |

## Relay to Lock Connections (Common Setup)

| Relay Terminal | Lock/Power Supply | Description |
|----------------|-------------------|-------------|
| COM (Common)   | 12V Power (+)     | Power Source|
| NO (Normally Open) | Lock (+)      | To Lock     |
| -              | Lock (-) to Power (-) | Ground Loop |

> [!NOTE]
> For this project, the Relay LED turning ON/OFF is sufficient to demonstrate the "Gate Opening".
