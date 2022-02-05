import asyncio
import json

import psycopg2
import tornado.ioloop
import tornado.platform.asyncio
from sqlalchemy.schema import CreateTable, DropTable
from sqlalchemy.ext.compiler import compiles
from tornado.httpclient import AsyncHTTPClient
from tornado.testing import AsyncHTTPTestCase

from vobla.app import TornadoApplication
from vobla.db import metadata


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"


class TestMixin(AsyncHTTPTestCase):

    async def recreate_tables(self):
        async with self.pg.acquire() as conn:
            for table in metadata.tables.values():
                drop_expr = DropTable(table)
                try:
                    await conn.execute(drop_expr)
                except psycopg2.ProgrammingError:
                    pass
        async with self.pg.acquire() as conn:
            for table in metadata.tables.values():
                create_expr = CreateTable(table)
                await conn.execute(create_expr)

    @classmethod
    def setUpClass(cls):
        super(TestMixin, cls).setUpClass()

    def setUp(self):
        super(TestMixin, self).setUp()
        self.pg = self._app.pg
        self.storage = self._app.storage
        self.auth = self._app.auth
        asyncio.get_event_loop().run_until_complete(self.recreate_tables())

    def get_new_ioloop(self):
        io_loop = tornado.platform.asyncio.AsyncIOLoop()
        asyncio.set_event_loop(io_loop.asyncio_loop)
        return io_loop

    def get_app(self):
        return TornadoApplication()

    async def fetch(self, url, *ar, **kw):
        client = AsyncHTTPClient(self.io_loop)
        if 'raise_error' not in kw:
            kw['raise_error'] = False
        resp = await client.fetch(self.get_url(url), *ar, **kw)
        return resp

    async def fetch_json(self, url, *ar, **kw):
        if 'body' in kw:
            kw['body'] = json.dumps(kw['body'])
            if 'headers' not in kw:
                kw['headers'] = {}
            kw['headers']['Content-Type'] = 'application/json'
            kw['headers']['Accept'] = 'application/json'
        resp = await self.fetch(url, *ar, **kw)
        resp._body = json.loads(resp.body)
        return resp

    @staticmethod
    def assertValidationError(resp, nonvalidated_fields, code=422):
        assert resp.code == code
        body = resp.body
        if isinstance(body, bytes):
            body = json.loads(body)
        assert 'error' in body
        assert 'fields' in body['error']
        if isinstance(nonvalidated_fields, list):
            for field in nonvalidated_fields:
                assert field in body['error']['fields']
        else:
            assert nonvalidated_fields in body['error']['fields']
