# cluster meta
CLUSTER_SIZE = 3

# state config
ELECTION_TIMEOUT = 5

# states
FOLLOWER = 'follower'
CANDIDATE = 'candidate'
LEADER = 'leader'

RAFT_DICT = {
    "S1": {
        "FOLLOWER_TIMEOUT": 1
    },
    "S2": {
        "FOLLOWER_TIMEOUT": 3
    },
    "S3": {
        "FOLLOWER_TIMEOUT": 6
    }
}
