from typing import NamedTuple
from requests_oauthlib import OAuth1

from ..utils import utils
from ..api import APISession, Credentials
from ..objects import Tweet, Place


class Client:
    """
    Simple and easy to use API client which wraps
    around APISession.

    Parameters
    ==========

    credentials : Credentials
        Twitter APP or user credentials object.
    """

    def __init__(self, credentials: Credentials):
        self._session = APISession(credentials)

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

        Parameters
        ==========

        text: str
            The text content of the tweet.

        media: list
            A list of media links which will be attached
            to the tweet. These can be a path to a local
            file, an URI to an online file which will be 
            downloaded or a already created FileInfo 
            object.
            Default: []
        
        possibly_sensitive: bool
            Wether the tweet contains any sensitive content
            such as nudity or medical procedures.
            Default: False

        lat: float
            The latitude of the location where the tweet
            referes to. This must be a number between -90
            and 90 and will be ignored if `long` parameter
            is not passed.
            Default: None

        long: float
            The longitude of the location where the tweet
            referes to. THis must be a value between -180
            and 180 and will be ignored if `lat` parameter
            is not passed.
            Default: None

        place: [Place, str]
            A place the tweet referes to. This can be a place
            object or a place ID as string.
            Default: None

        display_coordinates: bool
            Wether or not to display coordinates in tweet.
            Default: False
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

        Parameters
        ==========

        tweet_id: [str, int]
            The ID of the tweet as string or integer.

        Returns
        =======

        Tweet
            The tweet object of the deleted tweet.
        """
        
        return self._session.statuses_destroy(tweet_id)

    def status(self, tweet_id: [str, int],
        include_entities: bool = True,
        include_ext_alt_text: bool = True) -> Tweet:
        """
        Get Tweet by its ID. If there was no Tweet
        found by this ID, the result will be None.

        Parameters
        ==========

        tweet_id: [str, int]
            ID of the Tweet to be fetched.

        include_entities: bool
            Include Tweet entity objects.
            Default: True

        include_ext_alt_text: bool
            Include Tweets alt text, if set.
            Default: True

        Returns
        =======

        Tweet
            Resulting Tweet or `None`.
        """

        return self._session.statuses_show(id=tweet_id,
            include_entities=include_entities,
            include_ext_alt_text=include_ext_alt_text)

    def statuses(self, tweet_ids: list, 
        include_entities: bool = True,
        include_ext_alt_text: bool = True,
        raise_on_none = False) -> dict:
        """
        Gets up to 100 tweets by their IDs.The result will be
        a dictionary with keys representing the originally
        requested Tweet ID paired with the fetched Tweet
        object, if found. Else, the value will be `None`.

        Parameters
        ==========
        
        tweet_ids: list
            List of Tweet IDs to be fetched.
        
        include_entities: bool
            Include Tweets entity objects.
            Default: True
        
        include_ext_alt_text: bool
            Include Tweets alt texts, if set.
            Default: True
        
        raise_on_none: bool
            If this is set to `True`, an `NoneResponseException`
            will be risen if one of the Tweets is `None` (not found,
            not existent or not accessable).

        Returns
        =======

        dict
            Tweet IDs as keys paired with the corresponding
            result Tweet object, which can be `None`.
        """

        return self._session.statuses_lookup(
            ids=tweet_ids,
            raise_on_none=raise_on_none,
            include_entities=include_entities,
            include_ext_alt_text=include_ext_alt_text)

    ###########
    # ALIASES #
    ###########

    def tweet(self, **kwargs) -> Tweet:
        """
        Alias for Client#status.
        """

        return self.status(**kwargs)

    def tweets(self, **kwargs) -> dict:
        """
        Alias for Client#statuses.
        """

        return self.statuses(**kwargs)