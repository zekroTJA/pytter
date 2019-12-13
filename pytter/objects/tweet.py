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

    def unretweet(self, do_not_raise: bool = False) -> object:
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

    def favorite(self) -> object:
        """
        Favorise (like) this Tweet.

        **Returns**

        - `Tweet`
          This Tweet object.
        """

        if not self._session:
            raise NoSessionException()

        return self._session.favorites_create(self.id or self.id_str,
            include_entities=True)

    def unfavorite(self) -> object:
        """
        Unfavorise (unlike) this Tweet.

        **Returns**

        - `Tweet`  
          This Tweet object.
        """

        if not self._session:
            raise NoSessionException()

        return self._session.favorites_destroy(self.id or self.id_str,
            include_entities=True)


    def reply(self, 
        text: str, 
        media: list = [],
        possibly_sensitive: bool = False,
        lat: float = None,
        long: float = None,
        place: [Place, int, str] = None,
        display_coordinates: bool = False) -> object:
        """
        Send a tweet as reply to the current tweet.
        The mentions of the recipients of the tweet are
        automatically populated from the origin tweet.

        **Parameters**

        - `text: str`  
          The text content of the tweet.

        - `media: list`  
          A list of media links which will be attached
          to the tweet. These can be a path to a local
          file, an URI to an online file which will be 
          downloaded or a already created FileInfo 
          object.
          *Default: `[]`*
        
        - `possibly_sensitive: bool`  
          Wether the tweet contains any sensitive content
          such as nudity or medical procedures.
          *Default: `False`*

        - `lat: float`  
          The latitude of the location where the tweet
          referes to. This must be a number between -90
          and 90 and will be ignored if `long` parameter
          is not passed.
          *Default: `None`*

        - `long: float`  
          The longitude of the location where the tweet
          referes to. THis must be a value between -180
          and 180 and will be ignored if `lat` parameter
          is not passed.
          *Default: `None`*

        - `place: [Place, str]`  
          A place the tweet referes to. This can be a place
          object or a place ID as string.
          *Default: `None`*

        - `display_coordinates: bool`  
          Wether or not to display coordinates in tweet.
          *Default: `False`*

        **Returns**

        - `Tweet`  
          The resulting Tweet object.
        """
        return self._session.statuses_update(
            status=text, 
            media=media,
            possibly_sensitive=possibly_sensitive,
            lat=lat,
            long=long,
            place=((place.id if type(place) == Place else place) if place else None),
            display_coordinates=display_coordinates,
            auto_populate_reply_metadata=True,
            in_reply_to_status_id=self.id)