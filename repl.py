import sys
import helper

# Supported Commands
CLUSTER_INFO = 'info'
CONNECTIONS = 'c'
HELP = 'h'
EXIT = 'exit'
STATE = 'state'

def repl(node):
    while True:
        commands = sys.stdin.readline().split()
        command = commands[0]
        if command == CLUSTER_INFO:
            helper.print_and_flush(node.cluster_info)
        elif command == CONNECTIONS:
            helper.print_and_flush(node.sockets.keys())
        elif command == STATE:
            helper.print_and_flush(node.state)            
        elif command == HELP:
            helper.print_and_flush("cluster_info: %s, connections: %s, exit: %s" %(CLUSTER_INFO, CONNECTIONS, EXIT))
        elif command == EXIT:
            helper.print_and_flush("Goodbye!")
            n.graceful_cleanup()
            return
        else:
            helper.print_and_flush("Unsupported command. For list of supported commands type 'h'")
