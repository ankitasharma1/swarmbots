import json

from MSG_CONFIG import REQUEST_VOTE, RESPONSE_VOTE, LEADER_HEARTBEAT


def leader_heartbeat_msg(s_id, curr_term):
    return make_msg(s_id, LEADER_HEARTBEAT, curr_term=curr_term)


def request_vote_msg(s_id, curr_term):
    return make_msg(s_id, REQUEST_VOTE, curr_term=curr_term)


def response_vote_msg(s_id, curr_term, vote):
    return make_msg(s_id, RESPONSE_VOTE, curr_term=curr_term, vote=vote)


def make_msg(s_id, msg_type, curr_term=None, vote=None):
    message = {
        'type': msg_type,
        'id': s_id,
        'curr_term': curr_term,
        'vote': vote
    }
    return json.dumps(message)


def deserialize(message):
    try:
        return json.loads(message)
    except Exception as e:
        print(e)
        print(f"{message} dropped")
        return None
