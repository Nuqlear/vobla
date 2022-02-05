import uuid

from sqlalchemy import select
from sqlalchemy import and_
from sqlalchemy import func

from vobla.db import models


async def get_user_storage_size(pgc, user_id: uuid.UUID) -> int:
    query = (
        select(
            [
                func.sum(models.DropFile.c.size)
            ]
        ).select_from(
            models.Drop.t.join(
                # for some reason weakref doesnt work here
                models.DropFile.table,
                onclause=and_(
                    models.DropFile.c.drop_id == models.Drop.c.id,
                    models.Drop.c.owner_id == user_id
                )
            )
        )
    )
    cursor = await pgc.execute(query)
    storage_size = await cursor.scalar()
    storage_size = storage_size or 0
    return storage_size
