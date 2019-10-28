CLUSTER_INITIATOR_CMDS = 3
JOINING_CLUSTER_CMDS = 5

DATA_SIZE = 1024

# Initially in this state. Either join the cluster or start the cluster and wait for other nodes to join.
JOIN = 1 
FOLLOWER = 2
CANDIDATE = 3
LEADER = 4

SUCCESS = 1
FALLBACK = 2

IGNORE = -1
