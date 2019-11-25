import random
import time
import message

"""
Election details.
"""
ELECTION_TIMEOUT = 10

"""
Cluster details.
"""
CONFIG_SIZE = 3

"""
States
"""
FOLLOWER = 'follower'
CANDIDATE = 'candidate'
LEADER = 'leader'

def do_raft(node):
    # Election timeout.
    random.seed(time.time())
    old_time = time.time()
    election_timeout = random.randrange(ELECTION_TIMEOUT)
    election_results = dict()

    # Incoming messages.
    request_vote = []
    leader_heartbeat = []
    response_vote = []    

    # Starts as a follower.
    node.state = FOLLOWER

    while True:
        # Check if we have received any messages.
        for other_id in node.other_s_ids:
            msg = node.recv_from(other_id)
            if msg:
                msg = message.deserialize(msg)
                msg_type = msg[message.TYPE]
                if msg_type == message.LEADER_HEARTBEAT:
                    leader_heartbeat.append(msg)
                elif msg_type == message.REQUEST_VOTE:
                    request_vote.append(msg)
                elif msg_type == message.RESPONSE_VOTE:
                    response_vote.append(msg)
                else:
                    print(f"Unexpected type: {msg_type}")        

        if node.state == FOLLOWER:
            follower(node, request_vote, leader_heartbeat, election_timeout, old_time)
        elif node.state == CANDIDATE:
            candidate(node, request_vote, leader_heartbeat, response_vote, election_timeout, old_time, election_results)
        elif node.state == LEADER:
            pass
        else:
            print(f"Unknown state {node.state}")

def follower(node, request_vote, leader_heartbeat, election_timeout, old_time):
    print(f">>> Follower State Term: {node.term}")

    # Check whether the election timeout has elapsed.
    if ((time.time() - old_time) > election_timeout):
        print(">>> F: no leader --> candidate")
        node.state = CANDIDATE
        return 
    else:
        # Check if we have correspondance from the leader.
        if len(leader_heartbeat) > 0:
            leader_heartbeat_message = leader_heartbeat.pop(0)
            leader_term = int(leader_heartbeat_message[message.CURR_TERM])
            if leader_term >= node.term:
                node.term = leader_term
                # Go back to being a follower. Reset the time.
                old_time = time.time()

    # If we have received a request vote message.
    if len(request_vote) > 0:
        request_vote_message = request_vote.pop(0)
        candidate_term = int(request_vote_message[message.CURR_TERM])
        candidate_id = request_vote_message[message.ID]

        if candidate_term < node.term:
            # Reject the vote.
            node.send_to([candidate_id], message.responseVoteMessage(node.swarmer_id, node.term, False))
        else:
            # Grant the vote.
            node.term = candidate_term                                  
            node.send_to([candidate_id], message.responseVoteMessage(node.swarmer_id, node.term, True))
            # Reset the election.
            oldtime = time.time()            

def candidate(node, request_vote, leader_heartbeat, response_vote, election_timeout, old_time, election_results):
    print(f">>> Candidate State Term: {node.term}")

    if election_results.get(node.term)
    election_results = candidate_election_reset(node)

    if election_results >= round(CONFIG_SIZE/2):
        print(f">>> C: Got {election_results} votes --> leader")
        return leader(node)

    # Check whether the electiontimeout has elapsed.  
    if ((time.time() - old_time) > election_timeout):
        # Reset the timer.
        old_time = time.time()
        # Start a new election.
        election_results = candidate_election_reset(node)
    else:
        # Check if we have correspondance from the leader.
        if len(leader_heartbeat) > 0:
            leader_heartbeat_message = leader_heartbeat.pop(0)
            leader_term = int(leader_heartbeat_message[message.CURR_TERM])
            if leader_term > node.term:
                node.term = leader_term
                print(">>> C: correspondance from leader --> follower")                                    
                # Go back to being a follower. 
                node.state = FOLLOWER
                return

        # Process competing request vote.
        if len(request_vote) > 0:
            print(">>> Received request vote")
            request_vote_message = request_vote.pop(0)
            candidate_term = int(request_vote_message[message.CURR_TERM])
            candidate_id = request_vote_message[message.ID]

            if candidate_term < node.term:
                # Reject the vote.
                node.send_to([candidate_id], message.responseVoteMessage(node.swarmer_id, node.term, False))
            else:
                # Grant the vote.
                node.term = candidate_term                  
                node.send_to([candidate_id], message.responseVoteMessage(node.swarmer_id, node.term, True))
                # Go back to being a follower.
                return follower(node)

        # Precess responses to vote.
        if len(response_vote) > 0:
            print(">>> Response vote")
            response_vote_message = response_vote.pop(0)
            vote = response_vote_message[message.VOTE]
            term = int(response_vote_message[message.CURR_TERM])

            # If we received a vote, record it.
            if vote:
                print(">>> C; Received a vote")
                election_results = election_results + 1
            else:
                if node.term < term:
                    node.term = term
                    print(">>> C: voter term > mine --> follower")                                                        
                    return follower(node)


def candidate_election_reset(node):
    # Increment term.
    node.term = int(node.term) + 1
    # Send request votes to everyone.    
    for other_id in node.other_s_ids:
        node.send_to([other_id], message.requestVoteMessage(node.swarmer_id, node.term))    
    # Return election results. Return 1 because we vote for ourself.
    return 1

def leader(node):
    print(f">>> Leader State term: {node.term}")

    # Update the state.
    node.state = LEADER 

    # Incoming messages.
    leader_heartbeat = []
    request_vote = []    

    while True:
        # Check if we have received any messages.
        for other_id in node.other_s_ids:
            msg = node.recv_from(other_id)
            if msg:
                msg = message.deserialize(msg)
                msg_type = msg[message.TYPE]
                if msg_type == message.LEADER_HEARTBEAT:
                    leader_heartbeat.append(msg)
                elif msg_type == message.REQUEST_VOTE:
                    request_vote.append(msg)
                else:
                    print(f"Unexpected type: {msg_type}")

        # Process competing request vote.
        if len(request_vote) > 0:
            print(">>> Received request vote")
            request_vote_message = request_vote.pop(0)
            candidate_term = int(request_vote_message[message.CURR_TERM])
            candidate_id = request_vote_message[message.ID]

            if candidate_term < node.term:
                # Reject the vote.
                node.send_to([candidate_id], message.responseVoteMessage(node.swarmer_id, node.term, False))
            else:
                # Grant the vote.
                node.term = candidate_term                  
                node.send_to([candidate_id], message.responseVoteMessage(node.swarmer_id, node.term, True))
                # Go back to being a follower.
                return follower(node)

        # Process leader heartbeat.
        if len(leader_heartbeat) > 0:
            leader_heartbeat_message = leader_heartbeat.pop(0)
            leader_term = int(leader_heartbeat_message[message.CURR_TERM])

            if leader_term > node.term:
                print(">>> L: correspondance from leader --> follower") 
                node.term = leader_term                               
                return follower(node)

        # Send request votes to everyone.    
        for other_id in node.other_s_ids:
            node.send_to([other_id], message.leaderHeartBeat(node.swarmer_id, node.term))    