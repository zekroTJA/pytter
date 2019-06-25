from typing import NamedTuple
from requests_oauthlib import OAuth1

from ..utils import utils
from ..api import APISession, Credentials
from ..objects import Tweet, Place


class Client:
    """
    Client wraps API requests to the
    Twitter API.

    Parameters
    ==========

    credentials : Credentials
        Twitter APP or user credentials object.
    """

    def __init__(self, credentials: Credentials):
        self._session = APISession(credentials)

    def update(self, 
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

        return self._session.update(
            status=text, 
            media=media,
            possibly_sensitive=possibly_sensitive,
            lat=lat,
            long=long,
            place=((place.id if type(place) == Place else place) if place else None),
            display_coordinates=display_coordinates)

    def delete(self, tweet_id: [str, int]) -> Tweet:
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
        
        return self._session.destroy(tweet_id)