"""
# pytter

pytter is a work in progress Twitter API wrapper focused
on light design and simple implementation. Currently,
pytter will only support the Tweet, Direct messaging,
Media, Trends, Geo and Labs API and no Ads, Metrics,
Premium or Enterprise API endpoints.

***Usage Example**

```python
from pytter import Client, Credentials

creds = Credentials(
    consumer_key='yourConsumerKey',
    consumer_secret='yourConsumerSecret',
    access_token_key='yourAccessTokenKey,
    access_token_secret='yourAccesTokenSecret')
    
client = Client(creds)

tweet = client.status_update('Hey Twitter API!')
print('Tweet ID: {}'.format(tweet.id_str))
```

Here you can find more examples using pytter:
- [examples in master-branch](https://github.com/zekroTJA/pytter/tree/master/examples)
- [examples in dev-branch](https://github.com/zekroTJA/pytter/tree/dev/examples)

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