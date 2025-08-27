from machine import Pin, PWM, ADC

servo = PWM(Pin(16))
servo.freq(50)

piezo_in = ADC(Pin(26))

def interval_mapping(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def servo_write(pin, angle):
    pulse_width = interval_mapping(angle, 0, 180, 0.5, 2.5)
    duty = int(interval_mapping(pulse_width, 0, 20, 0, 65535))
    pin.duty_u16(duty)
    
def raise_target():
    servo_write(servo, 90)
    
def lower_target():
    servo_write(servo, 0)


# def activate(time_duration):
#     # Activate servo to stand up. If piezo exceeds threshold, lay back down and return true
#     # If time is exceeded, lay back down and return false
#     utime.sleep(.5)
#     start_time = utime.ticks_ms()
#     was_hit = False
#     while utime.ticks_diff(utime.ticks_ms(), start_time) < time_duration:
#         pot_value = piezo_in.read_u16()
#         if pot_value > 10000:
#             say(pot_value)
#             servo_write(servo, 0)
#             was_hit = True

#     say(f'Target {target_name} was hit: {was_hit}')
#     servo_write(servo, 0)
#     send_to_controller(str(was_hit))




