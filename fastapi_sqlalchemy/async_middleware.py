from contextvars import ContextVar
from typing import Dict, Optional, Union

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp

from fastapi_sqlalchemy.exceptions import (
    MissingSessionError, SessionNotInitialisedError
)

_Session: sessionmaker = None
_session: ContextVar[Optional[AsyncSession]] = ContextVar("_session", default=None)


class AsyncDBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        db_url: Optional[Union[str, URL]] = None,
        custom_engine: Optional[AsyncEngine] = None,
        engine_args: Dict = None,
        session_args: Dict = None,
        commit_on_exit: bool = False,
    ):
        super().__init__(app)
        global _Session
        engine_args = engine_args or {}
        self.commit_on_exit = commit_on_exit

        session_args = session_args or {}
        if not custom_engine and not db_url:
            raise ValueError("You need to pass a db_url or a custom_engine parameter.")
        if not custom_engine:
            engine = create_async_engine(db_url, future=True, **engine_args)
        else:
            engine = custom_engine
        _Session = sessionmaker(bind=engine, class_=AsyncSession, **session_args)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        async with async_db(commit_on_exit=self.commit_on_exit):
            response = await call_next(request)
        return response


class AsyncDBSessionMeta(type):
    # using this metaclass means that we can access db.session as a property at a class level,
    # rather than db().session
    @property
    def session(self) -> AsyncSession:
        """Return an instance of Session local to the current async context."""
        if _Session is None:
            raise SessionNotInitialisedError

        session = _session.get()
        if session is None:
            raise MissingSessionError

        return session


class AsyncDBSession(metaclass=AsyncDBSessionMeta):
    def __init__(self, session_args: Dict = None, commit_on_exit: bool = False):
        self.token = None
        self.session_args = session_args or {}
        self.commit_on_exit = commit_on_exit

    async def __aenter__(self):
        if not isinstance(_Session, sessionmaker):
            raise SessionNotInitialisedError
        self.token = _session.set(_Session(**self.session_args))
        return type(self)

    async def __aexit__(self, exc_type, exc_value, traceback):
        sess = _session.get()
        if exc_type is not None:
            await sess.rollback()

        if self.commit_on_exit:
            await sess.commit()

        await sess.close()
        _session.reset(self.token)


async_db: AsyncDBSessionMeta = AsyncDBSession
