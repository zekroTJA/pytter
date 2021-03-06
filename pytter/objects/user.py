from typing import List

class NoSessionException(Exception):
    MESSAGE = 'session is not set to tweet instance'
    def __init__(self):
        super().__init__(self.MESSAGE)

class UserStats:
    """
    Representing user statistics like follower count,
    following count, tweet cound and listed count.
    """

    def __init__(self, data: dict = {}, data_stats: dict = {}):
        self.followers_count    = data.get('followers_count') or data_stats.get('followers_count')
        self.following_count    = data.get('friends_count') or data_stats.get('following_count')
        self.tweet_count        = data.get('statuses_count') or data_stats.get('tweet_count')
        self.listed_count       = data.get('listed_count') or data_stats.get('listed_count')
        self.favorites_count   = data.get('favourites_count') or data_stats.get('favourites_count')

class User:
    """
    User object.
    Reference: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/user-object
    """

    def __init__(self, data: dict = {}, session = None):
        self._session = session

        self.id                 = data.get('id')
        self.id_str             = data.get('id_str') or str(self.id)
        self.name               = data.get('name')
        self.screen_name        = data.get('screen_name')
        self.location           = data.get('location')
        self.url                = data.get('url')
        self.description        = data.get('description')
        self.protected          = data.get('protected')
        self.verified           = data.get('verified')
        self.created_at         = data.get('created_at')
        self.username           = data.get('username') or data.get('screen_name')
        self.profile_image_url  = data.get('profile_image_url_https') or data.get('profile_image_url')
        self.profile_banner_url = data.get('profile_banner_url')
        self.stats              = UserStats(data=data, data_stats=data.get('stats') or {})

    def followers_ids(self) -> List[str]:
        """
        Returns a list of all IDs of the
        users following this user.

        **Returns**

        - `List[str]`  
          User IDs of following users.
        """

        return self._session.followers_ids(self.id or self.id_str)

    def followers(self, skip_status: bool = True, include_user_entities: bool = True) -> List[object]:
        """
        Returns a list of all User objets
        of the users follwoing this user.

        **Returns**

        - `List[User]`  
          User objects of following users.
        """

        return self._session.followers_list(self.id or self.id_str,
            skip_status=skip_status, include_user_entities=include_user_entities)

    def following_ids(self) -> List[str]:
        """
        Returns a list of all IDs of the
        friends of this user (users this 
        user is currently following).

        **Returns**

        - `List[str]`  
          List of friends user IDs.
        """

        return self._session.friends_ids(self.id or self.id_str)

    def following(self, skip_status: bool = True, include_user_entities: bool = True) -> List[object]:
        """
        Returns a list of all User objects of 
        the friends of this user (users this 
        user is currently following).

        **Returns**

        - `List[User]`  
          List of friends User objects.
        """

        return self._session.friends_list(self.id or self.id_str,
            skip_status=skip_status, include_user_entities=include_user_entities)