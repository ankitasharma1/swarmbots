import constants

class Config():
    def __init__(self):   
        self.size = 3.0
        self.election_timeout = 20
        self.heartbeat_timeout = 5
        self.start_timeout = 100

        self.success = constants.SUCCESS
        self.fallback = constants.FALLBACK
