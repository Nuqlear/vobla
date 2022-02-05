import psycopg2
from webargs.tornadoparser import use_args

from vobla import errors
from vobla.auth import jwt_needed
from vobla.schemas import args
from vobla.handlers import BaseHandler
from vobla.utils import api_spec_exists
from vobla.db import models


def email_simple_validation(email):
    return (
        len(email) > 4
        and len(email) < 254
        and email.count("@") != 0
        and email.count(".") != 0
    )


@api_spec_exists
class SignupHandler(BaseHandler):
    @use_args(args.auth.UserSignupSchema, locations=("json",))
    async def post(self, reqargs):
        """
        ---
        description: Sign up an user
        parameters:
            - in: body
              schema: UserSignupSchema
        tags:
            - users
        responses:
            201:
                description: User is registered
                schema: SuccessfulAuthSchema
            422:
                description: Incorrect input data
                schema: ValidationErrorSchema
        """
        async with self.pgc.begin() as tr:
            if not email_simple_validation(reqargs["email"]):
                raise errors.validation.VoblaValidationError(
                    email="Email does not look valid"
                )
            password = reqargs.pop("password")
            user = models.User(
                **reqargs,
                password_hash=self.application.auth.hash_password(password),
                active_session_hash=self.application.auth.generate_active_session_hash(),
            )
            try:
                await user.insert(self.pgc)
                jwt = self.application.auth.make_user_jwt(user)
                response = {"token": jwt}
                self.set_status(201)
            except psycopg2.IntegrityError:
                tr.rollback()
                raise errors.validation.VoblaValidationError(
                    email="Email already registered"
                )
            self.write(response)


@api_spec_exists
class LoginHandler(BaseHandler):
    @use_args(args.auth.UserLoginSchema, locations=("json",))
    async def post(self, reqargs):
        """
        ---
        description: Authorize an user
        parameters:
            - in: body
              schema: UserLoginSchema
        tags:
            - users
        responses:
            202:
                description: User is authorized
                schema: SuccessfulAuthSchema
            422:
                description: Incorrect input data
                schema: ValidationErrorSchema
        """
        user = await models.User.select(
            self.pgc, models.User.c.email == reqargs["email"]
        )
        if not (
            user
            and self.application.auth.verify_password(
                reqargs["password"],
                user.password_hash,
            )
        ):
            raise errors.validation.VoblaValidationError(
                email="Incorrect login/password", password="Invalid login/password"
            )
        else:
            self.set_status(202)
            jwt = self.application.auth.make_user_jwt(user)
            response = {"token": jwt}
            self.write(response)
            self.finish()


@api_spec_exists
class JWTCheckHandler(BaseHandler):
    @jwt_needed
    async def get(self):
        """
        ---
        description: Check Authorization token for validity
        parameters:
            - in: header
              name: 'Authorization'
              type: string
              required: true
        tags:
            - users
        responses:
            204:
                description: Valid credentials
            401:
                description: Invalid/Missing authorization header
                schema: ValidationErrorSchema
        """
        self.set_status(204)
        self.clear_header("Content-Type")
        self.finish()
