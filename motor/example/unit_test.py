from time import sleep
from adafruit_motorkit import MotorKit

kit = MotorKit()

def test_motor(motor, time_sec, throttle):
    if motor == "m1":
        kit.motor1.throttle = throttle
        sleep(time_sec)
        kit.motor1.throttle = 0
    elif motor == "m2":
        kit.motor2.throttle = throttle
        sleep(time_sec)
        kit.motor2.throttle = 0
    elif motor == "both":
        kit.motor1.throttle = throttle
        kit.motor2.throttle = throttle
        sleep(time_sec)
        kit.motor1.throttle = 0
        kit.motor2.throttle = 0

if __name__ == "__main__":
    test_time = 0.25 # seconds
    test_throttle = 1.0
    test_motor("m1", test_time, test_throttle)
    test_motor("m2", test_time, test_throttle)
    test_motor("both", test_time, test_throttle)

