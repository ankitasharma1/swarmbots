from communication.recv_from import RecvFromAgent
from communication.SWARMER_BT_INFO import UUID

from motor.motor_driver import MotorDriver
from motor.MOTOR_CONFIG import THROTTLE, RUN_TIME, MSG_SIZE

md = MotorDriver(THROTTLE, RUN_TIME)

try:
    recv_agent = RecvFromAgent(UUID, MSG_SIZE)
    recv_agent.advertise()
    while True:
        receivedData = recv_agent.read()
        if receivedData == b'forward':
            md.forward()
        if receivedData == b'backward':
            md.backward()
        if receivedData == b'right':
            md.right()
        if receivedData == b'left':
            md.left()
except:
    print("ERROR: exception detected, starting clean up")

recv_agent.clean_up()

