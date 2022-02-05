import weakref

import sqlalchemy as sa
import aiopg.sa.exc

from vobla.db import metadata


class ModelMeta(type):
    def __init__(cls, name, bases, nmspc):
        super(ModelMeta, cls).__init__(name, bases, nmspc)
        if hasattr(cls, "schema") is False:
            raise Exception("You should declare the model's schema!")
        table_name = getattr(cls, "__tablename__", name.lower())
        cls.table = sa.Table(table_name, metadata, *cls.schema)
        cls.t = weakref.proxy(cls.table)
        cls.c = weakref.proxy(cls.table.c)


class MultimethodDescriptor(object):
    """
    Descriptor which allows an usage of the
    same name for class and instance methods
    """

    def __init__(self, cls_m_name, inst_m_name):
        self.cls_m_name = cls_m_name
        self.inst_m_name = inst_m_name

    def __get__(self, inst, cls):
        if inst is None:
            return getattr(cls, self.cls_m_name)
        else:
            return getattr(inst, self.inst_m_name)


class Model(object, metaclass=ModelMeta):

    schema = []

    def __init__(self, *args, **kwargs):
        for column_name, column_value in kwargs.items():
            if column_name in self.c.keys():
                setattr(self, column_name, column_value)

    @classmethod
    def _construct_from_row(cls, row):
        if row:
            obj = cls()
            for column_name, column_val in row.items():
                setattr(obj, column_name, column_val)
            return obj
        else:
            return None

    def _update_from_row(self, row):
        for column_name, column_val in row.items():
            setattr(self, column_name, column_val)

    @classmethod
    async def fetchone(cls, pgc, query):
        cursor = await pgc.execute(query)
        res = await cursor.fetchone()
        return cls._construct_from_row(res)

    @classmethod
    async def fetchall(cls, pgc, query):
        cursor = await pgc.execute(query)
        res = await cursor.fetchall()
        return [cls._construct_from_row(row) for row in res]

    @classmethod
    async def fetchmany(cls, pgc, query, size):
        while True:
            cursor = await pgc.execute(query)
            res = await cls.cursor.fetchmany(query, size)
            res = [cls._construct_from_row(row) for row in res]
            if not cursor:
                break
            yield res
        yield res

    @classmethod
    async def _class_delete(cls, pgc, query):
        await pgc.execute(cls.t.delete().where(query))

    async def _instance_delete(self, pgc, query):
        await pgc.execute(self.t.delete().where(self.c.id == self.id))

    delete = MultimethodDescriptor("_class_delete", "_instance_delete")

    @classmethod
    async def select(cls, pgc, query, *ar, return_list=False):
        cursor = await pgc.execute(cls.t.select().where(query))
        if cursor.rowcount > 1:
            res = await cursor.fetchall()
            return [cls._construct_from_row(row) for row in res]
        elif cursor.rowcount == 1:
            res = await cursor.fetchone()
            obj = cls._construct_from_row(res)
            return [obj] if return_list else obj
        else:
            return [] if return_list else None

    @classmethod
    async def _class_insert(cls, pgc, values, returning=None):
        obj = cls._construct_from_row(values)
        query = cls.t.insert().values(values)
        if returning:
            returning.append(cls.c.id)
            query = query.returning(*returning)
        cursor = await pgc.execute(query)
        try:
            row = await cursor.fetchone()
            obj._update_from_row(row)
        except aiopg.sa.exc.ResourceClosedError:
            pass
        return obj

    async def _instance_insert(self, pgc, returning=None):
        values = {
            column: getattr(self, column)
            for column in self.c.keys()
            if hasattr(self, column)
        }
        query = self.t.insert(values)
        if returning:
            returning.append(self.c.id)
            query = query.returning(*returning)
        cursor = await pgc.execute(query)
        res = await cursor.fetchone()
        self._update_from_row(res)

    insert = MultimethodDescriptor("_class_insert", "_instance_insert")

    @classmethod
    async def _class_update(cls, pgc, id, values, returning=None):
        query = cls.t.update().where(cls.c.id == id).values(values)
        if returning:
            returning.append(cls.c.id)
            query = query.returning(*returning)
        cursor = await pgc.execute(query)
        row = await cursor.fetchone()
        return cls._construct_from_row(row)

    async def _instance_update(self, pgc, returning=None):
        values = {
            column: getattr(self, column)
            for column in self.c.keys()
            if hasattr(self, column)
        }
        query = self.t.update().where(self.c.id == values.pop("id")).values(values)
        if returning:
            returning.append(self.c.id)
            query = query.returning(*returning)
        await pgc.execute(query)

    update = MultimethodDescriptor("_class_update", "_instance_update")
