from vobla.db import models
from vobla.db.querysets import get_user_storage_size


async def check_drop_file_allowed(pgc, user: models.User, drop_file_size: int):
    user_tier = await models.UserTier.select(
        pgc, models.UserTier.c.id == user.user_tier_id
    )
    user_storage_size = await get_user_storage_size(pgc, user.id)

    if user_tier.max_drop_file_size and drop_file_size > user_tier.max_drop_file_size:
        raise Exception

    if (
        user_tier.max_storage_size
        and user_storage_size + drop_file_size > user_tier.max_storage_size
    ):
        raise Exception
