
from enum import Enum

class HTTPMethod(Enum):
    GET=1
    HEAD=2
    POST=3
    PUT=4
    DELETE=5

# see: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
class HTTPContentType(Enum):
    JSON='application/json'
    TEXT_PLAIN='text/plain'
    TEXT_HTML='text/html'
    TEXT_JAVASCRIPT='text/javascript'