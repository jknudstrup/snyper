from machine import Pin, PWM, ADC
import asyncio

# Pin Assignments
SERVO_PIN = 16
PIEZO_PIN = 26

SERVO_FREQ = 50
HIT_THRESHOLD = 10000


def linear_interpolate(input, input_range, output_range):
    """
    Maps a value from one range to another proportionally.
    
    Args:
        input: The value to convert
        input_range: Tuple (min, max) of input range
        output_range: Tuple (min, max) of output range
    
    Returns:
        float: The interpolated value in the output range
    """
    input_min, input_max = input_range
    output_min, output_max = output_range
    return (input - input_min) * (output_max - output_min) / (input_max - input_min) + output_min


class PeripheralController:
    """
    Controls target peripherals: servo motor for target positioning and piezo sensor for hit detection.
    """
    
    def __init__(self, servo_pin, piezo_pin, servo_freq=50, hit_threshold=10000):
        """
        Initialize peripheral controller.
        
        Args:
            servo_pin: GPIO pin number for servo control
            piezo_pin: GPIO pin number for piezo sensor
            servo_freq: PWM frequency for servo control (default: 50Hz)
            hit_threshold: ADC value threshold for hit detection (default: 10000)
        """
        self.servo_pin = servo_pin
        self.piezo_pin = piezo_pin
        self.servo_freq = servo_freq
        self.hit_threshold = hit_threshold
        
        # Initialize hardware
        self.servo = PWM(Pin(self.servo_pin))
        self.servo.freq(self.servo_freq)
        self.piezo_in = ADC(Pin(self.piezo_pin))
    
    def _servo_write(self, angle_degrees):
        """
        Internal method to control servo position.
        
        Args:
            angle_degrees: Target angle (0-180 degrees)
        """
        pulse_width_ms = linear_interpolate(angle_degrees, (0, 180), (0.5, 2.5))
        pwm_duty_cycle = int(linear_interpolate(pulse_width_ms, (0, 20), (0, 65535)))
        self.servo.duty_u16(pwm_duty_cycle)
    
    async def raise_target(self):
        """
        Raise target to upright position (90 degrees).
        
        Returns:
            bool: True when movement is assumed complete (after 0.5s delay)
        """
        self._servo_write(90)
        await asyncio.sleep(0.5)
        return True
    
    async def lower_target(self):
        """
        Lower target to down position (0 degrees).
        
        Returns:
            bool: True when movement is assumed complete (after 0.5s delay)
        """
        print("Peripheral Controller received 'Lower' command")
        self._servo_write(0)
        await asyncio.sleep(0.5)
        return True
    
    def hit_was_detected(self):
        pot_value = self.piezo_in.read_u16()
        if pot_value > self.hit_threshold:
            return True
        return False

# Create default instance for easy importing
peripheral_controller = PeripheralController(SERVO_PIN, PIEZO_PIN, SERVO_FREQ, HIT_THRESHOLD)


# def activate(time_duration):
#     # Activate servo to stand up. If piezo exceeds threshold, lay back down and return true
#     # If time is exceeded, lay back down and return false
#     utime.sleep(.5)
#     start_time = utime.ticks_ms()
#     was_hit = False
#     while utime.ticks_diff(utime.ticks_ms(), start_time) < time_duration:
#         pot_value = piezo_in.read_u16()
#         if pot_value > HIT_THRESHOLD:
#             say(pot_value)
#             servo_write(servo, 0)
#             was_hit = True

#     say(f'Target {target_name} was hit: {was_hit}')
#     servo_write(servo, 0)
#     send_to_controller(str(was_hit))




