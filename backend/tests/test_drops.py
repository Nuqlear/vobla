import os
import json
from itertools import count
from io import BytesIO

import requests
from sqlalchemy import and_
from tornado.testing import gen_test

from vobla.db import models
from vobla import errors
from tests import TestMixin
from tests import factories


class TestGetDrops(TestMixin):

    url = "/api/drops"

    @gen_test
    async def test_when_authenticated_then_drops_returned(self):
        async with self._app.pg.acquire() as conn:
            u = await factories.UserFactory(conn=conn)
            drop = await factories.DropFactory(conn=conn, owner_id=u.id)
            await drop.update_hash(conn)
            token = self.auth.make_user_jwt(u)
            resp = await self.fetch_json(
                self.url, method="GET", headers={"Authorization": f"bearer {token}"}
            )
            assert resp.code == 200
            assert "drops" in resp.body
            drops = resp.body["drops"]
            assert len(drops) == 1
            for attr in ("name", "hash"):
                assert getattr(drop, attr) == drops[0][attr]
            assert "dropfiles" in drops[0]
            assert len(drops[0]["dropfiles"]) == 0
            dropfile2 = await factories.DropFileFactory(conn=conn, drop_id=drop.id)
            resp = await self.fetch_json(
                self.url, method="GET", headers={"Authorization": f"bearer {token}"}
            )
            assert "drops" in resp.body
            drops = resp.body["drops"]
            assert len(drops) == 1
            assert "dropfiles" in drops[0]
            assert len(drops[0]["dropfiles"]) == 1
            for attr in ("name", "hash", "mimetype"):
                assert getattr(dropfile2, attr, None) == drops[0]["dropfiles"][0][attr]

    @gen_test
    async def test_when_unauthenticated_then_401_returned(self):
        resp = await self.fetch_json(self.url, method="GET")
        self.assertValidationError(resp, "Authorization", 401)


class TestDeleteDrops(TestMixin):

    url = "/api/drops"

    @gen_test
    async def test_when_user_authenticated_then_drops_deleted(self):
        async with self._app.pg.acquire() as conn:
            user = await factories.UserFactory(conn=conn)
            token = self.auth.make_user_jwt(user)
            drop = await models.Drop.create(conn, user)
            await models.DropFile.create(conn, drop)
            resp = await self.fetch(
                self.url, method="DELETE", headers={"Authorization": f"bearer {token}"}
            )
            assert resp.code == 200
            drops = await models.Drop.select(
                conn, models.Drop.c.owner_id == user.id, return_list=True
            )
            self.assertListEqual(drops, [])

    @gen_test
    async def test_when_unauthenticated_then_401_returned(self):
        resp = await self.fetch(self.url, method="DELETE")
        self.assertValidationError(resp, "Authorization", 401)


async def _create_dropfile(conn):
    u = await factories.UserFactory(conn=conn)
    drop = await factories.DropFactory(conn=conn, owner_id=u.id)
    await drop.update_hash(conn)
    dropfile = await factories.DropFileFactory(conn=conn, drop_id=drop.id)
    await dropfile.update_hash(conn)
    return u, drop, dropfile


class TestGetDrop(TestMixin):
    @gen_test
    async def test_when_user_authenticated_then_drop_returned(self):
        async with self._app.pg.acquire() as conn:
            u = await factories.UserFactory(conn=conn)
            drop = await factories.DropFactory(conn=conn, owner_id=u.id)
            await drop.update_hash(conn)
            dropfile = await factories.DropFileFactory(conn=conn, drop_id=drop.id)
            await dropfile.update_hash(conn)
        resp = await self.fetch_json(f"/api/drops/{drop.hash}", method="GET")
        assert resp.code == 200
        for attr in ("name", "hash"):
            assert getattr(drop, attr) == resp.body[attr]
        assert (
            drop.created_at.replace(tzinfo=None).isoformat() == resp.body["created_at"]
        )
        assert "dropfiles" in resp.body
        assert len(resp.body["dropfiles"]) == 1
        for attr in ("name", "hash", "mimetype"):
            assert getattr(dropfile, attr, None) == resp.body["dropfiles"][0][attr]


class TestGetDropFile(TestMixin):
    @gen_test
    async def test_when_user_authenticated_then_dropfiles_deleted(self):
        async with self._app.pg.acquire() as conn:
            _, _, dropfile = await _create_dropfile(conn)
            resp = await self.fetch(f"/api/drops/files/{dropfile.hash}", method="GET")
            assert resp.code == 200

    @gen_test
    async def test_when_dropfile_doesnt_exist_then_404_returned(self):
        async with self._app.pg.acquire() as conn:
            _, _, dropfile = await _create_dropfile(conn)
            resp = await self.fetch(
                f"/api/drops/files/{models.Drop.encode(1231)}", method="GET"
            )
            assert resp.code == 404


