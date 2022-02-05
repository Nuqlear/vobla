import asyncio
import pyssdb

import tornado.web
import tornado.ioloop

from vobla.settings import config
from vobla.urls import url_patterns
from vobla.db.engine import create_engine
from vobla.storage import  get_storage


class TornadoApplication(tornado.web.Application):
    async def init_pg(self):
        self.pg = await create_engine(tornado.ioloop.IOLoop.current().asyncio_loop)
        # is pg shutdowning properly?

    def __init__(self):
        asyncio.get_event_loop().run_until_complete(self.init_pg())
        self.ssdb = pyssdb.Client(
            host=config["ssdb"]["host"], port=int(config["ssdb"]["port"])
        )
        self.storage = get_storage()
        tornado.web.Application.__init__(self, url_patterns, **config["tornado"])
