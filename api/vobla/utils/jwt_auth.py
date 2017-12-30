import functools

from tornado import gen

from vobla import errors
from vobla.db.models import User


def jwt_needed(func):

    @functools.wraps(func)
    @gen.coroutine
    def deco(self, *args, **kwargs):
        header = self.request.headers.get('Authorization')
        if header:
            parts = header.split()
            if parts[0].lower() == 'bearer':
                self.user = yield from User.verify_jwt(
                    self.pgc, parts[1]
                )
            if getattr(self, 'user', None) is None:
                raise errors.validation.VoblaJWTAuthError(
                    'Authorization token is invalid'
                )
        else:
            raise errors.validation.VoblaJWTAuthError(
                'Authorization header is missing'
            )
        yield from func(self, *args, **kwargs)

    return deco
