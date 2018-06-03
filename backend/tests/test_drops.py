import os
import json
import shutil
import tempfile
from itertools import count
from io import BytesIO
from unittest import mock
from datetime import datetime
from datetime import timezone

import requests
from sqlalchemy import and_
from tornado.testing import gen_test

from vobla.db import models
from vobla.settings import config
from vobla import errors
from tests import TestMixin


class DropsTestMixin(TestMixin):

    @classmethod
    def setUpClass(cls):
        super(DropsTestMixin, cls).setUpClass()
        cls.patches = [
            mock.patch.dict(
                config._proxies['vobla'], {
                    'upload_folder': tempfile.mkdtemp()
                }
            )
        ]
        for patch in cls.patches:
            patch.start()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(config['vobla']['upload_folder'])
        for patch in cls.patches:
            patch.stop()
        super(DropsTestMixin, cls).tearDownClass()


class UserDropsHandlerTest(DropsTestMixin):

    url = '/api/drops'

    @gen_test
    async def test_GET_valid_args(self):
        user_data = {
            'email': 'email',
            'password_hash': 'pass',
        }
        async with self._app.pg.acquire() as conn:
            u = await models.User.insert(conn, user_data)
            token = u.make_jwt()
            drop = await models.Drop.create(conn, u)
            await models.DropFile.create(conn, drop)
            resp = await self.fetch_json(
                self.url,
                method='GET',
                headers={
                    'Authorization': f'bearer {token}',
                }
            )
            assert resp.code == 200
            assert 'drops' in resp.body
            drops = resp.body['drops']
            assert len(drops) == 1
            for attr in (
                'name', 'hash'
            ):
                assert getattr(drop, attr) == drops[0][attr]
            assert drops[0]['owner']['email'] == u.email
            assert (
                drop.created_at.replace(tzinfo=timezone.utc).isoformat() ==
                drops[0]['created_at']
            )
            assert 'dropfiles' in drops[0]
            assert len(drops[0]['dropfiles']) == 0
            dropfile2 = await models.DropFile.create(conn, drop)
            dropfile2.uploaded_at = datetime.utcnow()
            await dropfile2.update(conn)
            resp = await self.fetch_json(
                self.url,
                method='GET',
                headers={
                    'Authorization': f'bearer {token}',
                }
            )
            assert 'drops' in resp.body
            drops = resp.body['drops']
            assert len(drops) == 1
            assert 'dropfiles' in drops[0]
            assert len(drops[0]['dropfiles']) == 1
            for attr in (
                'name', 'hash', 'mimetype'
            ):
                assert (
                    getattr(dropfile2, attr, None) ==
                    drops[0]['dropfiles'][0][attr]
                )
            assert (
                (
                    dropfile2.uploaded_at
                    .replace(tzinfo=timezone.utc).isoformat()
                ) == drops[0]['dropfiles'][0]['uploaded_at']
            )

    @gen_test
    async def test_GET_unauthorized(self):
        resp = await self.fetch_json(
            self.url,
            method='GET',
        )
        self.assertValidationError(resp, 'Authorization', 401)

    @gen_test
    async def test_DELETE_valid(self):
        user_data = {
            'email': 'email',
            'password_hash': 'pass',
        }
        async with self._app.pg.acquire() as conn:
            user = await models.User.insert(conn, user_data)
            token = user.make_jwt()
            drop = await models.Drop.create(conn, user)
            await models.DropFile.create(conn, drop)
            resp = await self.fetch(
                self.url,
                method='DELETE',
                headers={
                    'Authorization': f'bearer {token}',
                }
            )
            assert resp.code == 200
            drops = await models.Drop.select(
                conn,
                models.Drop.c.owner_id == user.id,
                return_list=True
            )
            self.assertListEqual(drops, [])


async def _create_dropfile(conn):
    user_data = {
        'email': 'email',
        'password_hash': 'pass',
    }
    u = await models.User.insert(conn, user_data)
    drop = await models.Drop.create(conn, u)
    dropfile = await models.DropFile.create(conn, drop)
    return u, drop, dropfile


