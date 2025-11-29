import RPi.GPIO as GPIO
import time

GPIO_PIN = 17   
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.OUT)

print(f"Blinking GPIO pin {GPIO_PIN}...")
print("Press Ctrl+C to stop the script and clean up.")

try:
    while True:
        GPIO.output(GPIO_PIN, GPIO.HIGH)
        print("LED is ON")
        time.sleep(1)
        GPIO.output(GPIO_PIN, GPIO.LOW)
        print("LED is OFF")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nScript interrupted by user.")

finally:
    GPIO.cleanup()
    print("GPIO clean up completed. Exiting script.")
    