from requests_oauthlib import OAuth1


class Credentials:
    """
    TwitterCedentials contains the consumer_key
    and the comsumer_secret for creating an
    access token.
    
    **Parameters**

    - `consumer_key: str`  
      The App consumer API key.

    - `consumer_secret: str`  
      The App consumer API secret key.

    - `access_token_key: str`  
      The App access token key.

    - `access_token_secret: str`  
      The App access token secret.
    """
    
    consumer_key: str        = None
    consumer_secret: str     = None
    access_token_key: str    = None
    access_token_secret: str = None

    def __init__(self, consumer_key: str, consumer_secret: str, access_token_key: str, access_token_secret: str):
        if consumer_key is None:
            raise Exception('consumer_key was None')
        if consumer_secret is None:
            raise Exception('consumer_secret was None')
        if access_token_key is None:
            raise Exception('access_token_key was None')
        if access_token_secret is None:
            raise Exception('access_token_secret was None')
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret

    def to_oauth1(self) -> OAuth1:
        return OAuth1(self.consumer_key, self.consumer_secret,
            self.access_token_key, self.access_token_secret)