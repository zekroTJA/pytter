"""
# pytter

pytter is a work in progress Twitter API wrapper focused
on light design and simple implementation. Currently,
pytter will only support the Tweet, Direct messaging,
Media, Trends, Geo and Labs API and no Ads, Metrics,
Premium or Enterprise API endpoints.

## Usage Example

    from pytter import Client, Credentials
    
    creds = Credentials(
        consumer_key='yourConsumerKey',
        consumer_secret='yourConsumerSecret',
        access_token_key='yourAccessTokenKey,
        access_token_secret='yourAccesTokenSecret')
        
    client = Client(creds)
    
    tweet = client.status_update('Hey Twitter API!')
    print('Tweet ID: {}'.format(tweet.id_str))


Here you can find more examples using pytter:  
- [examples in master-branch](https://github.com/zekroTJA/pytter/tree/master/examples)  
- [examples in dev-branch](https://github.com/zekroTJA/pytter/tree/dev/examples)  

## API

There are two main API access points you can use with pytter:

### The [`Client`](client/client.m.html) API

[`Client`](client/client.m.html) is a class that wraps around the  [`APISession`](api/api.m.html).  
It is an easy to use interface for using the Twitter API as intuitively as possible 
by supplying amended function names, alias functions and sub-functions of API objects
to inetract and work with them.

So, you can create a [`Tweet`](objects/tweet.m.html) by using the following function:  

    tweet = client.status_update(
        'Hey! This is a little test!')

And later, you can delete the [`Tweet`](objects/tweet.m.html) using the sub-function `delete`:  

    tweet.delete()

You can use the same to fetch a tweet by its ID and then retweet this tweet:

    tweet = client.status('1142746872953671680')
    retweet = tweet.retweet()

### The [`APISession`](api/api.m.html) API

[`APISession`](api/api.m.html) is a barebone implementation of the Twitter API representing
each API endpoint in the same naming syntax as function. Resulting objects will be also
usable with the sub-functions named above due to architecture of the API wrapper. But if you
are more confident using a raw API interface, the [`APISession`](api/api.m.html) class may be your
way to go.

Example:  

    from pytter import APISession, Credentials

    creds = Credentials(
        consumer_key='yourConsumerKey',
        consumer_secret='yourConsumerSecret',
        access_token_key='yourAccessTokenKey,
        access_token_secret='yourAccesTokenSecret')

    session = APISession(creds)

    tweet = session.statuses_update(
        status='Hey, this is a test Tweet!')
    recovered = session.statuses_show(id=tweet.id_str)
    session.statuses_destroy(id=recovered.id_str)

"""

__title__     = 'pytter'
__author__    = 'zekro'
__version__   = '0.1.0'
__license__   = 'Apache Licence 2.0'
__copyright__ = '(c) 2019 Ringo Hoffmann (zekro Development)'
__url__       = 'https://github.com/zekrotja/pytter'

from .client import *
from .utils import *
from .objects import *
from .api import *