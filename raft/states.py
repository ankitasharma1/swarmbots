import helper
import constants
import time
import message
from threading import Thread
import random

def follower(node):
    helper.print_and_flush(">>> Follower State term: %s" %(node.term))

    # Update the state.
    node.state = constants.FOLLOWER

    random.seed(time.time())
    oldtime = time.time()
    election_timeout = random.randrange(node.config.election_timeout)

    while True:
        # Check whether election time out has elapsed.
        diff = time.time() - oldtime
        if (diff > election_timeout):
            # If there is no leader, enter the candidate phase.
            if node.leader == None:
                helper.print_and_flush(">>> F: no leader --> candidate")
                return candidate(node)
        else:
            # If we receive heartbeat from leader.
            if len(node.leader_heartbeat) > 0:
                node.leader_heartbeat_lock.acquire()
                node.leader_heartbeat = []
                node.leader_heartbeat_lock.release()
                # Go back to being a follower.
                node.voted_for = None
                #helper.print_and_flush(">>> F: correspondance from leader --> follower")                
                oldtime = time.time()

        # If we receive a request vote message.
        if len(node.request_vote) > 0:
            node.request_vote_lock.acquire()
            request_vote_message = node.request_vote.pop(0)
            node.request_vote = []
            node.request_vote_lock.release()

            candidate_term = request_vote_message.get(message.CURR_TERM)
            candidate_id = request_vote_message.get(message.ID)

            node.sockets_lock.acquire()
            candidate_socket = node.sockets.get(candidate_id)
            node.sockets_lock.release()

            # If the candidate's term is less than our own, reject.
            if candidate_term < node.term:
                helper.print_and_flush(">>> F: reject vote for %s" %(candidate_id))
                candidate_socket.send(message.responseVoteMessage(node.id, node.term, False))
            elif node.voted_for == None:
                helper.print_and_flush(">>> F: vote granted for %s" %(candidate_id))
                # Grant the vote.
                node.voted_for = candidate_id
                node.term = candidate_term
                candidate_socket.send(message.responseVoteMessage(node.id, node.term, True))
                # Restart the election.
                oldtime = time.time()

def candidate(node):
    # Update the state.
    node.state = constants.CANDIDATE
    candidate_election_reset(node)
    
    # We count ourselves. Start at 1 rather than 0.
    election_results = 1

    helper.print_and_flush(">>> Candidate State term %s:" %(node.term))

    random.seed(time.time())
    oldtime = time.time()

    while True:
        if election_results >= round(node.config.size/2):
            helper.print_and_flush(">>> C: Got %d votes --> leader" %(election_results))
            return leader(node)

        # Check whether election timeout has elapsed.
        diff = time.time() - oldtime
        if diff > random.randrange(node.config.election_timeout):
            # Reset the timer.          
            oldtime = time.time()
            # Election timeout elapses, start a new election.            
            election_results = 1
            candidate_election_reset(node)
        else:
            # If we receive heartbeat from leader.
            if len(node.leader_heartbeat) > 0:
                node.leader_heartbeat_lock.acquire()
                node.leader_heartbeat = []
                node.leader_heartbeat_lock.release()
                # Go back to being a follower.
                node.voted_for = None
                helper.print_and_flush(">>> C: correspondance from leader --> follower")                
                return follower(node)

            # Process competing request to vote.
            if len(node.request_vote) > 0:
                print(">>> Received request vote")
                node.request_vote_lock.acquire()
                request_vote_message = node.request_vote.pop(0)
                node.request_vote = []
                node.request_vote_lock.release()

                candidate_term = request_vote_message.get(message.CURR_TERM)
                candidate_id = request_vote_message.get(message.ID)
                node.sockets_lock.acquire()
                candidate_socket = node.sockets.get(candidate_id)
                node.sockets_lock.release()

                # Reject vote.
                if candidate_term < node.term:
                    helper.print_and_flush(">>> C: reject vote for %s" %(candidate_id))  
                    candidate_socket.send(message.responseVoteMessage(node.id, node.term, False)) 
                else: # Grant vote. Go back to being a follower.
                    helper.print_and_flush(">>> C: vote granted %s" %(candidate_id)) 
                    node.voted_for = candidate_id
                    node.term = candidate_term
                    candidate_socket.send(message.responseVoteMessage(node.id, node.term, True))
                    return follower(node)

            # Process responses to vote.
            if len(node.response_vote) > 0:
                node.response_vote_lock.acquire()
                response_vote_message = node.response_vote.pop(0)
                node.response_vote = []
                node.response_vote_lock.release()
                vote = response_vote_message.get(message.VOTE)
                term = int(response_vote_message.get(message.CURR_TERM))
                # If we received a vote, record it.
                if vote:
                    helper.print_and_flush(">>> C: received a vote")              
                    election_results = election_results + 1

                else:
                    if node.term < term:
                        node.term = term
                        helper.print_and_flush(">>> C: voter term > mine --> follower")                                                        
                        return follower(node)


def candidate_election_reset(node):
    # Vote for self.
    node.voted_for = node.id
    # Increment term.
    node.term = int(node.term) + 1
    # Set leader to None.
    node.leader = None

    # Send request votes.
    node.sockets_lock.acquire()
    for id, socket in node.sockets.items():        
        socket.send(message.requestVoteMessage(node.id, node.term))   
    node.sockets_lock.release()

def leader(node):
    helper.print_and_flush(">>> Leader State term: %s" %(node.term))

    # Update the state.
    node.state = constants.LEADER

    while True:
        # Send leader heartbeats.
        node.sockets_lock.acquire()
        for id, socket in node.sockets.items():        
            socket.send(message.leaderHeartBeat(node.id))   
        node.sockets_lock.release()    
