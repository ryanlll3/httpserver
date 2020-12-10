"""
could accept client request

"""

from views import *
# router table
urls = [
    ('/time', show_time),
    ('/hello', hello),
    ('/bye', bye)
]