class TestDeleteDropFile(TestMixin):
    @gen_test
    async def test_when_user_authenticated_then_dropfiles_deleted(self):
        async with self._app.pg.acquire() as conn:
            user, _, dropfile = await _create_dropfile(conn)
            token = self.auth.make_user_jwt(user)
            resp = await self.fetch(
                f"/api/drops/files/{dropfile.hash}",
                method="DELETE",
                headers={"Authorization": f"bearer {token}"},
            )
            assert resp.code == 200
            dropfile = await models.DropFile.select(
                conn, models.DropFile.c.id == dropfile.id
            )
            assert dropfile is None

    @gen_test
    async def test_when_user_unauthenticated_then_401_returned(self):
        async with self._app.pg.acquire() as conn:
            _, drop, _ = await _create_dropfile(conn)
        resp = await self.fetch_json(f"/api/drops/{drop.hash}", method="DELETE")
        self.assertValidationError(resp, "Authorization", 401)


class TestDropUploadByChunks(TestMixin):
    async def _upload_chunk(self, data, headers):
        headers = {key: str(value) for key, value in headers.items()}
        prepare = requests.Request(
            url="http://localhost/img", files={"chunk": (BytesIO(data))}, data={}
        ).prepare()
        headers["Content-Type"] = prepare.headers.get("Content-Type")
        response = await self.fetch(
            "/api/drops/upload/chunks",
            headers=headers,
            method="POST",
            body=prepare.body,
        )
        if response.body:
            response._body = json.loads(response._body)
        return response

    async def _test_valid_upload(self, pgc, token, chunk_size, drop_hash=None):
        file_path = os.path.join(
            os.path.dirname(__file__), "fixtures", "python-logo.png"
        )
        file_total_size = os.stat(file_path).st_size
        headers = {
            "Authorization": f"bearer {token}",
            "Chunk-Number": 1,
            "Chunk-Size": chunk_size,
            "File-Total-Size": file_total_size,
        }
        if drop_hash is not None:
            headers["Drop-Hash"] = drop_hash
        drop_file = None
        with open(file_path, "rb") as f:
            data = f.read()
            response = await self._upload_chunk(data[:chunk_size], headers)
            assert "drop_file_hash" in response.body
            assert "drop_hash" in response.body
            assert "url" in response.body
            drop_file_hash = response.body["drop_file_hash"]
            drop_hash = response.body["drop_hash"]
            if file_total_size > chunk_size:
                assert response.code == 200
                for chunk_number in count(2):
                    offset = (chunk_number - 1) * chunk_size
                    limit = chunk_number * chunk_size
                    send_data = data[offset:limit]
                    headers.update(
                        {
                            "Chunk-Number": chunk_number,
                            "Drop-File-Hash": drop_file_hash,
                            "Drop-Hash": drop_hash,
                        }
                    )
                    response = await self._upload_chunk(send_data, headers)
                    if chunk_number * chunk_size >= file_total_size:
                        break
                    else:
                        assert response.code == 200
        assert response.code == 201
        drop_file = await models.DropFile.select(
            pgc,
            and_(
                models.DropFile.c.hash == drop_file_hash,
                models.Drop.c.hash == drop_hash,
            ),
        )
        assert drop_file is not None
        assert drop_file.mimetype == "image/png"
        obj = drop_file.get_from_storage(self.storage)
        assert obj is not None
        drop_file_data = obj.read()
        assert drop_file_data == data
        return drop_file

    @gen_test(timeout=120)
    async def test_when_user_authenticated_then_dropfile_uploaded(self):
        """
        test DropFile upload by one and multiple chunks.
        """
        async with self._app.pg.acquire() as conn:
            u = await factories.UserFactory(conn=conn)
            drop = await factories.DropFactory(conn=conn, owner_id=u.id)
            await drop.update_hash(conn)
            token = self.auth.make_user_jwt(u)
            # 100000b should be enough to upload fixture file by one request
            chunk_sizes = [100, 100000]
            for chunk_size in chunk_sizes:
                drop_file = await self._test_valid_upload(conn, token, chunk_size)
                assert drop_file.drop_id != drop.id
            for chunk_size in chunk_sizes:
                drop_file = await self._test_valid_upload(
                    conn, token, chunk_size, drop.hash
                )
                assert drop_file.drop_id == drop.id

    @gen_test
    async def test_when_user_unauthenticated_then_401_returned(self):
        headers = {
            "Authorization": f"bearer asdasda",
            "Chunk-Number": 1,
            "Chunk-Size": 100,
            "File-Total-Size": 100,
        }
        data = os.urandom(100)
        resp = await self._upload_chunk(data, headers)
        self.assertValidationError(
            resp, "Authorization", errors.validation.VoblaJWTAuthError.code
        )

    @gen_test
    async def test_when_drop_file_or_drop_hash_are_invalid_then_errors_returned(self):
        async with self._app.pg.acquire() as conn:
            u = await factories.UserFactory(conn=conn)
            drop = await factories.DropFactory(conn=conn, owner_id=u.id)
            await drop.update_hash(conn)
            dropfile = await factories.DropFileFactory(conn=conn, drop_id=drop.id)
            await dropfile.update_hash(conn)
            data = os.urandom(100)
            u2 = await factories.UserFactory(conn=conn)
            u2_token = self.auth.make_user_jwt(u2)
            # logic for first and next chunks has some differencies
            for chunk_number in [1, 2]:
                # non-existing dropfile's hash
                headers = {
                    "Authorization": f"bearer {u2_token}",
                    "Chunk-Number": chunk_number,
                    "Chunk-Size": 100,
                    "File-Total-Size": 200,
                    "Drop-Hash": models.Drop.encode(21231),
                }
                resp = await self._upload_chunk(data, headers)
                self.assertValidationError(resp, "Drop-Hash", 404)
                # hash of dropfile which owned by another user
                headers = {
                    "Authorization": f"bearer {u2_token}",
                    "Chunk-Number": chunk_number,
                    "Chunk-Size": 100,
                    "File-Total-Size": 100,
                    "Drop-Hash": drop.hash,
                }
                resp = await self._upload_chunk(data, headers)
                self.assertValidationError(resp, "Drop-Hash", 403)
                # nonexisting drop's hash
                headers = {
                    "Authorization": f"bearer {u2_token}",
                    "Chunk-Number": chunk_number,
                    "Chunk-Size": 100,
                    "File-Total-Size": 100,
                    "Drop-File-Hash": models.DropFile.encode(1231),
                }
                resp = await self._upload_chunk(data, headers)
                self.assertValidationError(resp, "Drop-File-Hash", 404)
                # hash of dropfile which owned by another user
                headers = {
                    "Authorization": f"bearer {u2_token}",
                    "Chunk-Number": chunk_number,
                    "Chunk-Size": 100,
                    "File-Total-Size": 100,
                    "Drop-File-Hash": dropfile.hash,
                }
                resp = await self._upload_chunk(data, headers)
                self.assertValidationError(resp, "Drop-File-Hash", 403)

    @gen_test
    async def test_when_dropfile_larger_than_limit_then_error_returned(self):
        async with self._app.pg.acquire() as conn:
            await factories.UserTierFactory(
                conn=conn,
                id=models.UserTierEnum.basic,
                max_drop_file_size=31457280,
            )
            u = await factories.UserFactory(
                conn=conn, user_tier_id=models.UserTierEnum.basic
            )
            u_token = self.auth.make_user_jwt(u)
            drop = await factories.DropFactory(conn=conn, owner_id=u.id)
            await drop.update_hash(conn)
            data = os.urandom(1001)
            headers = {
                "Authorization": f"bearer {u_token}",
                "Chunk-Number": 1,
                "Chunk-Size": 31457281,
                "File-Total-Size": 31457281,
                "Drop-Hash": drop.hash,
            }
            resp = await self._upload_chunk(data, headers)
            self.assertError(resp, "File exceeds account limit of 30 MB per upload", 400)

    @gen_test
    async def test_when_max_storage_larger_than_limit_then_error_returned(self):
        async with self._app.pg.acquire() as conn:
            await factories.UserTierFactory(
                conn=conn,
                id=models.UserTierEnum.basic,
                max_storage_size=31457280,
            )
            u = await factories.UserFactory(
                conn=conn, user_tier_id=models.UserTierEnum.basic
            )
            u_token = self.auth.make_user_jwt(u)
            drop = await factories.DropFactory(conn=conn, owner_id=u.id)
            await drop.update_hash(conn)
            dropfile = await factories.DropFileFactory(
                conn=conn, drop_id=drop.id, size=31457200
            )
            await dropfile.update_hash(conn)
            drop2 = await factories.DropFactory(conn=conn, owner_id=u.id)
            await drop2.update_hash(conn)
            dropfile2 = await factories.DropFileFactory(conn=conn, drop_id=drop2.id)
            await dropfile2.update_hash(conn)
            data = os.urandom(81)
            headers = {
                "Authorization": f"bearer {u_token}",
                "Chunk-Number": 1,
                "Chunk-Size": 81,
                "File-Total-Size": 81,
                "Drop-Hash": models.Drop.encode(21231),
            }
            resp = await self._upload_chunk(data, headers)
            self.assertError(
                resp, "File exceeds account limit of 30 MB per account", 400
            )

    @gen_test
    async def test_when_chunk_number_is_invalid_then_error_returned(self):
        async with self._app.pg.acquire() as conn:
            u = await factories.UserFactory(conn=conn)
            drop = await factories.DropFactory(conn=conn, owner_id=u.id)
            await drop.update_hash(conn)
            dropfile = await factories.DropFileFactory(conn=conn, drop_id=drop.id)
            await dropfile.update_hash(conn)
            token = self.auth.make_user_jwt(u)
            resp = await self._upload_chunk(
                os.urandom(100),
                {
                    "Authorization": f"bearer {token}",
                    "Chunk-Number": 2,
                    "Chunk-Size": 100,
                    "File-Total-Size": 200,
                    "Drop-Hash": drop.hash,
                    "Drop-File-Hash": dropfile.hash,
                },
            )
            self.assertValidationError(resp, "Chunk-Number", 422)


