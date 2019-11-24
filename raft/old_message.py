import constants
import json
import ruamel.yaml as yaml
import helper

MESSAGE_SIZE = 1024
NOP = "x"

# Message Type
TYPE = "type"
JOIN = "join"
START = "start"
CONNECT = "connect"
REQUEST_VOTE = "request_vote"
RESPONSE_VOTE = "response_vote"
LEADER_HEARTBEAT = "leader_heart_beat"

# Params for JOIN
ID = "id"
IP = "ip"
PORT = "port"

# Params for START
CLUSTER_INFO = "cluster_info"

# Params for REQUEST_VOTE
CURR_TERM = "curr_term"

# Params for RESPONSE_VOTE
VOTE = "vote"

# Misc. Params
PADDING = "padding"

#--------------------------------------------#
# Leader heart beat
def leaderHeartBeat(id, curr_term):
  message = {TYPE: LEADER_HEARTBEAT, 
             ID: id,
             CURR_TERM: str(curr_term)}
  message = serialize(message)
  return json.dumps(message)

# Request vote message
def requestVoteMessage(id, curr_term):
  message = {TYPE: REQUEST_VOTE, 
             ID: id, 
             CURR_TERM: str(curr_term)}
  message = serialize(message)             
  return json.dumps(message)

# Response vote message
def responseVoteMessage(id, curr_term, vote):
  message = {TYPE: RESPONSE_VOTE, 
             ID: id, 
             CURR_TERM: str(curr_term), 
             VOTE: vote}
  message = serialize(message)
  return json.dumps(message)

# Message to connect to another node
def connectMessage(id):
    message = {TYPE: CONNECT,
               ID: id}
    message = serialize(message)
    return json.dumps(message)

# When joining the cluster, the node sends its id, ip address
# and port number.
def joinMessage(id, ip, port):
    message = {TYPE: JOIN, 
               ID: id,
               IP: ip, PORT: port}
    message = serialize(message)
    return json.dumps(message)

# When all nodes have connected to the cluster, send a message
# with all of the contact details for the other  nodes so that 
# every node knows the other node's existence.
def startMessage(id, clusterInfo):
    message = {TYPE: START,
        ID: id,
        CLUSTER_INFO: clusterInfo
    }
    message = serialize(message)
    return json.dumps(message)

# Message to serialize the message by adding the appropriate amount
# of padding.
def serialize(message):
  i = 0
  padding = NOP
  while i < MESSAGE_SIZE:
    message.update({PADDING: padding * i})
    # Add padding to the message until it is MESSAGE_SIZE
    # number of bytes.
    if len(json.loads(message)) == MESSAGE_SIZE:
      return message
    i = i + 1

# Message to deserialize json to python dict object.
def deserialize(message):
  return json.loads(message)
