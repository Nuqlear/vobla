
class VoblaError(Exception):

    def __init__(self, *ar, **kw):
        super(VoblaError, self).__init__(*ar, **kw)


from . import validation
from . import http
