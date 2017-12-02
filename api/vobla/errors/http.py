import tornado.web

from vobla.errors import VoblaError


class VoblaHTTPError(VoblaError, tornado.web.HTTPError):

    def __init__(self, code, message):
        self.code = code
        self.message = message
        super(VoblaHTTPError, self).__init__(code, reason=message)
