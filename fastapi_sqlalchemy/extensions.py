from __future__ import annotations

from contextlib import ExitStack
from contextvars import ContextVar
from typing import Dict, List, Optional, Type, Union

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import DeclarativeMeta as DeclarativeMeta_
from sqlalchemy.orm import Query, Session, declarative_base, sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp

from .exceptions import (
    DBSessionType,
    MissingSessionError,
    NonTableQuery,
    SessionNotInitialisedError,
)


class SQLAlchemy:
    def __init__(
        self,
        url: Optional[URL] = None,
        custom_engine: Optional[Engine] = None,
        engine_args: Dict = None,
        session_args: Dict = None,
        commit_on_exit: bool = False,
    ):
        self.initiated = False
        self._Base: Type[DeclarativeMeta] = declarative_base(metaclass=DeclarativeMeta)
        setattr(self.Base, "db", self)
        self._session = ContextVar("_session", default=None)
        self.session_maker: sessionmaker = None
        if not url:
            pass
        else:
            return self.init(url, custom_engine, engine_args, session_args, commit_on_exit)

    @property
    def Base(self) -> Type[DeclarativeMeta]:
        return self._Base

    def init(
        self,
        url: Optional[URL] = None,
        custom_engine: Optional[Engine] = None,
        engine_args: Dict = None,
        session_args: Dict = None,
        commit_on_exit: bool = False,
    ) -> None:
        self.url = url
        self.custom_engine = custom_engine
        self.engine_args = engine_args or {}
        self.session_args = session_args or {}
        self.commit_on_exit = commit_on_exit

        # setattr(self.Base, "session", self.session)
        if not self.custom_engine and not self.url:
            raise ValueError("You need to pass a url or a custom_engine parameter.")
        if not self.custom_engine:
            self.engine = create_engine(self.url, **self.engine_args)
        else:
            self.engine = self.custom_engine
        self.session_maker = sessionmaker(bind=self.engine, **self.session_args)

        self.initiated = True

    def create_all(self):
        self.Base.metadata.create_all(self.engine)
        return None

    @property
    def session(self) -> Session:
        if self._session is None:
            raise SessionNotInitialisedError
        session = self._session.get()
        if session is None:
            raise MissingSessionError
        return session

    def __call__(self) -> SQLAlchemy:
        """This is just for compatibility with the old API"""
        return self

    def __enter__(self):
        if not isinstance(self.session_maker, sessionmaker):
            raise SessionNotInitialisedError
        self.token = self._session.set(self.session_maker(**self.session_args))
        return type(self)

    def __exit__(self, exc_type, exc_value, traceback):
        sess = self.session
        if exc_type is not None:
            sess.rollback()

        if self.commit_on_exit:
            sess.commit()

        sess.close()
        self._session.reset(self.token)


class DeclarativeMeta(DeclarativeMeta_):
    db: SQLAlchemy

    @property
    def session(self):
        return self.db.session

    @property
    def query(self) -> Query:
        return self.db.session.query(self)


db: SQLAlchemy = (
    SQLAlchemy()
)  # this is just for compatibility with the old version of the middleware.
