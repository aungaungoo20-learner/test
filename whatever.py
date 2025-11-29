"""
Raspberry Pi AC Controller using IR Transmitter
Requires: IR LED connected to GPIO pin (default GPIO 17)
Install: pip install pigpio
Run pigpio daemon: sudo pigpiod
"""

import pigpio
import time

class ACController:
    def __init__(self, gpio_pin=17):
        """
        Initialize AC controller with IR transmitter
        
        Args:
            gpio_pin: GPIO pin number where IR LED is connected
        """
        self.gpio_pin = gpio_pin
        self.pi = pigpio.pi()
        
        if not self.pi.connected:
            raise Exception("Failed to connect to pigpio daemon. Run: sudo pigpiod")
        
        # Common AC IR protocols use 38kHz carrier frequency
        self.carrier_freq = 38000
        
    def send_raw_code(self, pulses):
        """
        Send raw IR code as series of on/off pulses
        
        Args:
            pulses: List of pulse durations in microseconds [on, off, on, off, ...]
        """
        self.pi.wave_clear()
        self.pi.wave_add_generic([
            pigpio.pulse(1 << self.gpio_pin, 0, pulses[i]) if i % 2 == 0
            else pigpio.pulse(0, 1 << self.gpio_pin, pulses[i])
            for i in range(len(pulses))
        ])
        
        wave_id = self.pi.wave_create()
        if wave_id >= 0:
            self.pi.wave_send_once(wave_id)
            while self.pi.wave_tx_busy():
                time.sleep(0.01)
            self.pi.wave_delete(wave_id)
    
    def send_nec_command(self, address, command):
        """
        Send NEC protocol IR command (common for many AC units)
        
        Args:
            address: 8-bit address code
            command: 8-bit command code
        """
        # NEC protocol timing (in microseconds)
        header_mark = 9000
        header_space = 4500
        bit_mark = 560
        one_space = 1690
        zero_space = 560
        
        pulses = [header_mark, header_space]
        
        # Address (8 bits) + inverted address (8 bits)
        for i in range(8):
            pulses.append(bit_mark)
            pulses.append(one_space if (address >> i) & 1 else zero_space)
        
        for i in range(8):
            pulses.append(bit_mark)
            pulses.append(zero_space if (address >> i) & 1 else one_space)
        
        # Command (8 bits) + inverted command (8 bits)
        for i in range(8):
            pulses.append(bit_mark)
            pulses.append(one_space if (command >> i) & 1 else zero_space)
        
        for i in range(8):
            pulses.append(bit_mark)
            pulses.append(zero_space if (command >> i) & 1 else one_space)
        
        # Stop bit
        pulses.append(bit_mark)
        
        # Generate carrier wave
        self.pi.hardware_PWM(self.gpio_pin, self.carrier_freq, 500000)  # 50% duty cycle
        self.send_raw_code(pulses)
        self.pi.hardware_PWM(self.gpio_pin, 0, 0)  # Turn off carrier
    
    def power_on(self):
        """Turn AC power on (example codes - replace with your AC's codes)"""
        print("Sending Power ON command...")
        self.send_nec_command(0x00, 0x08)  # Example code
    
    def power_off(self):
        """Turn AC power off"""
        print("Sending Power OFF command...")
        self.send_nec_command(0x00, 0x09)  # Example code
    
    def set_temperature(self, temp):
        """
        Set AC temperature
        
        Args:
            temp: Temperature in Celsius (16-30 typically)
        """
        if not 16 <= temp <= 30:
            print("Temperature out of range (16-30°C)")
            return
        
        print(f"Setting temperature to {temp}°C...")
        # Map temperature to command code (example mapping)
        command = 0x10 + (temp - 16)
        self.send_nec_command(0x00, command)
    
    def set_mode(self, mode):
        """
        Set AC mode
        
        Args:
            mode: 'cool', 'heat', 'fan', 'dry', 'auto'
        """
        modes = {
            'cool': 0x30,
            'heat': 0x31,
            'fan': 0x32,
            'dry': 0x33,
            'auto': 0x34
        }
        
        if mode.lower() not in modes:
            print(f"Invalid mode. Choose from: {list(modes.keys())}")
            return
        
        print(f"Setting mode to {mode}...")
        self.send_nec_command(0x00, modes[mode.lower()])
    
    def set_fan_speed(self, speed):
        """
        Set fan speed
        
        Args:
            speed: 'low', 'medium', 'high', 'auto'
        """
        speeds = {
            'low': 0x40,
            'medium': 0x41,
            'high': 0x42,
            'auto': 0x43
        }
        
        if speed.lower() not in speeds:
            print(f"Invalid speed. Choose from: {list(speeds.keys())}")
            return
        
        print(f"Setting fan speed to {speed}...")
        self.send_nec_command(0x00, speeds[speed.lower()])
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.pi.stop()


# Example usage
if __name__ == "__main__":
    # Initialize controller
    ac = ACController(gpio_pin=17)
    
    try:
        # Turn on AC
        ac.power_on()
        time.sleep(2)
        
        # Set to cooling mode
        ac.set_mode('cool')
        time.sleep(1)
        
        # Set temperature to 24°C
        ac.set_temperature(24)
        time.sleep(1)
        
        # Set fan speed to medium
        ac.set_fan_speed('medium')
        time.sleep(1)
        
        # Wait before turning off
        print("\nAC is running. Press Ctrl+C to turn off...")
        time.sleep(10)
        
        # Turn off AC
        ac.power_off()
        
    except KeyboardInterrupt:
        print("\nTurning off AC...")
        ac.power_off()
    finally:
        ac.cleanup()
        print("Cleanup complete")