from vobla.errors.http import VoblaHTTPError


class VoblaValidationError(VoblaHTTPError):

    code = 422

    def __init__(self, code=None, **messages):
        if code is not None:
            self.code = code
        self.messages = messages
        super(VoblaValidationError, self).__init__(
            self.code, 'Validation error'
        )


class VoblaJWTAuthError(VoblaValidationError):

    code = 401

    def __init__(self, message):
        self.messages = {
            'Authorization': message
        }
        super(VoblaJWTAuthError, self).__init__(
            **self.messages
        )
