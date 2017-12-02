from passlib.hash import pbkdf2_sha256
from tornado.testing import gen_test

from vobla.db import User, UserInvite
from vobla import errors
from tests import TestMixin


class SignupTest(TestMixin):

    async def _test_case(self, case_data, code):
        resp = await self.fetch_json(
            '/api/users/signup',
            body=case_data,
            method='POST',
            headers={}
        )
        assert resp.code == code
        return resp

    @gen_test
    async def test_incomplete_data(self):
        async with self.pg.acquire() as conn:
            ui = await UserInvite.create(conn)
        cases = [
            {},
            {'email': 'asdas'},
            {'password': '228'},
            {'invite_code': ui.code},
            {'email': 'em', 'password': '228'}
        ]
        for case_data in cases:
            resp = await self._test_case(
                case_data, errors.validation.VoblaValidationError.code
            )
            assert 'token' not in resp.body

    @gen_test
    async def test_valid_data(self):
        async with self.pg.acquire() as conn:
            ui = await UserInvite.create(conn)
            data = {
                'email': 'email',
                'password': 'pass',
                'invite_code': ui.code
            }
            resp = await self._test_case(data, 201)
            assert 'token' in resp.body
            user = await User.select(
                conn, User.c.email==data['email']
            )
            assert user is not None
            assert pbkdf2_sha256.verify(
                data['password'], user.password_hash
            )

    @gen_test
    async def test_already_registered(self):
        data = {
            'email': 'email',
            'password_hash': 'pass',
        }
        async with self._app.pg.acquire() as conn:
            await User.insert(conn, data)
            ui = await UserInvite.create(conn)
            data['invite_code'] = ui.code
        data['password'] = data.pop('password_hash')
        resp = await self._test_case(
            data, errors.validation.VoblaValidationError.code
        )
        assert 'token' not in resp.body


class LoginTest(TestMixin):

    async def _test_case(self, case_data, code):
        resp = await self.fetch_json(
            '/api/users/login',
            body=case_data,
            method='POST',
            headers={}
        )
        assert resp.code == code
        return resp

    @gen_test
    async def test_incomplete_data(self):
        cases = [
            {}, {'email': 'asdas'}, {'password': '228'}
        ]
        for case_data in cases:
            resp = await self._test_case(
                case_data, errors.validation.VoblaValidationError.code
            )
            assert 'token' not in resp.body

    @gen_test
    async def test_valid_non_registered_data(self):
        data = {
            'email': 'email',
            'password': 'pass'
        }
        resp = await self._test_case(
            data, errors.validation.VoblaValidationError.code
        )
        assert 'token' not in resp.body

    @gen_test
    async def test_valid_data(self):
        data = {
            'email': 'email',
            'password': 'pass'
        }
        async with self._app.pg.acquire() as conn:
            await User.insert(
                conn,
                dict(
                    email=data['email'],
                    password_hash=pbkdf2_sha256.hash(data['password'])
                )
            )
        resp = await self._test_case(data, 202)
        assert 'token' in resp.body


class SyncTest(TestMixin):

    async def _test_case(self, jwt, code):
        headers = (
            jwt and {'Authorization': 'bearer {}'.format(jwt)} or {}
        )
        resp = await self.fetch(
            '/api/users/jwtcheck',
            method='GET',
            headers=headers
        )
        assert resp.code == code

    @gen_test
    async def test_headers(self):
        data = {
            'email': 'email',
            'password': 'pass'
        }
        async with self._app.pg.acquire() as conn:
            user = await User.insert(
                conn,
                dict(
                    email=data['email'],
                    password_hash=pbkdf2_sha256.hash(data['password'])
                )
            )
            jwt = user.make_jwt()
        for token, code in [
            (jwt, 201),
            (jwt[:-1], errors.validation.VoblaJWTAuthError.code),
            (None, errors.validation.VoblaJWTAuthError.code)
        ]:
            await self._test_case(token, code)
