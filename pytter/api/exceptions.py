class RateLimitException(Exception):
    _MESSAGE = 'rate limit exceeded'

    def __init__(self):
        super().__init__(self._MESSAGE)