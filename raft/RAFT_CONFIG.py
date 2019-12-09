# cluster meta
CLUSTER_SIZE = 3

# state config
ELECTION_TIMEOUT = 7

# states
FOLLOWER = 'follower'
CANDIDATE = 'candidate'
LEADER = 'leader'

RAFT_DICT = {
    "S1": {
        "FOLLOWER_TIMEOUT": 2
    },
    "S2": {
        "FOLLOWER_TIMEOUT": 5
    },
    "S3": {
        "FOLLOWER_TIMEOUT": 8
    }
}
