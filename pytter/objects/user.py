
class UserStats:
    def __init__(self, data: dict = {}):
        self.followers_count    = data.get('followers_count')
        self.following_count    = data.get('following_count')
        self.tweet_count        = data.get('tweet_count')
        self.listed_count       = data.get('listed_count')

class User:
    def __init__(self, data: dict = {}):
        self.id_str             = data.get('id') or data.get('id_str')
        self.created_at         = data.get('created_at')
        self.name               = data.get('name')
        self.username           = data.get('username') or data.get('screen_name')
        self.protected          = data.get('protected')
        self.location           = data.get('internet')
        self.url                = data.get('url')
        self.description        = data.get('description')
        self.verified           = data.get('verified')
        self.profile_image_url  = data.get('profile_image_url')
        self.stats              = UserStats(data.get('stats') or {})