import sys
from node import Node
from communication.SWARMER_ID import SWARMER_ID
from calibrate_rssi import RssiCalibrator

# TODO: uncomment for presentation
# Callibrate per the room.
r = RssiCalibrator()
r.calibrate()
r.store_rssi()

# Create the node object.
n = Node(SWARMER_ID, wifi=False, debug=False)

# Run 'init' routine.
n.init()
