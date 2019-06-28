from .media import Media
from .user import User
from .geo import Coordinates, Place


class NoSessionException(Exception):
    MESSAGE = 'session is not set to tweet instance'
    def __init__(self):
        super().__init__(self.MESSAGE)

class TweetEntities:
    """
    Collection of tweet entities like a list of hashtags, attached media
    and mentioned users.
    Reference: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object
    """

    def __init__(self, data: dict = {}, data_extended: dict = {}):
        if not data or not data_extended:
            return None
        self.hashtags       = [h.get('text') for h in data.get('hashtags')] if 'hashtags' in data else []
        self.media          = [Media(d) for d in data.get('media')] if 'media' in data_extended else []
        self.user_mentions  = [User(u) for u in data.get('user_mentions')] if 'user_mentions' in data else []

class Tweet:
    """
    Tweet object.
    Reference: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object
    """

    def __init__(self, data: dict = {}, session = None):
        if not data:
            return None

        self._session = session

        self.created_at     = data.get('created_at')
        self.id             = data.get('id')
        self.id_str         = data.get('id_str') or str(self.id)
        self.text           = data.get('text')
        self.source         = data.get('source')
        self.trucated       = data.get('truncated')
        
        self.in_reply_to_status_id      = data.get('in_reply_to_status_id')
        self.in_reply_to_status_id_str  = data.get('in_reply_to_status_id_str')
        self.in_reply_to_user_id_str    = data.get('in_reply_to_user_id_str')
        self.in_reply_to_screen_name    = data.get('in_reply_to_screen_name')

        self.user = User(data.get('user')) if 'user' in data else None

        self.coordinates    = Coordinates(data.get('coordinates')) if 'coordinates' in data else None
        self.place          = Place(data.get('place')) if 'place' in data else None

        self.is_quote_status        = data.get('contributors')
        self.quoted_status_id       = data.get('quoted_status_id')
        self.quoted_status_id_str   = data.get('quoted_status_id_str')
        self.quote_status           = Tweet(data.get('quote_status')) if 'quote_status' in data else None
        self.retweeted_status       = Tweet(data.get('retweeted_status')) if 'retweeted_status' in data else None

        self.contributors       = data.get('contributors')
        self.retweet_count      = data.get('retweet_count')
        self.quote_count        = data.get('quote_count')
        self.favorite_count     = data.get('favorite_count')
        self.possibly_sensitive = data.get('possibly_sensitive')
        self.lang               = data.get('lang')

        self.urls       = data.get('urls')
        self.entities   = TweetEntities(data=data.get('entities'), data_extended=data.get('extended_entities'))
        
        self.favorited  = data.get('favorited')
        self.favorited  = data.get('retweeted')

    def delete(self) -> object:
        """
        Delete this tweet.

        **Returns**

        - `Tweet`  
          This Tweet object.
        """
        if not self._session:
            raise NoSessionException()
        return self._session.statuses_destroy(self.id or self.id_str)

    def retweet(self) -> object:
        """
        Retweet this tweet.

        **Returns**

        - `Tweet`  
          This Tweet object containing
          retweet information.
        """
        
        if not self._session:
            raise NoSessionException()

        return self._session.statuses_retweet(self.id or self.id_str)

    def un_retweet(self, do_not_raise: bool = False) -> object:
        """
        Revoke this retweet.

        **Parameters**

        - `do_not_raise: bool`  
          Do not raise an exception if the tweet is
          not a retweet and can not be revoked.

        **Returns**

        - `Tweet`  
          This Tweet object.
        """

        if not self._session:
            raise NoSessionException()

        if not self.retweeted_status:
            if do_not_raise:
                return None
            raise Exception('a non-retweet can not be revoked')

        return self._session.statuses_unretweet(self.id or self.id_str)

    def retweets(self, count: int = None) -> list:
        """
        Retruns a list of up to 100 retweets of
        this tweet.

        **Parameters**

        - `count: int`  
          The ammount of retweets to be collected
          (in range of [1, 100]).  
          *Default`: `None`*

        **Returns**  
        
        - `list`  
          List of Tweet objects representing the
          retweets details.
        """

        if not self._session:
            raise NoSessionException()
        
        return self._session.statuses_retweets(self.id or self.id_str, count=count)