
class Coordinates:
    """
    Geo location coordinates.
    Reference: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/geo-objects#coordinates
    """
    
    def __init__(self, data: dict = {}):
        if not data:
            return None
        self.coordinates = data.get('coordinates')
        self.type        = data.get('type')

class BoundingBox:
    """
    Describes an area by coordinates.
    Reference: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/geo-objects#bounding-box
    """
    
    def __init__(self, data: dict = {}):
        if not data:
            return None
        self.coordinates    = [Coordinates(c) for c in data.get('coordinates')]
        self.type           = data.get('type')

class Place:
    """
    A specific, named geo location place with defined 
    area coordinates.
    Reference: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/geo-objects#place
    """

    def __init__(self, data: dict = {}):
        if not data:
            return None
        self.id             = data.get('id')
        self.url            = data.get('url')
        self.place_type     = data.get('place_type')
        self.name           = data.get('name')
        self.full_name      = data.get('full_name')
        self.country_code   = data.get('country_code')
        self.country        = data.get('country')
        self.bounding_box   = BoundingBox(data.get('bounding_box')) if 'bounding_box' in data else None
        self.attributes     = data.get('attributes')