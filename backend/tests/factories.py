import uuid
import datetime

import factory
import factory.fuzzy

from vobla.db import models


class BaseAsyncFactory(factory.Factory):
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        async def create_coro(*args, **kwargs):
            conn = kwargs.pop("conn")
            return await model_class.insert(conn, kwargs)

        return create_coro(*args, **kwargs)


class UserFactory(BaseAsyncFactory):
    user_tier_id = "super"
    email = factory.fuzzy.FuzzyText()
    password_hash = factory.fuzzy.FuzzyText()
    active_session_hash = factory.fuzzy.FuzzyText()

    class Meta:
        model = models.User


class UserTierFactory(BaseAsyncFactory):
    id = "super"
    name = factory.fuzzy.FuzzyText()
    max_drop_file_size = None
    max_storage_size = None

    class Meta:
        model = models.User


class DropFactory(BaseAsyncFactory):
    name = factory.fuzzy.FuzzyText()
    owner_id = factory.LazyFunction(uuid.uuid4)
    hash = factory.fuzzy.FuzzyText()
    created_at = factory.LazyFunction(datetime.datetime.utcnow)
    is_preview_ready = False

    class Meta:
        model = models.Drop


class DropFileFactory(BaseAsyncFactory):
    name = factory.fuzzy.FuzzyText()
    drop_id = factory.LazyFunction(uuid.uuid4)
    hash = factory.fuzzy.FuzzyText()
    mimetype = factory.fuzzy.FuzzyText()
    size = factory.fuzzy.FuzzyInteger(0, 10000)
    created_at = factory.LazyFunction(datetime.datetime.utcnow)
    uploaded_at = factory.LazyFunction(datetime.datetime.utcnow)

    class Meta:
        model = models.DropFile
