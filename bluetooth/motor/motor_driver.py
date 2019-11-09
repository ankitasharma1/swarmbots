from time import sleep
from adafruit_motorkit import MotorKit

def failsafe(func):
    def wrapper(*args, **kw_args):
        try:
            return func(*args, **kw_args)
        except Exception:
            self = args[0]
            self.kit.motor1.throttle = 0
            self.kit.motor2.throttle = 0
            print("ERROR: motor failure detected, motors shutdown")
    return wrapper

class MotorDriver():
    def __init__(self, throttle, run_time):
        self.kit = MotorKit()
        self.throttle = throttle
        self.run_time = run_time

    @failsafe
    def right(self):
        self.kit.motor2.throttle = self.throttle
        sleep(self.run_time)
        self.kit.motor2.throttle = 0

    @failsafe
    def left(self):
        self.kit.motor1.throttle = self.throttle
        sleep(self.run_time)
        self.kit.motor1.throttle = 0

    @failsafe
    def forward(self):
        self.kit.motor1.throttle = self.throttle
        self.kit.motor2.throttle = self.throttle
        sleep(self.run_time)
        self.kit.motor1.throttle = 0
        self.kit.motor2.throttle = 0

    @failsafe
    def backward(self):
        self.kit.motor1.throttle = -1 * self.throttle
        self.kit.motor2.throttle = -1 * self.throttle
        sleep(self.run_time)
        self.kit.motor1.throttle = 0
        self.kit.motor2.throttle = 0
   

if __name__ == '__main__':
    from MOTOR_CONFIG import THROTTLE, RUN_TIME
    
    md = MotorDriver(THROTTLE, RUN_TIME)
    md.right()
    md.left()
    md.forward()
    md.backward()
