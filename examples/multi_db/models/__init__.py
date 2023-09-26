import inspect
from typing import Dict, List

from sqlalchemy import Column

from fastapi_sqlalchemy import ModelBase


class BaseModel(ModelBase):
    @classmethod
    def new(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()
        return obj

    @classmethod
    def get(cls, **kwargs):
        result: cls = cls.query.filter_by(**kwargs).first()
        return result

    @classmethod
    def get_all(cls, **kwargs):
        result: List[cls] = cls.query.filter_by(**kwargs).all()
        return result

    def update(self, **kwargs):
        for column, value in kwargs.items():
            setattr(self, column, value)

        self.save()
        return self

    def __repr__(self):
        try:
            columns = dict(
                (column.name, getattr(self, column.name)) for column in self.__table__.columns
            )

        except:
            o = {}
            members = inspect.getmembers(self)
            for name, obj in members:
                if type(obj) == Column:
                    o[name] = obj
            columns = o

        column_strings = []
        for column, value in columns.items():
            column_strings.append(f"{column}: {value}")

        repr = f"<{self.__class__.__name__} {', '.join(column_strings)}>"
        return repr