class DropHandlerTest(DropsTestMixin):

    @gen_test
    async def test_GET_valid(self):
        async with self._app.pg.acquire() as conn:
            u, drop, dropfile = await _create_dropfile(conn)
            resp = await self.fetch_json(
                f'/api/drops/{drop.hash}',
                method='GET'
            )
            assert resp.code == 200
            for attr in (
                'name', 'hash'
            ):
                assert getattr(drop, attr) == resp.body[attr]
            assert resp.body['owner']['email'] == u.email
            assert (
                drop.created_at.replace(tzinfo=timezone.utc).isoformat() ==
                resp.body['created_at']
            )
            assert 'dropfiles' in resp.body
            assert len(resp.body['dropfiles']) == 0
            dropfile2 = await models.DropFile.create(conn, drop)
            dropfile2.uploaded_at = datetime.utcnow()
            await dropfile2.update(conn)
            resp = await self.fetch_json(
                f'/api/drops/{drop.hash}',
                method='GET'
            )
            assert 'dropfiles' in resp.body
            assert len(resp.body['dropfiles']) == 1
            for attr in (
                'name', 'hash', 'mimetype'
            ):
                assert (
                    getattr(dropfile2, attr, None) ==
                    resp.body['dropfiles'][0][attr]
                )
            assert (
                (
                    dropfile2.uploaded_at
                    .replace(tzinfo=timezone.utc).isoformat()
                ) == resp.body['dropfiles'][0]['uploaded_at']
            )

    @gen_test
    async def test_DELETE_valid(self):
        async with self._app.pg.acquire() as conn:
            user, drop, dropfile = await _create_dropfile(conn)
            token = user.make_jwt()
            resp = await self.fetch(
                f'/api/drops/files/{dropfile.hash}',
                method='DELETE',
                headers={
                    'Authorization': f'bearer {token}',
                }
            )
            assert resp.code == 200
            dropfile = await models.DropFile.select(
                conn, models.DropFile.c.id == dropfile.id
            )
            assert dropfile is None

    @gen_test
    async def test_DELETE_unauthorized(self):
        async with self._app.pg.acquire() as conn:
            _, drop, _ = await _create_dropfile(conn)
        resp = await self.fetch_json(
            f'/api/drops/{drop.hash}',
            method='DELETE',
        )
        self.assertValidationError(resp, 'Authorization', 401)


class DropFileHandler(DropsTestMixin):

    @gen_test
    async def test_DELETE_unauthorized(self):
        async with self._app.pg.acquire() as conn:
            _, _, dropfile = await _create_dropfile(conn)
        resp = await self.fetch_json(
            f'/api/drops/files/{dropfile.hash}',
            method='DELETE',
        )
        self.assertValidationError(resp, 'Authorization', 401)

    @gen_test
    async def test_DELETE_valid(self):
        async with self._app.pg.acquire() as conn:
            user, drop, dropfile = await _create_dropfile(conn)
            token = user.make_jwt()
            resp = await self.fetch(
                f'/api/drops/files/{dropfile.hash}',
                method='DELETE',
                headers={
                    'Authorization': f'bearer {token}',
                }
            )
            assert resp.code == 200
            dropfile = await models.DropFile.select(
                conn, models.DropFile.c.id == dropfile.id
            )
            assert dropfile is None

    @gen_test
    async def test_GET_valid(self):
        async with self._app.pg.acquire() as conn:
            _, _, dropfile = await _create_dropfile(conn)
            resp = await self.fetch(
                f'/api/drops/files/{dropfile.hash}',
                method='GET'
            )
            assert resp.code == 200

    @gen_test
    async def test_GET_404(self):
        async with self._app.pg.acquire() as conn:
            _, _, dropfile = await _create_dropfile(conn)
            resp = await self.fetch(
                f'/api/drops/files/{models.hashids.encode(1231, 1)}',
                method='GET'
            )
            assert resp.code == 404


