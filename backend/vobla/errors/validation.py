from vobla.errors.http import VoblaHTTPError


class VoblaValidationError(VoblaHTTPError):

    code = 422

    def __init__(self, code=None, **fields):
        if code is not None:
            self.code = code
        self.fields = fields
        super(VoblaValidationError, self).__init__(
            self.code, 'Validation error'
        )


class VoblaJWTAuthError(VoblaValidationError):

    code = 401

    def __init__(self, message):
        self.fields = {
            'Authorization': message
        }
        super(VoblaJWTAuthError, self).__init__(
            **self.fields
        )
