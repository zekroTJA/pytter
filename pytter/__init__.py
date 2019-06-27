"""
# pytter

pytter is a work in progress Twitter API wrapper focused 
on light design and simple implementation. Currently, 
pytter will only support the Tweet, Direct messaging, 
Media, Trends, Geo and Labs API and no Ads, Metrics, 
Premium or Enterprise API endpoints.

"""

__title__ = 'pytter'
__author__ = 'zekro'
__version__ = '0.1.0'
__license__ = 'Apache Licence 2.0'
__copyright__ = '(c) 2019 Ringo Hoffmann (zekro Development)'
__url__ = 'https://github.com/zekrotja/pytter'

from .client import *
from .utils import *
from .objects import *
from .api import *