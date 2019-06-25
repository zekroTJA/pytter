import uuid
import base64
import urllib
import requests
from requests_oauthlib import OAuth1, OAuth2

from .credentials import Credentials
from .exceptions import RateLimitException
from ..utils import utils
from ..objects import Tweet, Media
from ..utils import FileInfo


class APISession:

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

    def request(self, method: str, resource_path: str, **kwargs):
        """
        Request the Twitter API with the defined authentication
        credentials.
        This method raises an exception on failed authentication or request.

        Parameters
        ==========

        method : str
            Request method.

        resource_path : str

            Path to the requested resource (without root URI).
            Leading '/' will be cut off.

        **kwargs
            Optional arguments passed to request.request()

        Returns
        =======
        
        Object
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
            raise Exception('request failed with status code {0} and message:'.format(res.status_code))

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

    def upload_media_request(self, command=None, params={}, raw=None, **kwargs):
        """
        Wrap a request to initiate, append or finalize a chunked media upload.

        Parameters
        ==========

        command : str
            Must be 'INIT', 'APPEND' or 'FINALIZE'.
            If 'raw' is set, this must not be passed.

        params : dict
            Request body parameters.
            If 'raw' is set, this must not be passed.

        raw
            Raw data used as reuqest body. 
            This option overwrites 'command' and 'params'.

        **kwargs:
            Additional arguments which will be passed to
            the request method.
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
            print(res.json())
            raise Exception('request failed with status code {0}'.format(res.status_code))

        return res

    def upload_file_cunked(self, file_info: utils.FileInfo, close_after: bool = False) -> Media:
        """
        Try to grab the FileInfo of the specified media file, checks if it 
        can be uploaded to twitter and then tries to upload the file via 
        the chunked twitter media upload endpoint.

        Parameters
        ==========

        media : str
            Either a local file location or a HTTP(S) URL
            to an online file resource.

        close_after: bool
            Wether the file info reader should be closed
            after upload or not.
            Default: False

        Returns
        =======

        Media
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
            raise Exception('res was None')

        return Media(res.json())

    def upload_attachments(self, media: list, close_after: bool = False) -> iter:
        """
        Upload a list of media using chunked upload.
        The list of media can only contain either 4 photos,
        1 gif or 1 video. Everything else will raise an
        exception.

        Parameters
        ==========

        media: list
            List of media objects as path to a local file,
            as URI to an online file which will be downloaded
            and atatched then or an existing FileInfo object.
        
        close_after: bool
            Wether to close each opened file handler after
            uploading or not.
            Default: False

        Returns
        =======

        iter
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

        if max_attachable > len(media):
            raise Exception('you can only attach up to {} files using this attachment type.'
                .format(max_attachable))

        for f in files:
            yield self.upload_file_cunked(f, close_after=close_after)

    def update(self, status: str, media: [list, str] = None, **kwargs) -> Tweet:
        """
        Create a Tweet with specified content.

        Parameters
        ==========

        status : str
            The status text. This can not be None, but empty ('')
            if you do not want to have text content in your tweet.

        img : str
            Image media identifier.
            This can be either a local file location or an
            online file linked by a HHTP(S) URL.

        **kwargs
            Additional keyword arguments which will be directly
            passed to the request arguments.
            You should only use valid arguments supported by the
            POST statuses/update endpoint:
            https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/post-statuses-update

        Returns
        =======

        Tweet
            The result Tweet object.
        """

        data = {
            'status': status,
        }

        for k, v in kwargs.items():
            data[k] = v

        if media is not None:
            if type(media) is not list:
                media = [media]

            media_objs = []

            for media_obj in self.upload_attachments(media):
                media_objs.append(media_obj)

            data['media_ids'] = ','.join([m.id_str for m in media_objs])
        
        res = self.request('POST', 'statuses/update.json', data=data)
        if not res:
            raise Exception('response was None')

        return Tweet(res, self)

    def destroy(self, id: [str, int], **kwargs) -> Tweet:
        """
        Delete a tweet.

        Parameters
        ==========

        id: [str, int]
            ID of the tweet to delete.

        **kwargs:
            Additional agruments passed directly to the 
            request parameters.

        Returns
        =======

        Tweet
            The tweet ofbject which was deleted.
        """
        
        data = {}
        for k, v in kwargs.items():
            data[k] = v

        res = self.request('POST', 'statuses/destroy/{}.json'.format(id), data=data)
        if not res:
            raise Exception('response was None')

        return Tweet(res)