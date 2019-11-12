import node
import constants
import repl
import sys
from threading import Thread
import time

def main():
    # Check command line arguments.
    if len(sys.argv) != constants.CLUSTER_INITIATOR_CMDS and len(sys.argv) != constants.JOINING_CLUSTER_CMDS:
        print('usage: main.py [id] [port] or start.py [id] [port] [ip address] [port]')            
        return

    # Error check the pass in port numbers.
    if not sys.argv[2].isdigit() and not sys.argv[4].isdigit():
        print('usage: main.py [port] or start.py [port] [ip address] [port]')            
        return        

    # Create a node.    
    id = sys.argv[1]
    port = sys.argv[2]
    n = node.Node(id, port)
    # Handle incoming connections.    
    handle_conn_thread = Thread(target=n.handleConnections, args=())
    handle_conn_thread.setDaemon(True)
    handle_conn_thread.start()
    if len(sys.argv) == constants.JOINING_CLUSTER_CMDS:
        rn = node.RemoteNode(sys.argv[3], sys.argv[4])
        # Request for node to join or rejoin the cluster.
        n.join(rn)
    else:
        start_thread = Thread(target=n.startCluster, args=())
        start_thread.setDaemon(True)
        start_thread.start()

    # Start the repl to query node diagnostics.
    repl.repl(n)

main()
