import aiopg.sa

from vobla.settings import config


def get_engine_params():
    return dict(
        host=config["postgres"]["host"],
        port=config["postgres"]["port"],
        database=config["postgres"]["db"],
        user=config["postgres"]["user"],
        password=config["postgres"]["password"],
    )


async def create_engine(loop):
    eng = await aiopg.sa.create_engine(loop=loop, **get_engine_params())
    return eng
