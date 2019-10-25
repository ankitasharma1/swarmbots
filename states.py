import helper
import constants

def follower(node):
    helper.print_and_flush(">>> Follower State")
    # Update the state.
    node.state = constants.FOLLOWER
    helper.print_and_flush(node.getSocketConnections())

def candidate(node):
    helper.print_and_flush(">>> Candidate State")
    # Update the state.
    node.state = constants.CANDIDATE

def leader(node):
    helper.print_and_flush(">>> Leader State")
    # Update the state.
    node.state = constants.LEADER    