import uuid

from sqlalchemy import select
from sqlalchemy import func

from vobla.db import models


async def get_user_storage_size(pgc, user_id: uuid.UUID) -> int:
    query = (
        select(
            [
                func.sum(models.DropFile.t.size)
            ]
        ).select_from(
            models.Drop.t.join(
                models.DropFile.t,
                models.DropFile.c.drop_id == models.Drop.c.id
            )
        ).where(
            models.Drop.c.owner_id == user_id
        )
    )
    cursor = await pgc.execute(query)
    storage_size = await cursor.scalar()
    return storage_size