class DropUploadHandlerTest(DropsTestMixin):

    async def _upload_chunk(self, data, headers):
        headers = {
            key: str(value) for key, value in headers.items()
        }
        prepare = (
            requests.Request(
                url="http://localhost/img",
                files={"chunk": (BytesIO(data))},
                data={}
            )
            .prepare()
        )
        headers['Content-Type'] = prepare.headers.get('Content-Type')
        response = await self.fetch(
            '/api/drops/upload',
            headers=headers,
            method='POST',
            body=prepare.body
        )
        if response.body:
            response._body = json.loads(response._body)
        return response

    async def _test_valid_upload(self, pgc, token, chunk_size, drop_hash=None):
        file_path = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'python-logo.png'
        )
        file_total_size = os.stat(file_path).st_size
        headers = {
            'Authorization': f'bearer {token}',
            'Chunk-Number': 1,
            'Chunk-Size': chunk_size,
            'File-Total-Size': file_total_size
        }
        if drop_hash is not None:
            headers['Drop-Hash'] = drop_hash
        drop_file = None
        with open(file_path, 'rb') as f:
            data = f.read()
            response = await self._upload_chunk(
                data[:chunk_size], headers
            )
            assert 'drop_file_hash' in response.body
            assert 'drop_hash' in response.body
            assert 'url' in response.body
            drop_file_hash = response.body['drop_file_hash']
            drop_hash = response.body['drop_hash']
            if file_total_size > chunk_size:
                assert response.code == 200
                for chunk_number in count(2):
                    offset = (chunk_number - 1) * chunk_size
                    limit = chunk_number * chunk_size
                    send_data = data[offset:limit]
                    headers.update({
                        'Chunk-Number': chunk_number,
                        'Drop-File-Hash': drop_file_hash,
                        'Drop-Hash': drop_hash
                    })
                    response = await self._upload_chunk(
                        send_data, headers
                    )
                    if chunk_number * chunk_size >= file_total_size:
                        break
                    else:
                        assert response.code == 200
        assert response.code == 201
        drop_file = await models.DropFile.select(
            pgc,
            and_(
                models.DropFile.c.hash == drop_file_hash,
                models.Drop.c.hash == drop_hash
            )
        )
        assert drop_file is not None
        assert os.path.exists(drop_file.file_path) is True
        assert drop_file.mimetype == 'image/png'
        with open(drop_file.file_path, 'rb') as uploaded_f:
            assert uploaded_f.read() == data
        return drop_file

    @gen_test(timeout=15)
    async def test_POST_full_valid_cycle(self):
        '''
        test DropFile upload by one and multiple chunks.
        '''
        data = {
            'email': 'email',
            'password_hash': 'pass',
        }
        async with self._app.pg.acquire() as conn:
            u = await models.User.insert(conn, data)
            token = u.make_jwt()
            drop = await models.Drop.create(conn, u)
            # 100000b should be enough to upload fixture file by one request
            chunk_sizes = [100, 100000]
            for chunk_size in chunk_sizes:
                drop_file = await self._test_valid_upload(
                    conn, token, chunk_size
                )
                assert drop_file.drop_id != drop.id
            for chunk_size in chunk_sizes:
                drop_file = await self._test_valid_upload(
                    conn, token, chunk_size, drop.hash
                )
                assert drop_file.drop_id == drop.id

    @gen_test
    async def test_POST_invalid_token(self):
        headers = {
            'Authorization': f'bearer asdasda',
            'Chunk-Number': 1,
            'Chunk-Size': 100,
            'File-Total-Size': 100
        }
        data = os.urandom(100)
        resp = await self._upload_chunk(data, headers)
        self.assertValidationError(
            resp, 'Authorization', errors.validation.VoblaJWTAuthError.code
        )

    @gen_test
    async def test_POST_invalid_hashes(self):
        user_data = {
            'email': 'email',
            'password_hash': 'pass',
        }
        async with self._app.pg.acquire() as conn:
            u = await models.User.insert(conn, user_data)
            drop = await models.Drop.create(conn, u)
            dropfile = await models.DropFile.create(conn, drop)
            data = os.urandom(100)
            user_data['email'] = 'email2'
            u2 = await models.User.insert(conn, user_data)
            u2_token = u2.make_jwt()
            # logic for first and next chunks has some differencies
            for chunk_number in [1, 2]:
                # non-existing dropfile's hash
                headers = {
                    'Authorization': f'bearer {u2_token}',
                    'Chunk-Number': chunk_number,
                    'Chunk-Size': 100,
                    'File-Total-Size': 200,
                    'Drop-Hash': models.hashids.encode(21231, 1)
                }
                resp = await self._upload_chunk(data, headers)
                self.assertValidationError(resp, 'Drop-Hash', 404)
                # hash of dropfile which owned by another user
                headers = {
                    'Authorization': f'bearer {u2_token}',
                    'Chunk-Number': chunk_number,
                    'Chunk-Size': 100,
                    'File-Total-Size': 100,
                    'Drop-Hash': drop.hash
                }
                resp = await self._upload_chunk(data, headers)
                self.assertValidationError(resp, 'Drop-Hash', 403)
                # nonexisting drop's hash
                headers = {
                    'Authorization': f'bearer {u2_token}',
                    'Chunk-Number': chunk_number,
                    'Chunk-Size': 100,
                    'File-Total-Size': 100,
                    'Drop-File-Hash': models.hashids.encode(1231, 1)
                }
                resp = await self._upload_chunk(data, headers)
                self.assertValidationError(resp, 'Drop-File-Hash', 404)
                # hash of dropfile which owned by another user
                headers = {
                    'Authorization': f'bearer {u2_token}',
                    'Chunk-Number': chunk_number,
                    'Chunk-Size': 100,
                    'File-Total-Size': 100,
                    'Drop-File-Hash': dropfile.hash
                }
                resp = await self._upload_chunk(data, headers)
                self.assertValidationError(resp, 'Drop-File-Hash', 403)

    @gen_test
    async def test_POST_invalid_chunk_number(self):
        user_data = {
            'email': 'email',
            'password_hash': 'pass',
        }
        async with self._app.pg.acquire() as conn:
            u = await models.User.insert(conn, user_data)
            drop = await models.Drop.create(conn, u)
            dropfile = await models.DropFile.create(conn, drop)
            token = u.make_jwt()
            resp = await self._upload_chunk(
                os.urandom(100), {
                    'Authorization': f'bearer {token}',
                    'Chunk-Number': 2,
                    'Chunk-Size': 100,
                    'File-Total-Size': 200,
                    'Drop-Hash': drop.hash,
                    'Drop-File-Hash': dropfile.hash
                }
            )
            self.assertValidationError(resp, 'Chunk-Number', 422)
