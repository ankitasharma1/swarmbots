import random
import time

from communication.message import leader_heartbeat_msg, request_vote_msg, response_vote_msg, deserialize
from communication.MSG_CONFIG import REQUEST_VOTE, RESPONSE_VOTE, LEADER_HEARTBEAT

from RAFT_CONFIG import CLUSTER_SIZE, FOLLOWER, CANDIDATE, LEADER, ELECTION_TIMEOUT

old_time = time.time()


def do_raft(node):
    # Election timeout.
    random.seed(node.seed)
    election_timeout = random.randrange(ELECTION_TIMEOUT)
    print(election_timeout)
    election_results = dict()

    # Incoming messages.
    request_vote = []
    leader_heartbeat = []
    response_vote = []    

    # Starts as a follower.
    node.old_state = FOLLOWER
    node.state = FOLLOWER
    
    global old_time

    while True:
        # Check if we have received any messages.
        for other_id in node.other_s_ids:
            msg = node.recv_from(other_id)
            if msg:
                # Deserialize the message.
                msg = deserialize(msg)
                if msg:
                    # Check the message type.
                    msg_type = msg['type']
                    if msg_type == LEADER_HEARTBEAT:
                        leader_heartbeat.append(msg)
                    elif msg_type == REQUEST_VOTE:
                        request_vote.append(msg)
                    elif msg_type == RESPONSE_VOTE:
                        response_vote.append(msg)
                    else:
                        print(f"Unexpected type: {msg_type}")
        
        # TODO: clean up election_results for terms < than node.term
        
        if node.state == FOLLOWER:
            # A new follower.
            if node.old_state != node.state:
                print(f"I am now a follower for term {node.term}.")
                # Clear queues if we are transitioning to a new state.
                request_vote = []
                leader_heartbeat = []
                response_vote = []    
                old_time = time.time()
            
            # Continue being a follower.
            follower(node, request_vote, leader_heartbeat, election_timeout)
        elif node.state == CANDIDATE:
            # A new candidate.        
            if node.old_state != node.state:
                print(f"I am now a candidate for term {node.term}.") 
                # Clear queues if we are transitioning to a new state.
                request_vote = []
                leader_heartbeat = []
                response_vote = []                               
                # Start the election and send request votes.
                candidate_election_reset(node)
                # Grant vote for ourself.
                election_results.update({node.term: 1})
                # Reset the time.
                old_time = time.time()
            
            # Continue being a candidate.
            candidate(node, request_vote, leader_heartbeat, response_vote, election_timeout, election_results)
        elif node.state == LEADER:
            # A new leader.
            if node.old_state != node.state:
                print(f"I am now a leader for term {node.term}.")  
                # Clear queues if we are transitioning to a new state.
                request_vote = []
                leader_heartbeat = []
                response_vote = []                      
            else:
                # Chill out if you've been the leader.
                time.sleep(.2)
                
            # Continue being a leader.
            leader(node, leader_heartbeat, request_vote)
        else:
            print(f"Unknown state {node.state}")


def follower(node, request_vote, leader_heartbeat, election_timeout):
    #print(f">>> Follower State Term: {node.term}")
    global old_time
    
    # Check whether the election timeout has elapsed.
    if (time.time() - old_time) > election_timeout:
        print(f">>> F: no leader --> candidate {time.time()} {old_time}")
        node.old_state = FOLLOWER
        node.state = CANDIDATE
        return 
    else:
        # Check if we have correspondance from the leader.
        if len(leader_heartbeat) > 0:
            #print(">>> F: leader correspondance")
            leader_heartbeat_message = leader_heartbeat.pop(0)
            leader_term = int(leader_heartbeat_message['curr_term'])
            if leader_term >= node.term:
                node.term = leader_term
                # Go back to being a follower. Reset the time.
                node.voted_for = None
                old_time = time.time()

    # If we have received a request vote message.
    if len(request_vote) > 0:
        request_vote_message = request_vote.pop(0)
        candidate_term = int(request_vote_message['curr_term'])
        candidate_id = request_vote_message['id']

        if candidate_term < node.term:
            # Reject the vote.
            node.send_to([candidate_id], response_vote_msg(node.swarmer_id, node.term, False))
        elif node.voted_for == None:
            print(f">>> F: Granting vote for {candidate_id}")
            # Grant the vote.
            node.voted_for = candidate_id
            node.term = candidate_term                                  
            node.send_to([candidate_id], response_vote_msg(node.swarmer_id, node.term, True))
            # Reset the election.
            oldtime = time.time()  

    # At this point, our old_state is FOLLOWER.                    
    node.old_state = FOLLOWER                 


