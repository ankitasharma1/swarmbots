import sys
from node import Node
from communication.SWARMER_ID import SWARMER_ID

# Callibrate per the room.


n = Node(SWARMER_ID, wifi=False, debug=False)

# Node 'init' routine.
n.init()
