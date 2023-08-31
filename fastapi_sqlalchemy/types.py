from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Coroutine, List, Optional, Self, Union, overload

from curio.meta import from_coroutine
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta as DeclarativeMeta_
from sqlalchemy.orm import Query, Session, aliased
from sqlalchemy.sql import ColumnExpressionArgument

from .decorators import awaitable


class ModelBase(object):
    query: Query
    session: Session | AsyncSession

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        if isinstance(obj.db.session, AsyncSession):
            obj.query = cls.db.sync_session.query(cls)
        else:
            obj.query = cls.db.session.query(cls)
        return obj

    @property
    def session(self) -> Session | AsyncSession:
        return self.db.session

    async def new(cls, **kwargs) -> Self:
        obj: Self = cls(**kwargs)
        await obj.save()
        return obj

    @classmethod
    @awaitable(new)
    def new(cls: Self, **kwargs) -> Union[Coroutine[Any, Any, Self], Self]:
        obj: Self = cls(**kwargs)
        obj.save()
        return obj

    async def get_all(cls, *criterion: ColumnExpressionArgument[bool], **kwargs: Any) -> List[Self]:
        if criterion:
            stmt = select(cls).filter(*criterion)
        else:
            stmt = select(cls).filter_by(**kwargs)
        result = await cls.session.execute(stmt)
        objs = result.scalars().all()
        return objs

    @classmethod
    @awaitable(get_all)
    def get_all(
        cls, *criterion: ColumnExpressionArgument[bool], **kwargs: Any
    ) -> Union[List[Self], Coroutine[Any, Any, List[Self]]]:
        if criterion:
            lst: List[Self] = cls.query.filter(*criterion, **kwargs).all()
        else:
            lst: List[Self] = cls.query.filter_by(**kwargs).all()
        return lst

    async def get(cls, *criterion: ColumnExpressionArgument[bool], **kwargs: Any) -> Self:
        if criterion:
            result = await cls.session.execute(select(cls).filter(*criterion))
        else:
            result = await cls.session.execute(select(cls).filter_by(**kwargs))
        return result.scalars().first()

    @classmethod
    @awaitable(get)
    def get(
        cls, *criterion: ColumnExpressionArgument[bool], **kwargs: Any
    ) -> Union[Coroutine[Any, Any, Self], Self]:
        if criterion:
            return cls.query.filter(*criterion, **kwargs).first()
        return cls.query.filter_by(**kwargs).first()

    async def save(self) -> None:
        t_e = self.session.sync_session.expire_on_commit
        self.session.sync_session.expire_on_commit = False
        self.session.add(self)
        await self.session.commit()
        self.session.sync_session.expire_on_commit = t_e

    @awaitable(save)
    def save(self) -> None:
        self.session.add(self)
        self.session.commit()

    async def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        await self.save()

    @awaitable(update)
    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.save()

    async def delete(self):
        await self.session.delete(self)
        await self.session.commit()

    @awaitable(delete)
    def delete(self):
        self.session.delete(self)
        self.session.commit()
