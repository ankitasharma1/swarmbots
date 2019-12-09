# message meta
MSG_SIZE = 512  # bytes
PADDING_BYTE = b' '

# socket config, this is how long the recv function will wait while checking
# for messages
RECV_TIMEOUT = 0.15  # seconds

# socket recv and send delay; we run into bandwidth issues over BT if we send
# and check recv as fast as we can
MSG_SEND_DELAY = RECV_TIMEOUT + 0.05
MSG_RECV_DELAY = RECV_TIMEOUT

# message types
REQUEST_VOTE = "request_vote"
RESPONSE_VOTE = "response_vote"
LEADER_HEARTBEAT = "leader_heart_beat"

