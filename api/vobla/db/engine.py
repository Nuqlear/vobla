import aiopg.sa

from vobla.settings import config


async def create_engine(loop):
    eng = await aiopg.sa.create_engine(
        host=config['postgres']['host'],
        port=config['postgres']['port'],
        database=config['postgres']['db'],
        user=config['postgres']['user'],
        password=config['postgres']['password'],
        loop=loop
    )
    return eng
