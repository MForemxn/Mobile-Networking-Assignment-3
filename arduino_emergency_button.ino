/*
  Emergency Vehicle Button - Arduino Sketch
  Simple button that triggers emergency signal via serial communication
  
  Hardware Setup:
  - Button connected to pin 2 (with internal pullup)
  - LED (optional) on pin 13 for visual feedback
  - Arduino connected via USB to computer running backend server
  
  Usage:
  - Press button once: Activates emergency (LED on)
  - Press button again: Deactivates emergency (LED off)
*/

const int BUTTON_PIN = 2;      // Button input pin
const int LED_PIN = 13;        // LED output pin (built-in LED)
const int DEBOUNCE_DELAY = 50; // Debounce time in milliseconds

bool emergencyActive = false;  // Track emergency state
bool lastButtonState = HIGH;   // Previous button state
bool currentButtonState = HIGH; // Current button state
unsigned long lastDebounceTime = 0;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Set up pins
  pinMode(BUTTON_PIN, INPUT_PULLUP);  // Use internal pullup resistor
  pinMode(LED_PIN, OUTPUT);
  
  // Initial state
  digitalWrite(LED_PIN, LOW);
  
  // Wait for serial to initialize
  delay(1000);
  Serial.println("READY");
  Serial.println("Arduino Emergency Button Initialized");
}

void loop() {
  // Read button state
  int reading = digitalRead(BUTTON_PIN);
  
  // Debounce logic
  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }
  
  if ((millis() - lastDebounceTime) > DEBOUNCE_DELAY) {
    // If button state has changed
    if (reading != currentButtonState) {
      currentButtonState = reading;
      
      // Button was pressed (LOW because of pullup)
      if (currentButtonState == LOW) {
        // Toggle emergency state
        emergencyActive = !emergencyActive;
        
        // Send command to Python backend
        if (emergencyActive) {
          Serial.println("EMERGENCY_ON");
          digitalWrite(LED_PIN, HIGH);  // Turn on LED
        } else {
          Serial.println("EMERGENCY_OFF");
          digitalWrite(LED_PIN, LOW);   // Turn off LED
        }
        
        // Brief delay to prevent immediate re-trigger
        delay(200);
      }
    }
  }
  
  lastButtonState = reading;
  
  // Optional: Blink LED when emergency is active
  if (emergencyActive) {
    // Slow blink for visual feedback
    static unsigned long lastBlink = 0;
    if (millis() - lastBlink > 500) {
      digitalWrite(LED_PIN, !digitalRead(LED_PIN));
      lastBlink = millis();
    }
  }
}

