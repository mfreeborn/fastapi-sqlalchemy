from __future__ import annotations

from contextlib import ExitStack
from contextvars import ContextVar
from typing import Dict, List, Optional, Union

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import DeclarativeMeta, Session, sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp

from .exceptions import (
    DBSessionType,
    MissingSessionError,
    SessionNotInitialisedError,
    SQLAlchemyType,
)
from .extensions import SQLAlchemy
from .extensions import db as db_


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        db: Optional[Union[List[SQLAlchemy], SQLAlchemy]] = None,
        db_url: Optional[URL] = None,
        **options,  # this is just for compatibility with the old version of the middleware.
    ):
        super().__init__(app)
        if not (type(db) == list or type(db) == SQLAlchemy) and not db_url:
            raise SQLAlchemyType()
        if db_url and not db:
            global db_
            if not db_.initiated:
                db_.init(url=db_url, **options)
            self.dbs = [db_]
        if type(db) == SQLAlchemy:
            self.dbs = [
                db,
            ]
        elif type(db) == list:
            self.dbs = db

        for db in self.dbs:
            db.create_all()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        with ExitStack() as stack:
            contexts = [stack.enter_context(ctx) for ctx in self.dbs]
            response = await call_next(request)
        return response
