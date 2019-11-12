import sys
import helper

# Supported Commands
CLUSTER_INFO = 'info'
CONNECTIONS = 'c'
HELP = 'h'
EXIT = 'exit'
STATE = 'state'
TERM = 'term'

def repl(node):
    while True:
        commands = sys.stdin.readline().split()
        if len(commands) > 0:
		    command = commands[0]
		    if command == CLUSTER_INFO:
		        helper.print_and_flush(node.cluster_info)
		    elif command == CONNECTIONS:
		        helper.print_and_flush(node.sockets.keys())
		    elif command == STATE:
		        helper.print_and_flush(node.state)  
		    elif command == TERM:
		        helper.print_and_flush(node.term)            
		    elif command == HELP:
		        helper.print_and_flush("cluster_info: %s, connections: %s, state: %s, exit: %s" %(CLUSTER_INFO, CONNECTIONS, STATE, EXIT))
		    elif command == EXIT:
		        helper.print_and_flush("Goodbye!")
		        node.graceful_cleanup()
		        return
		    else:
		        helper.print_and_flush("Unsupported command. For list of supported commands type 'h'")
