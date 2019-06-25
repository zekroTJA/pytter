

class RateLimitException(Exception):
    MESSAGE = 'rate limit exceeded'
    def __init__(self):
        super().__init__(self.MESSAGE)

class NoneResponseException(Exception):
    MESSAGE = 'response was None'
    def __init__(self):
        super().__init__(self.MESSAGE)