

class RateLimitException(Exception):
    MESSAGE = 'rate limit exceeded'
    def __init__(self):
        super().__init__(self.MESSAGE)

class NoneResponseException(Exception):
    MESSAGE = 'response was None'
    def __init__(self):
        super().__init__(self.MESSAGE)

class ParameterOutOfBoundsException(Exception):
    MESSAGE = 'parameter out of bounds'
    def __init__(self, additional_description: str = None):
        if additional_description:
            self.MESSAGE += ': {}'.format(additional_description)
        super().__init__(self.MESSAGE)

class ParameterNoneException(Exception):
    MESSAGE = 'none parameters given'
    def __init__(self, additional_description: str = None):
        if additional_description:
            self.MESSAGE += ': {}'.format(additional_description)
        super().__init__(self.MESSAGE)