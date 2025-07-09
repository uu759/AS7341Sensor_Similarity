import serial
import time

# Configure the serial port
# IMPORTANT: Replace 'COM3' with the actual serial port of your Arduino
# You can find this in the Arduino IDE or your system's device manager.
# On Linux/macOS, it might be something like '/dev/ttyACM0' or '/dev/ttyUSB0'.
SERIAL_PORT = 'COM3'
BAUD_RATE = 9600

def send_command(ser, command):
    """Sends a command string to the Arduino via serial."""
    ser.write(command.encode() + b'\n')
    print(f"Sent: {command}")
    time.sleep(0.1) # Give Arduino time to process
    while ser.in_waiting: # Read response from Arduino
        print(f"Received: {ser.readline().decode().strip()}")

def set_led_color(ser, index, r, g, b):
    """Sets the color of a specific LED or all LEDs."""
    command = f"{index},{r},{g},{b}"
    send_command(ser, command)

def clear_all_leds(ser):
    """Turns off all LEDs."""
    send_command(ser, "clear")

if __name__ == "__main__":
    try:
        # Establish serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Allow some time for the serial connection to establish
        print(f"Connected to Arduino on {SERIAL_PORT}")

        # --- Example Usage ---

        # Clear all LEDs initially
        clear_all_leds(ser)
        time.sleep(1)

        # Set LED 0 to red
        set_led_color(ser, 0, 255, 0, 0)
        time.sleep(1)

        # Set LED 1 to green
        set_led_color(ser, 1, 0, 255, 0)
        time.sleep(1)

        # Set LED 2 to blue
        set_led_color(ser, 2, 0, 0, 255)
        time.sleep(1)

        # Set LED 3 to yellow
        set_led_color(ser, 3, 255, 255, 0)
        time.sleep(1)

        # Set all LEDs to white
        set_led_color(ser, "all", 255, 255, 255)
        time.sleep(2)

        # Clear all LEDs again
        clear_all_leds(ser)
        time.sleep(1)

        print("Demonstration complete.")

    except serial.SerialException as e:
        print(f"Error: Could not open serial port {SERIAL_PORT}. Please check if Arduino is connected and the port is correct.")
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")
