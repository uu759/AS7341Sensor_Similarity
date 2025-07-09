#include <Arduino.h>
#include <FastLED.h>

#define LED_PIN 6  // Data pin for the LED strip
#define NUM_LEDS 8 // Number of LEDs on the strip

CRGB leds[NUM_LEDS];

void setup()
{
  Serial.begin(9600);
  while (!Serial)
  {
    ; // Wait for serial port to connect. Needed for native USB port only
  }
  Serial.println("Arduino LED Control Ready");

  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(50); // Set a default brightness
  FastLED.clear();
  FastLED.show();
}

void loop()
{
  if (Serial.available())
  {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove any whitespace

    // Expected command format: "INDEX,R,G,B"
    // Example: "0,255,0,0" (sets LED 0 to red)
    // Example: "all,255,255,255" (sets all LEDs to white)

    int firstComma = command.indexOf(',');
    int secondComma = command.indexOf(',', firstComma + 1);
    int thirdComma = command.indexOf(',', secondComma + 1);

    if (firstComma != -1 && secondComma != -1 && thirdComma != -1)
    {
      String indexStr = command.substring(0, firstComma);
      int r = command.substring(firstComma + 1, secondComma).toInt();
      int g = command.substring(secondComma + 1, thirdComma).toInt();
      int b = command.substring(thirdComma + 1).toInt();

      r = constrain(r, 0, 255);
      g = constrain(g, 0, 255);
      b = constrain(b, 0, 255);

      if (indexStr.equalsIgnoreCase("all"))
      {
        for (int i = 0; i < NUM_LEDS; i++)
        {
          leds[i] = CRGB(r, g, b);
        }
        Serial.println("All LEDs set.");
      }
      else
      {
        int ledIndex = indexStr.toInt();
        if (ledIndex >= 0 && ledIndex < NUM_LEDS)
        {
          leds[ledIndex] = CRGB(r, g, b);
          Serial.print("LED ");
          Serial.print(ledIndex);
          Serial.println(" set.");
        }
        else
        {
          Serial.println("Error: Invalid LED index.");
        }
      }
      FastLED.show();
    }
    else if (command.equalsIgnoreCase("clear"))
    {
      FastLED.clear();
      FastLED.show();
      Serial.println("All LEDs cleared.");
    }
    else
    {
      Serial.println("Error: Invalid command format. Use 'INDEX,R,G,B' or 'all,R,G,B' or 'clear'.");
    }
  }
}
