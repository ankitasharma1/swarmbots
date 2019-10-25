import constants
import json
import ruamel.yaml as yaml

# Message Type
TYPE = "type"
JOIN = "join"
START = "start"

# Params for JOIN
ID = "id"
IP = "ip"
PORT = "port"

# Params for START
CLUSTER_INFO = "cluster_info"

#--------------------------------------------#

# When joining the cluster, the node sends its id, ip address
# and port number.
def joinMessage(id, ip, port):
    message = {TYPE: JOIN, 
               ID: id,
               IP: ip, PORT: port}
    return json.dumps(message)

# When all nodes have connected to the cluster, send a message
# with all of the contact details for the other  nodes so that 
# every node knows the other node's existence.
def startMessage(id, clusterInfo):
    message = {TYPE: START,
        ID: id,
        CLUSTER_INFO: clusterInfo
    }
    return json.dumps(message)

# Message to deserialize json to python dict object.
def deserialize(message):
    return yaml.safe_load(message)