class DropUploadBlobHandlerTest(TestMixin):
    @gen_test
    async def test_when_user_authenticated_then_dropfile_created(self):
        async with self._app.pg.acquire() as conn:
            file_path = os.path.join(
                os.path.dirname(__file__), "fixtures", "python-logo.png"
            )
            with open(file_path, "rb") as f:
                data = f.read()
                u = await factories.UserFactory(conn=conn)
                prepare = requests.Request(
                    url="http://localhost/img", files={"blob": (BytesIO(data))}, data={}
                ).prepare()
                jwt = self.auth.make_user_jwt(u)
                response = await self.fetch(
                    "/api/drops/upload/blob",
                    headers={
                        "Authorization": f"bearer {jwt}",
                        "Content-Type": prepare.headers.get("Content-Type"),
                    },
                    method="POST",
                    body=prepare.body,
                )
                if response.body:
                    response._body = json.loads(response._body)
                assert "drop_file_hash" in response.body
                assert "drop_hash" in response.body
                assert "url" in response.body
                assert response.code == 201
                drop_file = await models.DropFile.select(
                    conn,
                    and_(
                        models.DropFile.c.hash == response.body["drop_file_hash"],
                        models.Drop.c.hash == response.body["drop_hash"],
                    ),
                )
                assert drop_file is not None
                assert drop_file.mimetype == "image/png"
                obj = drop_file.get_from_storage(self.storage)
                assert obj is not None
                drop_file_data = obj.read()
                assert drop_file_data == data

    @gen_test
    async def test_when_user_unauthenticated_then_401_returned(self):
        file_path = os.path.join(
            os.path.dirname(__file__), "fixtures", "python-logo.png"
        )
        with open(file_path, "rb") as f:
            data = f.read()
            prepare = requests.Request(
                url="http://localhost/img", files={"blob": (BytesIO(data))}, data={}
            ).prepare()
            response = await self.fetch(
                "/api/drops/upload/blob",
                headers={
                    "Authorization": "bearer blablae",
                    "Content-Type": prepare.headers.get("Content-Type"),
                },
                method="POST",
                body=prepare.body,
            )
        self.assertValidationError(
            response, "Authorization", errors.validation.VoblaJWTAuthError.code
        )


class TestSharexUploader(TestMixin):
    @gen_test
    async def test_when_user_authenticated_then_sharex_data_returned(self):
        async with self._app.pg.acquire() as conn:
            u = await factories.UserFactory(conn=conn)
            token = self.auth.make_user_jwt(u)
        resp = await self.fetch(
            "/api/sharex", method="GET", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.code == 200
        assert json.loads(resp.body) == {
            "Name": "vobla",
            "DestinationType": "ImageUploader",
            "RequestURL": "https://vobla.olegshigor.in/api/drops/upload/blob",
            "FileFormName": "blob",
            "Headers": {"Authorization": f"Bearer {token}"},
            "URL": "https://vobla.olegshigor.in/f/$json:drop_file_hash$",
        }

    @gen_test
    async def test_when_user_unauthenticated_then_401_returned(self):
        resp = await self.fetch("/api/sharex", method="GET")
        assert resp.code == 401
