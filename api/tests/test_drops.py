import os
import json
import shutil
import tempfile
from itertools import count
from io import BytesIO
from unittest import mock

import requests
from passlib.hash import pbkdf2_sha256
from sqlalchemy import and_
from tornado.testing import gen_test

from vobla.db import User, UserInvite, DropFile, Drop
from vobla.settings import config
from vobla import errors
from tests import TestMixin


class DropsUploadTest(TestMixin):

    @classmethod
    def setUpClass(cls):
        super(DropsUploadTest, cls).setUpClass()
        cls.patches = [
            mock.patch.dict(
                'vobla.settings.config', {
                    'vobla': {
                        'temp_upload_folder': tempfile.mkdtemp(),
                        'upload_folder': tempfile.mkdtemp()
                    }
                }
            )
        ]
        for patch in cls.patches:
            patch.start()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(config['vobla']['temp_upload_folder'])
        shutil.rmtree(config['vobla']['upload_folder'])
        for patch in cls.patches:
            patch.stop()
        super(DropsUploadTest, cls).tearDownClass()

    async def upload_chunk(self, data, **kwargs):
        token = kwargs.pop('token', None)
        drop_hash = kwargs.get('drop_hash', None)
        drop_file_hash = kwargs.get('drop_file_hash', None)
        headers = {}
        headers['Authorization'] = f'bearer {token}'
        headers['Chunk-Number'] = kwargs.get('chunk_number')
        headers['Chunk-Size'] = kwargs.get('chunk_size')
        headers['File-Total-Size'] = kwargs.get('file_total_size')
        if drop_file_hash is not None:
            headers['Drop-File-Hash'] = drop_file_hash
        if drop_hash is not None:
            headers['Drop-Hash'] = drop_hash
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

    @gen_test
    async def test_valid_upload(self):
        data = {
            'email': 'email',
            'password_hash': 'pass',
        }
        async with self._app.pg.acquire() as conn:
            u = await User.insert(conn, data)
        token = u.make_jwt()
        chunk_size = 100
        drop_hash = None
        file_path = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'python-logo.png'
        )
        file_total_size = os.stat(file_path).st_size
        with open(file_path, 'rb') as f:
            data = f.read()
            response = await self.upload_chunk(
                data[:chunk_size],
                token=token,
                chunk_number=1,
                chunk_size=chunk_size,
                file_total_size=file_total_size,
                drop_hash=drop_hash
            )
            if file_total_size > chunk_size:
                assert response.code == 200
                assert 'drop_file_hash' in response.body
                drop_file_hash = response.body['drop_file_hash']
                drop_hash = response.body['drop_hash']
                for chunk_number in count(2):
                    offset = (chunk_number - 1) * chunk_size
                    limit = chunk_number * chunk_size
                    send_data = data[offset:limit]
                    response = await self.upload_chunk(
                        send_data,
                        token=token,
                        chunk_number=chunk_number,
                        chunk_size=chunk_size,
                        file_total_size=file_total_size,
                        drop_file_hash=drop_file_hash,
                        drop_hash=drop_hash
                    )
                    if chunk_number * chunk_size >= file_total_size:
                        assert response.code == 201
                        drop_file = await DropFile.select(
                            conn,
                            and_(
                                DropFile.c.hash==drop_file_hash,
                                Drop.c.hash==drop_hash
                            )
                        )
                        assert drop_file is not None
                        assert os.path.exists(drop_file.file_path) is True
                        assert drop_file.mimetype == 'image/png'
                        with open(drop_file.file_path, 'rb') as uploaded_f:
                            assert uploaded_f.read() == data
                        break
                    else:
                        assert response.code == 200
            else:
                assert response.code == 201
