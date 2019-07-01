from typing import NamedTuple
from requests_oauthlib import OAuth1
from typing import Dict, List

from ..utils import utils
from ..api import APISession, Credentials
from ..objects import Tweet, Place, User


class Client:
    """
    Simple and easy to use API client which wraps
    around APISession.

    **Parameters**

    - `credentials : Credentials`  
      Twitter APP or user credentials object.
    """

    #################
    # GENERAL FUNCS #
    #################

    def __init__(self, credentials: Credentials):
        self._session = APISession(credentials)

    def session(self) -> APISession:
        """
        Returns the clients APISession
        instance.

        **Returns**

        - `APISession`  
          Initialized APISession instance.
        """
        
        return self._session

    ############
    # STATUSES #
    ############

    def status_update(self, 
        text: str, 
        media: list = [],
        possibly_sensitive: bool = False,
        lat: float = None,
        long: float = None,
        place: [Place, int, str] = None,
        display_coordinates: bool = False) -> Tweet:
        """
        Send a tweet.

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
            display_coordinates=display_coordinates)

    def status_delete(self, tweet_id: [str, int]) -> Tweet:
        """
        Delete a tweet by its ID.

        **Parameters**

        - `tweet_id: [str, int]`  
          The ID of the tweet as string or integer.

        **Returns**

        - `Tweet`  
          The tweet object of the deleted tweet.
        """
        
        return self._session.statuses_destroy(tweet_id)

    def status_retweet(self, tweet_id: [str, int]) -> Tweet:
        """
        Retweet a tweet by its ID.

        **Parameters**

        - `tweet_id: [str, int]`  
          ID of the Tweet to retweet.

        **Returns**

        - `Tweet`  
          The resulting Tweet containing 
          retweet information.
        """

        return self._session.statuses_retweet(id=tweet_id)

    def status_unretweet(self, tweet_id: [str, int]) -> Tweet:
        """
        Revoke a retweet by its ID.

        **Parameters**

        - `tweet_id: [str, int]`  
          The retweet ID to be revoked.

        **Returns**

        - `Tweet`  
          The Tweet object of the revoked retweet.
        """

        return self._session.statuses_unretweet(id=tweet_id)

    def status(self, tweet_id: [str, int],
        include_entities: bool = True,
        include_ext_alt_text: bool = True) -> Tweet:
        """
        Get Tweet by its ID. If there was no Tweet
        found by this ID, the result will be None.

        **Parameters**

        - `tweet_id: [str, int]`  
          ID of the Tweet to be fetched.

        - `include_entities: bool`  
          Include Tweet entities.
          *Default: `True`*

        - `include_ext_alt_text: bool`  
          Include Tweets alt text, if set.
          *Default: `True`*

        **Returns**

        - `Tweet`  
          Resulting Tweet or `None`.
        """

        return self._session.statuses_show(id=tweet_id,
            include_entities=include_entities,
            include_ext_alt_text=include_ext_alt_text)

    def statuses(self, tweet_ids: list, 
        include_entities: bool = True,
        include_ext_alt_text: bool = True,
        raise_on_none = False) -> Dict[str, Tweet]:
        """
        Gets up to 100 tweets by their IDs.The result will be
        a dictionary with keys representing the originally
        requested Tweet ID paired with the fetched Tweet
        object, if found. Else, the value will be `None`.

        **Parameters**
        
        - `tweet_ids: list`  
          List of Tweet IDs to be fetched.
        
        - `include_entities: bool`  
          Include Tweets entity objects.
          Default: True
        
        - `include_ext_alt_text: bool`  
          Include Tweets alt texts, if set.
          Default: True
        
        - `raise_on_none: bool`  
          If this is set to `True`, an `NoneResponseException`
          will be risen if one of the Tweets is `None` (not found,
          not existent or not accessable).

        **Returns**

        - `Dict[[str, int], Tweet]`  
          Tweet IDs as keys paired with the corresponding
          result Tweet object, which can be `None`.
        """

        return self._session.statuses_lookup(
            ids=tweet_ids,
            raise_on_none=raise_on_none,
            include_entities=include_entities,
            include_ext_alt_text=include_ext_alt_text)

    def status_retweets(self, tweet_id: [str, int], count: int = None) -> List[Tweet]:
        """
        Returns a list of up to 100 retweet objects
        of the passed tweet.

        - `id: [str, int]`  
          The ID of the Tweet to get the list of
          retweets from.

        - `count: int`  
          The ammount of retweets to be collected
          (in range of [1, 100]).  
          *Default`: `None`*

        **Returns**  
        
        - `List[Tweet]`  
          List of Tweet objects representing the
          retweets details.
        """

        return self._session.statuses_retweets(id=tweet_id, count=count)

    #########
    # USERS #
    #########

    def user(self, 
        id: [str, int] = None, 
        screen_name: str = None,
        include_entities: bool = True) -> User:
        """
        Get a user Object by its ID or screen name (Twitter handle).
        At least one of both, ID or screen name, must be delivered.

        **Parameters**

        - `id: [str, int]`  
          ID of the desired user.  
          *Default: `None`*

        - `screen_name: str`  
          User name (Twitter handle) of the desired user.  
          *Default: `None`*

        - `include_entities: bool`  
          Include entities node that may appear within
          embedded statuses.  
          *Default: `True`*

        **Returns**

        - `User`  
          Resulting User object.
        """

        return self._session.users_show(
            id=id, 
            screen_name=screen_name,
            include_entities=include_entities)

    def users(self, 
        ids: List[str] = None, 
        screen_names: List[str] = None,
        include_entities: bool = True) -> Dict[str, User]:
        """
        Get a list of up to 100 users specified by their
        IDs OR screen names (Twitter handles). Neither
        the list of IDs as same as the list of screen
        names must not be empty.
        IDs and screen names can no be mixed. Screen names
        value list will be prefered.

        **Parameters**

        - `ids: List[str]`  
          List of IDs of desired users.  
          *Default: `None`*

        - `screen_names: List[str]`  
          List of screen names (Twitter handles) of the
          desired users.  
          *Default: `None`*

        - `include_entities: bool`  
          Include entities node that may appear within
          embedded statuses.  
          *Default: `True`*

        **Returns**

        - `Dict[str, User]`  
          A dict of user IDs and user names as keys
          linked to the corresponding user objects.
          So, for each user, there are two values in
          the dict. Firstly linked to an ID key and 
          secondly linked to the users user name as 
          key.
        """

        return self._session.users_lookup(
            ids=ids,
            screen_names=screen_names,
            include_entities=include_entities)

    ###########
    # ALIASES #
    ###########

    def tweet(self, **kwargs) -> Tweet:
        """
        Alias for Client#status.
        """

        return self.status(**kwargs)

    def tweets(self, **kwargs) -> Dict[str, Tweet]:
        """
        Alias for Client#statuses.
        """

        return self.statuses(**kwargs)