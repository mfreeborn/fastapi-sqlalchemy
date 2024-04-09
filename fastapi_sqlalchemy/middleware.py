from __future__ import annotations

import asyncio
import inspect
import logging
from contextlib import AsyncExitStack, ExitStack
from typing import Dict, List, Optional, Union

from curio.meta import from_coroutine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp

from .exceptions import SQLAlchemyType
from .extensions import SQLAlchemy
from .extensions import db as db_
from .extensions import reset_session, start_session


class DBStateMap:
    def __init__(self):
        self.dbs: Dict[URL, sessionmaker] = {}
        self.initialized = False

    def __getitem__(self, item: URL) -> sessionmaker:
        return self.dbs[item]

    def __setitem__(self, key: URL, value: sessionmaker) -> None:
        if not self.initialized:
            self.dbs[key] = value
        else:
            raise ValueError("DBStateMap is already initialized")


def is_async():
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        db: Optional[Union[List[SQLAlchemy], SQLAlchemy]] = None,
        db_url: Optional[URL] = None,
        **options,
    ):
        super().__init__(app)
        self.state_map = DBStateMap()
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
        req_async = False
        try:
            for route in self.app.app.app.routes:
                if route.path == request.scope["path"]:
                    req_async = inspect.iscoroutinefunction(route.endpoint)
        except:
            req_async = False
        token = start_session()
        exception = None
        async with AsyncExitStack() as async_stack:
            with ExitStack() as sync_stack:
                contexts = [
                    await async_stack.enter_async_context(ctx())
                    for ctx in self.dbs
                    if ctx.async_ and req_async
                ]
                contexts.extend([sync_stack.enter_context(ctx()) for ctx in self.dbs])
                try:
                    response = await call_next(request)
                except Exception as e:
                    exception = e
                    for db in self.dbs:
                        db.session.rollback()

        if exception:
            raise exception

        reset_session(token)
        return response

        # if req_async:
        #     return dispatch_inner()
        # else:
        #     with ExitStack() as stack:
        #         contexts = [stack.enter_context(ctx()) for ctx in self.dbs]
        #         response = call_next(request)
        # return response
