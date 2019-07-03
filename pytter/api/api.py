import uuid
import base64
import urllib
import requests
from typing import Iterator, List, Dict
from requests_oauthlib import OAuth2

from .credentials import Credentials
from .exceptions import (
    RateLimitException, NoneResponseException, 
    ParameterOutOfBoundsException,
    ParameterNoneException
)

from ..utils import utils
from ..objects import Tweet, Media, User
from ..utils import FileInfo


class APISession:
    """
    Barebone Twitter API wrapper representing Twitters API
    endpoints directly. Initialized with App Credentials
    for authentication and authorization.

    **Parameters**

    - `credentials: Credentials`  
      APP or User credentials to authenticate against
      the Twitter API.
    """

    API_ROOT_URI        = 'https://api.twitter.com'
    API_VERSION         = '1.1'
    API_UPLOAD_ROOT_URI = 'https://upload.twitter.com/1.1'
    UPLOAD_CHUNK_SIZE   = 1024 * 1024 * 1024 # 1 MiB

    def __init__(self, credentials: Credentials):
        self._session = requests.Session()
        
        self._credentials = credentials
        
        self._session = requests.Session()

        if all([self._credentials.access_token_key,
                self._credentials.access_token_secret,
                self._credentials.consumer_key,
                self._credentials.consumer_secret]):
            self._oauth = self._credentials.to_oauth1()
        else:
            self.obtain_user_context_token()

    ############################
    # GENERAL REQUEST HANDLING #
    ############################

    def request(self, method: str, resource_path: str, **kwargs) -> object:
        """
        Request the Twitter API with the defined authentication
        credentials.
        This method raises an exception on failed authentication or request.

        **Parameters**

        - `method : str`  
          Request method.

        - `resource_path : str`  
          Path to the requested resource (without root URI).
          Leading '/' will be cut off.

        - `**kwargs`  
          Optional arguments passed to request.request()

        **Returns**
        
        - `Object`  
          JSON-parsed response body.
        """

        res = self._session.request(
            auth=self._oauth,
            method=method,
            url='{0}/{1}/{2}'.format(self.API_ROOT_URI, self.API_VERSION,
                (resource_path[1:] if resource_path.startswith('/') else resource_path)),
            **kwargs)

        if res.status_code == 429:
            raise RateLimitException()

        if not res.ok:
            raise Exception('request failed with status code {} and message: {}'
                .format(res.status_code, res.text))

        return res.json()

    def obtain_user_context_token(self):
        """
        Collect a user context bearer token
        from client_key and client_secret and sets it as OAuth2 
        authentication method for further requests.
        """

        key = urllib.parse.quote_plus(self._credentials.consumer_key)
        secret = urllib.parse.quote_plus(self._credentials.consumer_secret)
        basic_token = base64.b64encode(
            '{0}:{1}'.format(key, secret).encode('utf8')).decode('utf8')
        
        res = self._session.post(
            url='{0}/oauth2/token'.format(self.API_ROOT_URI),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'Authorization': 'Basic {0}'.format(basic_token),
            },
            data={
                'grant_type': 'client_credentials',
            })

        if res.status_code == 429:
            raise RateLimitException()
        if res.status_code != 200:
            raise Exception('request failed with status code {0}'.format(res.status_code))

        body = res.json()

        self._oauth = OAuth2(token=body)

    ##############
    # UPLOAD API #
    ##############

    def upload_media_request(self, command=None, params={}, raw=None, **kwargs) -> object:
        """
        Wrap a request to initiate, append or finalize a chunked media upload.

        **Parameters**

        - `command : str`  
          Must be 'INIT', 'APPEND' or 'FINALIZE'.
          If 'raw' is set, this must not be passed.

        - `params : dict`  
          Request body parameters.
          If 'raw' is set, this must not be passed.

        - `raw`  
          Raw data used as reuqest body. 
          This option overwrites 'command' and 'params'.

        - `**kwargs:`  
          Additional arguments which will be passed to
          the request method.

        **Returns**

        - `object`  
          Resulting FINALIZE response object.
        """

        if raw is None:
            params['command'] = command
            params = utils.sort_dict_alphabetically(params)

        res = self._session.post(
            auth=self._oauth,
            url='{0}/media/upload.json'.format(self.API_UPLOAD_ROOT_URI),
            data=(params if raw is None else raw),
            **kwargs)

        if res.status_code == 429:
            raise RateLimitException()
        if res.status_code < 200 or res.status_code >= 300:
            raise Exception('request failed with status code {0}'.format(res.status_code))

        return res

    def upload_file_cunked(self, file_info: utils.FileInfo, close_after: bool = False) -> Media:
        """
        Try to grab the FileInfo of the specified media file, checks if it 
        can be uploaded to twitter and then tries to upload the file via 
        the chunked twitter media upload endpoint.

        **Parameters**

        - `media : str`  
          Either a local file location or a HTTP(S) URL
          to an online file resource.

        - `close_after: bool`  
          Wether the file info reader should be closed
          after upload or not.
          *Default: `False`*

        **Returns**

        - `Media`  
          Result media object.
        """

        # --- INIT ------------------------------------------------------------
        res = self.upload_media_request(
            command='INIT',
            params={
                'total_bytes': file_info.size,
                'media_type': file_info.mime_type,
            })
        
        res_data = res.json()
        if 'media_id_string' not in res_data:
            raise Exception('"media_id_string" not contained in response body')
        media_id = res_data['media_id']

        # --- APPEND ----------------------------------------------------------
        boundary_uuid = uuid.uuid4().hex
        boundary = '--{0}'.format(boundary_uuid).encode('utf8')
        for chunk in utils.chunk_file(file_info, self.UPLOAD_CHUNK_SIZE):
            body_data = (
                # COMMAND
                boundary,
                b'Content-Disposition: form-data; name="command"',
                b'',
                b'APPEND',
                # MEDIA_ID
                boundary,
                b'Content-Disposition: form-data; name="media_id"',
                b'',
                str(media_id).encode('utf8'),
                # MEDIA
                boundary,
                'Content-Disposition: form-data; name="media"; filename="{0!r}"'
                    .format(file_info.file_name).encode('utf8'),
                b'Content-Type: application/octet-stream',
                b'',
                chunk.data,
                # SEGMENT_INDEX
                boundary,
                b'Content-Disposition: form-data; name="segment_index"',
                b'',
                str(chunk.index).encode('utf8'),
                boundary + b'--'
            )
            body = b'\r\n'.join(body_data)

            self.upload_media_request(
                headers={ 
                    'Content-Type': 'multipart/form-data; boundary={0}'
                        .format(boundary_uuid), 
                    'Content-Length': str(len(body)),
                },
                raw=body)

        # --- FINALIZE --------------------------------------------------------
        res = self.upload_media_request(
            command='FINALIZE',
            params={
                'media_id': str(media_id),
            })

        if close_after:
            file_info.close()

        if res == None:
            raise NoneResponseException()

        return Media(res.json())

    def upload_attachments(self, media: list, close_after: bool = False) -> Iterator[Media]:
        """
        Upload a list of media using chunked upload.
        The list of media can only contain either 4 photos,
        1 gif or 1 video. Everything else will raise an
        exception.

        **Parameters**

        - `media: list`  
          List of media objects as path to a local file,
          as URI to an online file which will be downloaded
          and atatched then or an existing FileInfo object.
        
        - `close_after: bool`  
          Wether to close each opened file handler after
          uploading or not.
          *Default: `False`*

        **Returns**

        - `Iterator[Media]`  
          Iterator of uploaded Media objects.
        """

        max_attachable = None
        files = []

        for m in media:
            file_info = m if type(m) == FileInfo else utils.try_get_file(m)
            i = utils.check_upload_compatibility(file_info)
            files.append(file_info)
            if not max_attachable:
                max_attachable = i

        if max_attachable and max_attachable > len(media):
            raise Exception('you can only attach up to {} files using this attachment type.'
                .format(max_attachable))

        for f in files:
            yield self.upload_file_cunked(f, close_after=close_after)

    ################
    # STATUSES API #
    ################

    def statuses_update(self, status: str, media: [list, str] = None, **kwargs) -> Tweet:
        """
        Create a Tweet with specified content.

        **Parameters**

        - `status : str`  
          The status text. This can not be None, but empty ('')
          if you do not want to have text content in your tweet.

        - `img : str`  
          Image media identifier.
          This can be either a local file location or an
          online file linked by a HHTP(S) URL.

        - `**kwargs`  
          Additional keyword arguments which will be directly
          passed to the request arguments.
          You should only use valid arguments supported by the
          POST statuses/update endpoint:
          https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-statuses-update

        **Returns**

        - `Tweet`  
          The result Tweet object.
        """

        data = kwargs
        data['status'] = status

        if media is not None:
            if type(media) is not list:
                media = [media]

            media_objs = []

            for media_obj in self.upload_attachments(media):
                media_objs.append(media_obj)

            data['media_ids'] = ','.join([m.id_str for m in media_objs])
        
        res = self.request('POST', 'statuses/update.json', data=data)
        if not res:
            raise NoneResponseException()

        return Tweet(res, self)

    def statuses_destroy(self, id: [str, int], **kwargs) -> Tweet:
        """
        Delete a tweet.

        **Parameters**

        - `id: [str, int]`  
          ID of the tweet to delete.

        - `**kwargs:`  
          Additional agruments passed directly to the 
          request parameters.

        **Returns**

        - `Tweet`  
          The tweet ofbject which was deleted.
        """
        
        data = kwargs

        res = self.request('POST', 'statuses/destroy/{}.json'.format(id), data=data)
        if not res:
            raise NoneResponseException()

        return Tweet(res)

    def statuses_show(self, id: [str, int], **kwargs) -> Tweet:
        """
        Fetches a single tweet by its ID. The tweets author
        user object will be in the response Tweet object.
        If there was no tweet found by the specified ID, the
        result will be `None`.

        **Parameters**

        - `id: [str, int]`  
          ID of the Tweet.

        - `**kwargs:`  
          Additional agruments passed directly to the 
          request parameters.

        **Returns**

        - `Tweet`  
          Result Tweet obect or `None`.
        """

        data = kwargs

        data['id'] = id

        res = self.request('GET', 'statuses/show.json', params=data)
        if not res:
            raise NoneResponseException()
        
        return Tweet(res, self)

    def statuses_lookup(self, ids: List[str], raise_on_none: bool = False, **kwargs) -> Dict[str, Tweet]:
        """
        Get details about up to 100 tweets. The returned
        dictionary keys represent the original requested
        IDs of the Tweets and are paired with the 
        corresponding Tweet object, if found. Defaultly,
        the value can be `None` if no Tweet was found
        matching the given ID.

        **Parameters**

        - `ids: list`  
          List of tweet IDs to be fetched.

        - `raise_on_none: boolean`  
          Raise an `NoneResponseException` exception if
          a Tweet could not be fetched for a given ID.

        - `**kwargs:`  
          Additional agruments passed directly to the 
          request parameters.

        **Returns**

        - `Dict[[int, str], Tweet]`  
          Tweet IDs as keys paired with the corresponding
          result Tweet object, which can be `None`.
        """

        ln = len(ids)
        if ln < 1 or ln > 100:
            raise ParameterOutOfBoundsException('index must be in range [1, 100]')

        data = kwargs

        data['id'] = ','.join([str(id) for id in ids])
        data['map'] = True

        res = self.request('GET', 'statuses/lookup.json', params=data)
    
        if not res or 'id' not in res:
            raise NoneResponseException()

        tweets = {}

        for tid, obj in res.get('id').items():
            if not obj and raise_on_none:
                raise NoneResponseException()
            tweets[tid] = Tweet(obj, self) if obj else None

        return tweets

    def statuses_retweet(self, id: [str, int], **kwargs) -> Tweet:
        """
        Retweet a Tweet by its ID.

        **Parameters**

        - `id: [str, int]`  
          ID of the Tweet to retweet.

        - `**kwargs:`  
          Additional agruments passed directly to the 
          request parameters.

        **Returns**

        - `Tweet`  
          Resulting Tweet object containing retweet 
          data information.
        """

        data = kwargs
        
        res = self.request('POST', 'statuses/retweet/{}.json'.format(id), params=data)
        if not res:
            return NoneResponseException()

        return Tweet(res, self)

    def statuses_unretweet(self, id: [str, int], **kwargs) -> Tweet:
        """
        Revoke a retweet by its ID.

        **Parameters**

        - `id: [str, int]`  
          ID of the Tweet to unretweet.

        - `**kwargs:`  
          Additional agruments passed directly to the 
          request parameters.

        **Returns**

        - `Tweet`  
          Tweet object of the revoked retweet.
        """

        data = kwargs

        res = self.request('POST', 'statuses/unretweet/{}.json'.format(id), params=data)
        if not res:
            return NoneResponseException()

        return Tweet(res)

    def statuses_retweets(self, id: [str, int], count: int = None, **kwargs) -> List[Tweet]:
        """
        Returns a list of up to 100 of the most recent 
        retweets of the specified Tweet by ID.

        **Parameters**

        - `id: [str, int]`  
          The ID of the Tweet to get the list of
          retweets from.

        - `count: int`  
          The ammount of retweets to be collected
          (in range of [1, 100]).  
          *Default`: `None`*

        - `**kwargs:`  
          Additional agruments passed directly to the 
          request parameters.

        **Returns**  
        
        - `List[Tweet]`  
          List of Tweet objects representing the
          retweets details.
        """

        data = kwargs

        if count:
            if count < 1 or count > 100:
                raise ParameterOutOfBoundsException('count must be in range of [1, 100]')
            data['count'] = count

        res = self.request('GET', 'statuses/retweets/{}.json'.format(id), params=data)
        if not res:
            raise NoneResponseException()

        return [Tweet(r, self) for r in res]

    def statuses_retweets_of_me(self, 
        count: int = None,
        since_id: [int, str] = None,
        max_id: [int, str] = None,
        include_entities: bool = True,
        include_user_entities: bool = True,
        **kwargs) -> List[Tweet]:
        """
        Returns the most recent retweets of tweets authored
        by the authenticated user. This is a subset of the
        user timeline.

        **Parameters**

        - `count: int`  
          Number of records to be retrieved in range of
          [1, 100]. If omitted, 20 will be assumed.  
          *Default: `None`*

        - `since_id: [int, str]`  
          Results only after the given tweet ID (which
          means more recent then the given tweet)  
          *Default: `None`*

        - `max_id: [int, str]`  
          Retuned results will be less than or equal 
          the given tweet ID.  
          *Default: `None`*

        - `include_entities: bool`  
          Include tweet entities in result objects.  
          *Default: `True`*
             
        - `include_user_entities: bool`  
          Include user objects in result objects.  
          *Default: `True`*

        - `**kwargs:`  
          Additional agruments passed directly to the 
          request parameters.

        **Returns**

        - `List[Tweet]`  
          Result list of Tweet objects.
        """

        data = kwargs

        data['include_entities'] = include_entities
        data['include_user_entities'] = include_user_entities

        if count:
            if count < 1 or count > 100:
                raise ParameterOutOfBoundsException('count must be in range of [1, 100]')
            data['count'] = count

        if since_id:
            data['since_id'] = since_id

        if max_id:
            data['max_id'] = max_id

        res = self.request('GET', 'statuses/retweets_of_mine', params=data)
        if not res:
            raise NoneResponseException()

        return [Tweet(r, self) for r in res]

    #################
    # FAVORITES API #
    #################

    def favorites_create(self, id: [str, int], **kwargs) -> Tweet:
        """
        Favorite (like) a Tweet by its specified ID.

        **Parameters**

        - `id: [str, int]`  
          The ID of the desired Tweet to favorite/like.

        - `**kwargs:`  
          Additional agruments passed directly to the 
          request parameters.

        **Returns**

        - `Tweet`  
          The favorized/liked Tweets object.
        """

        data = kwargs
        data['id'] = id
        
        res = self.request('POST', 'favorites/create.json', data=data)
        if not res:
            raise NoneResponseException()

        return Tweet(res, self)

    def favorites_destroy(self, id: [str, int], **kwargs) -> Tweet:
        """
        Unfavorite (unlike) a liked Tweet by its specified ID.

        **Parameters**

        - `id: [str, int]`  
          The ID of the desired liked tweet to 
          unfavorite/unlike.

        - `**kwargs:`  
          Additional agruments passed directly to the 
          request parameters.

        **Returns**

        - `Tweet`  
          The unfavorized/unliked Tweet object.
        """

        data = kwargs
        data['id'] = id

        res = self.request('POST', 'favorited/destroy.json', data=data)
        if not res:
            raise NoneResponseException()

        return Tweet(res, self)

    #############
    # USERS API #
    #############

    def users_show(self, id: [str, int] = None, screen_name: str = None, **kwargs) -> User:
        """
        Fetches a single user by its ID or screen name
        (Twitter handle).

        **Parameters**

        - `id: [str, int]`  
          ID of the desired user.  
          *Default: `None`*

        - `screen_name: str`  
          Screen name (handle) of the
          desired user.  
          *Default: `None`*

        - `**kwargs:`  
          Additional agruments passed directly to the 
          request parameters.

        **Returns**

        - `User`  
          Fetched user object.
        """

        if not id and not screen_name:
            raise ParameterNoneException()

        data = kwargs
        if id: 
            data['user_id'] = id
        if screen_name: 
            data['screen_name'] = screen_name

        res = self.request('GET', 'users/show.json', params=data)
        if not res:
            raise NoneResponseException()

        return User(res, self)

    def users_lookup(self, ids: List[str] = None, screen_names: List[str] = None, **kwargs) -> Dict[str, User]:
        """
        Fetches up to 100 users by their ids OR screen
        names (Twitter handles).
        IDs and screen names can no be mixed. Screen names
        value list will be prefered.

        **Parameters**

        - `ids: List[str]`  
          List of desired user IDs.  
          *Default: `none`*

        - `screen_names: List[str]`  
          List of desired user screen names
          (handles).  
          *Default: `none`*

        - `**kwargs:`  
          Additional agruments passed directly to the 
          request parameters.

        **Returns**

        - `Dict[str, User]`  
          A dict of user IDs and user names as keys
          linked to the corresponding user objects.
          So, for each user, there are two values in
          the dict. Firstly linked to an ID key and 
          secondly linked to the users user name as 
          key.
        """

        if not ids and not screen_names:
            raise ParameterNoneException()

        data = kwargs
        ln = 0
        if ids and len(ids) > 0:
            data['user_id'] = ','.join([str(id) for id in ids])
            ln += len(ids)
        if screen_names and len(screen_names) > 0:
            data['screen_name'] = ','.join(screen_names)
            ln += len(screen_names)

        if ln < 1 or ln > 100:
            raise ParameterOutOfBoundsException(
                'ids + screen_names length must be in range [1, 100]')

        res = self.request('GET', 'users/lookup.json', params=data)
        if not res:
            return NoneResponseException()

        users = {}
        for r in res:
          user = User(r, self)
          users[user.id_str] = user
          users[user.username or user.screen_name] = user

        return users