import constants

class Config():
    def __init__(self):   
        self.size = 3.0
        self.election_timeout = 5
        self.heartbeat_timeout = 3
        self.start_timeout = 1

        self.success = constants.SUCCESS
        self.fallback = constants.FALLBACK