def candidate(node, request_vote, leader_heartbeat, response_vote, election_timeout, election_results):
    #print(f">>> Candidate State Term: {node.term}")
    global old_time
        
    if election_results.get(node.term) >= round(CLUSTER_SIZE / 2):
        print(f">>> C: Got {election_results} votes --> leader")
        node.old_state = CANDIDATE
        node.state = LEADER
        return

    # Check whether the election timeout has elapsed.  
    if ((time.time() - old_time) > election_timeout):
        # Reset the timer.
        old_time = time.time()
        # Start a new election.
        candidate_election_reset(node)
        # Vote for ourself.
        election_results = election_results.update({node.term: 1})
    else:
        # Check if we have correspondance from the leader.
        if len(leader_heartbeat) > 0:
            leader_heartbeat_message = leader_heartbeat.pop(0)
            leader_term = int(leader_heartbeat_message['curr_term'])
            if leader_term > node.term:
                node.term = leader_term
                node.voted_for = None
                print(">>> C: correspondance from leader --> follower")                                    
                # Go back to being a follower. 
                node.old_state = CANDIDATE
                node.state = FOLLOWER
                return

        # Process competing request vote.
        if len(request_vote) > 0:
            request_vote_message = request_vote.pop(0)
            candidate_term = int(request_vote_message['curr_term'])
            candidate_id = request_vote_message['id']
            print(f">>> C: Received request vote from {candidate_id} with term {candidate_term}")

            if candidate_term < node.term:
                # Reject the vote.
                node.send_to([candidate_id], response_vote_msg(node.swarmer_id, node.term, False))
                print(f">>> C: Rejecting vote for {candidate_id}")                
            else:
                # Grant the vote.
                node.term = candidate_term   
                node.voted_for = candidate_id               
                node.send_to([candidate_id], response_vote_msg(node.swarmer_id, node.term, True))
                # Go back to being a follower.
                node.old_state = CANDIDATE
                node.state = FOLLOWER
                print(f">>> C: Granting vote to {candidate_id}")
                return

        # Precess responses to vote.
        if len(response_vote) > 0:
            response_vote_message = response_vote.pop(0)
            vote = response_vote_message['vote']
            term = int(response_vote_message['curr_term'])

            # If we received a vote, record it.
            if vote:
                print(f">>> C; Received a vote for term {term} my_term = {node.term}")
                election_results = election_results.update({term: election_results.get(term) + 1})
            else:
                if node.term < term:
                    node.term = term
                    print(">>> C: voter term > mine --> follower")    
                    node.old_state = CANDIDATE                                                    
                    node.state = FOLLOWER
                    return

    # At this point, our old_state is CANDIDATE.                    
    node.old_state = CANDIDATE       


def candidate_election_reset(node):
    # Vote for self.
    node.voted_for = node.swarmer_id
    # Increment term.
    node.term = int(node.term) + 1
    # Send request votes to everyone.    
    for other_id in node.other_s_ids:
        node.send_to([other_id], request_vote_msg(node.swarmer_id, node.term))


def leader(node, leader_heartbeat, request_vote):
    #print(f">>> Leader State term: {node.term}")

    # Process competing request vote.
    if len(request_vote) > 0:
        print(">>> Received request vote")
        request_vote_message = request_vote.pop(0)
        candidate_term = int(request_vote_message['curr_term'])
        candidate_id = request_vote_message['id']

        if candidate_term < node.term:
            # Reject the vote.
            node.send_to([candidate_id], response_vote_msg(node.swarmer_id, node.term, False))
        else:
            # Grant the vote.
            print(f">>> L: Granting vote for {candidate_id} with term {candidate_term}")
            node.term = candidate_term
            node.voted_for = candidate_id                  
            node.send_to([candidate_id], response_vote_msg(node.swarmer_id, node.term, True))
            # Go back to being a follower.
            node.old_state = LEADER
            node.state = FOLLOWER
            return

    # Process leader heartbeat.
    if len(leader_heartbeat) > 0:
        leader_heartbeat_message = leader_heartbeat.pop(0)
        leader_term = int(leader_heartbeat_message['curr_term'])

        if leader_term > node.term:
            print(f">>> L: correspondance from leader with term {leader_term}--> follower") 
            node.term = leader_term  
            node.voted_for = None
            node.old_state = LEADER
            node.state = FOLLOWER
            return                             

    # Send leader heartbeats to everyone.    
    for other_id in node.other_s_ids:
        node.send_to([other_id], leader_heartbeat_msg(node.swarmer_id, node.term))
        
    # At this point, our old_state is LEADER.                    
    node.old_state = LEADER                    
