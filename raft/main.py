import sys
from time import sleep
from node import Node

# Check command line arguments.
if len(sys.argv) != 2:
    print('usage: main.py [id]')
    sys.exit(1)

# Unique node id.
node_id = sys.argv[1]

n = Node(node_id)

# Node 'init' routine.
n.init()

sleep(1)

n.send_to(['S1', 'S2', 'S3'], "hello all") 
