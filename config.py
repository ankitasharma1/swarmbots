import constants

class Config():
    def __init__(self):   
        self.size = 3
        self.election_timeout = 150/1000
        self.heartbeat_timeout = 150/1000
        self.start_timeout = 100/1000

        self.success = constants.SUCCESS
        self.fallback = constants.FALLBACK
