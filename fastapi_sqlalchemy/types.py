from typing import overload

from sqlalchemy.orm import DeclarativeMeta as DeclarativeMeta_
from sqlalchemy.orm import Query, Session


class ModelBase(object):
    query: Query
    session: Session

    def save(self) -> None:
        self.db.session.add(self)
        self.db.session.commit()
        return None

    def update(self, commit=True, **kwargs) -> None:
        for attr, value in kwargs.items():
            if attr in self.__dict__.keys():
                setattr(self, attr, value)
        if commit:
            self.save()
        return None
