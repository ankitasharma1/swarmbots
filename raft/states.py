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

def follower(node):
    print(f">>> Follower State Term: {node.term}")

    # Update the state.
    node.state = FOLLOWER

    random.seed(time.time())
    old_time = time.time()
    election_timeout = random.randrange(ELECTION_TIMEOUT)

    # Incoming messages.
    request_vote = []
    leader_heartbeat = []

    while True:
        # Check if we have received any messages.
        for other_id in node.other_s_ids:
            msg = node.recv_from(other_id)
            if msg:
                msg = message.deserialize(msg)
                msg_type = msg[message.TYPE]
                if msg_type == message.LEADER_HEARTBEAT:
                    leader_hearbeat.append(msg)
                elif msg_type == message.REQUEST_VOTE:
                    request_vote.append(msg)
                else:
                    print(f"Unexpected type: {msg_type}")


        # Check whether the election timeout has elapsed.
        if ((time.time() - old_time) > ELECTION_TIMEOUT):
            print(">>> F: no leader --> candidate")
            return candidate(node)
        else:
            # Check if we have correspondance from the leader.
            if len(leader_heartbeat) > 0:
                leader_hearbeat_message = leader_heartbeat.pop(0)
                leader_term = int(leader_hearbeat_message[message.CURR_TERM])
                if leader_term > node.term:
                    node.term = leader_term
                    # Go back to being a follower. Reset the time.
                    old_time = time.time()

        # If we have received a request vote message.
        if len(request_vote) > 0:
            request_vote_message = request_vote.pop(0)
            candidate_term = request_vote_message[message.CURR_TERM]
            candidate_id = request_vote_message[message.ID]

            if candidate_term < node.term:
                # Reject the vote.
                node.send_to([candidate_id], message.responseVoteMessage(node.id, node.term, False))
            else:
                # Grant the vote.
                node.term = candidate_term                                  
                node.send_to([candidate_id], message.responseVoteMessage(node.id, node.term, True))
                # Reset the election.
                oldtime = time.time()            

def candidate(node):
    print(f">>> Candidate State Term: {node.term}")

    # Update the state.
    node.state = CANDIDATE
    election_results = candidate_election_reset(node)

    random.seed(time.time())
    old_time = time.time()
    election_timeout = random.randrange(ELECTION_TIMEOUT)
    
    # Incoming messages.
    request_vote = []
    leader_heartbeat = []
    response_vote = []

    while True:
        # Check if we have received any messages.
        for other_id in node.other_s_ids:
            msg = node.recv_from(other_id)
            if msg:
                msg = message.deserialize(msg)
                msg_type = msg[message.TYPE]
                if msg_type == message.LEADER_HEARTBEAT:
                    leader_hearbeat.append(msg)
                elif msg_type == message.REQUEST_VOTE:
                    request_vote.append(msg)
                elif msg_type == message.RESPONSE_VOTE:
                    response_vote.append(msg)
                else:
                    print(f"Unexpected type: {msg_type}")

        if election_results >= round(CONFIG_SIZE/2):
            print(f">>> C: Got {election_results} votes --> leader")
            return leader(node)

        # Check whether the electiontimeout has elapsed.  
        if ((time.time() - old_time) > ELECTION_TIMEOUT):
            # Reset the timer.
            old_time = time.time()
            # Start a new election.
            election_results = candidate_election_reset(node)
        else:
            # Check if we have correspondance from the leader.
            if len(leader_heartbeat) > 0:
                leader_hearbeat_message = leader_heartbeat.pop(0)
                leader_term = int(leader_hearbeat_message[message.CURR_TERM])
                if leader_term > node.term:
                    node.term = leader_term
                    helper.print_and_flush(">>> C: correspondance from leader --> follower")                                    
                    # Go back to being a follower. 
                    return follower(node)

        # Process competing request vote.
        if len(request_vote) > 0:
            print(">>> Received request vote")
            request_vote_message = request_vote.pop(0)
            candidate_term = request_vote_message[message.CURR_TERM]
            candidate_id = request_vote_message[message.ID]

            if candidate_term < node.term:
                # Reject the vote.
                node.send_to([candidate_id], message.responseVoteMessage(node.id, node.term, False))
            else:
                # Grant the vote.
                node.term = candidate_term                  
                node.send_to([candidate_id], message.responseVoteMessage(node.id, node.term, True))
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