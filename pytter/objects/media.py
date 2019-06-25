

class Media:
    """
    Media object for videos, images or gifs attached to tweets.
    Reference: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/entities-object#media
    """
    
    def __init__(self, data: dict = {}):
        if not data:
            return None
        self.display_url            = data.get('display_url')
        self.expanded_url           = data.get('expanded_url')
        self.id                     = data.get('id') or data.get('media_id')
        self.id_str                 = data.get('id_str') or data.get('media_id_str') or str(self.id)
        self.media_url              = data.get('media_url')
        self.media_url_https        = data.get('media_url_https')
        self.size                   = data.get('size')
        self.url                    = data.get('url')
        self.expanded_url           = data.get('expanded_url')
        self.source_status_id       = data.get('source_status_id')
        self.source_status_id_str   = data.get('source_status_id_str')
        self.type                   = data.get('type')