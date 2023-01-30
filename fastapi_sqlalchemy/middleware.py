from contextvars import ContextVar
from typing import Dict, Optional, Union

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import Session, sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp

from fastapi_sqlalchemy.exceptions import MissingSessionError, SessionNotInitialisedError

_Session: sessionmaker = None
_session: ContextVar[Optional[Session]] = ContextVar("_session", default=None)


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        db_url: Optional[Union[str, URL]] = None,
        custom_engine: Optional[Engine] = None,
        engine_args: Dict = None,
        session_args: Dict = None,
        commit_on_exit: bool = False,
        rollback_on_client_error: bool = False,
        rollback_on_server_error: bool = False,
    ):
        """Initialize middleware.

        Args:
            rollback_on_client_error:
                Fastapi does handle http client errors
                (see https://httpwg.org/specs/rfc9110.html#status.4xx)
                and returns a valid response without raising inside
                the `DBSessionMiddleware.dispatch` method.
                If `rollback_on_client_errors` is true the session
                gets rolledback even if no Exception is raised inside
                the contextmanager.
            rollback_on_server_error:
                See above `rollback_on_client_error`. The session
                is rolled back on 5xx HTTP-Codes
                (https://httpwg.org/specs/rfc9110.html#status.5xx).
        """
        super().__init__(app)
        global _Session
        engine_args = engine_args or {}
        self.commit_on_exit = commit_on_exit
        self.rollback_on_client_error = rollback_on_client_error
        self.rollback_on_server_error = rollback_on_server_error

        session_args = session_args or {}

        if not custom_engine and not db_url:
            raise ValueError("You need to pass a db_url or a custom_engine parameter.")
        if not custom_engine:
            engine = create_engine(db_url, **engine_args)
        else:
            engine = custom_engine
        _Session = sessionmaker(bind=engine, **session_args)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        with db(commit_on_exit=self.commit_on_exit) as dbsession_context:
            response = await call_next(request)

            if response and hasattr(response, "status_code") and response.status_code:
                # I am not deep enough in fastapi. In allmost all cases
                # status_code should be int. It may be possible that third
                # party usage of custom HTTPException could set status codes
                # as strings.
                status_code = int(response.status_code)
                is_client_error = status_code >= 400 and status_code < 500
                is_server_error = status_code >= 500

                if is_client_error and self.rollback_on_client_error:
                    dbsession_context.force_rollback = True

                if is_server_error and self.rollback_on_server_error:
                    dbsession_context.force_rollback = True

        return response


class DBSessionMeta(type):
    # using this metaclass means that we can access db.session as a property at a class level,
    # rather than db().session
    @property
    def session(self) -> Session:
        """Return an instance of Session local to the current async context."""
        if _Session is None:
            raise SessionNotInitialisedError

        session = _session.get()
        if session is None:
            raise MissingSessionError

        return session


class DBSession(metaclass=DBSessionMeta):
    def __init__(self, session_args: Dict = None, commit_on_exit: bool = False):
        self.token = None
        self.session_args = session_args or {}
        self.commit_on_exit = commit_on_exit

        # The code using this context could signal that
        # the session should rolled back in case of
        # conditions or errors which are not raised
        # but handled internally.
        self.force_rollback = False

    def __enter__(self):
        if not isinstance(_Session, sessionmaker):
            raise SessionNotInitialisedError
        self.token = _session.set(_Session(**self.session_args))
        # We return `self` here to make the context
        # available to inner code for enabling `force_rollback`
        # on the session.
        # Before this change the return value was `type(self)`.
        # In allmost all examples the return was not used
        # and this refactoring should not break existing code.
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sess = _session.get()

        is_rolled_back = False

        if exc_type is not None:
            sess.rollback()
            is_rolled_back = True

        if self.force_rollback and not is_rolled_back:
            sess.rollback()
            is_rolled_back = True

        if self.commit_on_exit and not is_rolled_back:
            sess.commit()

        sess.close()
        _session.reset(self.token)


db: DBSessionMeta = DBSession
