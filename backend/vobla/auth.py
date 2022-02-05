import random
import functools

import jwt
from passlib.hash import pbkdf2_sha256
from tornado import gen

from vobla import errors
from vobla.db import models
from vobla.settings import config


class VoblaAuth:
    def __init__(
        self,
        hash_function: callable = pbkdf2_sha256,
        jwt_alg: str = "HS256",
    ):
        self._hash_function = hash_function
        self._jwt_alg = jwt_alg

    def make_user_jwt(self, user: models.User) -> bytes:
        return self.make_jwt(
            {
                "email": user.email,
                "active_session_hash": user.active_session_hash,
            }
        )

    def make_jwt(self, data: dict) -> bytes:
        return jwt.encode(
            data,
            config["tornado"]["secret_key"],
            algorithm=self._jwt_alg,
        ).decode("ascii")

    async def verify_user_jwt(self, pgc, token):
        try:
            data = jwt.decode(
                token, config["tornado"]["secret_key"], algorithms=[self._jwt_alg]
            )
            if "email" not in data:
                return None
            obj = await models.User.select(
                pgc, models.User.c.email == data["email"]
            )
            if obj is None:
                return None
            if obj.active_session_hash != data.get("active_session_hash"):
                return None
            return obj
        except jwt.exceptions.DecodeError:
            pass
        return None

    def verify_password(self, password: str, hash: str) -> bool:
        return self._hash_function.verify(password, hash)

    def generate_active_session_hash(self) -> str:
        r = random.SystemRandom()
        code = "".join(r.choice("0123456789ABCDEF") for i in range(87))
        return code

    def hash_password(self, password: str) -> str:
        return self._hash_function.hash(password)


def jwt_needed(func):
    @functools.wraps(func)
    @gen.coroutine
    def deco(self, *args, **kwargs):
        header = self.request.headers.get("Authorization")
        if header:
            parts = header.split()
            if parts[0].lower() == "bearer":
                self.user = yield from self.application.auth.verify_user_jwt(
                    self.pgc, parts[1]
                )
            if getattr(self, "user", None) is None:
                raise errors.validation.VoblaJWTAuthError(
                    "Authorization token is invalid"
                )
        else:
            raise errors.validation.VoblaJWTAuthError("Authorization header is missing")
        yield from func(self, *args, **kwargs)

    return deco


vobla_auth = VoblaAuth()
