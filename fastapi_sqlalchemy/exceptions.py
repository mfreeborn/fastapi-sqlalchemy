from typing import List


class MissingSessionError(Exception):
    """Excetion raised for when the user tries to access a database session before it is created."""

    def __init__(self):
        msg = """
        No session found! Either you are not currently in a request context,
        or you need to manually create a session context by using a `db` instance as
        a context manager e.g.:

        with db():
            db.session.query(User).all()
        """

        super().__init__(msg)


class SessionNotInitialisedError(Exception):
    """Exception raised when the user creates a new DB session without first initialising it."""

    def __init__(self):
        msg = """
        Session not initialised! Ensure that DBSessionMiddleware has been initialised before
        attempting database access.
        """

        super().__init__(msg)


class SessionNotAsync(TypeError):
    """Exception raised when the user calls sync_session from within a synchronous function."""

    def __init__(self):
        msg = """
        Session not async! Ensure that you are calling sync_session from within an asynchronous function.
        """
        super().__init__(msg)


class DBSessionType(TypeError):
    """Exception raised when the user passes an object to DBSessionMiddleware that is not of DBSession or List[DBSession] type."""

    def __init__(self):
        msg = """
        Middleware not initialised! Ensure that db is of type DBSession or List[DBSession].
        """

        super().__init__(msg)


class SQLAlchemyType(TypeError):
    """Exception raised when the user passes an object to DBSessionMiddleware that is not of SQLAlchemy or List[SQLAlchemy] or URL type."""

    def __init__(self):
        msg = """
        Middleware not initialized! Ensure that db is of type SQLAlchemy or List[SQLAlchemy] or URL.
        """

        super().__init__(msg)


class NonTableQuery(TypeError):
    """Exception raised when the user attempts to call .query on a non-table object."""

    def __init__(self):
        msg = """
        Non-table object! Ensure that the object you are querying is a table.
        """

        super().__init__(msg)


class SQLAlchemyAsyncioMissing(ImportError):
    """Exception raised when the user attempts to use the async_ parameter without installing SQLAlchemy-Asyncio."""

    def __init__(self, missing: str = "sqlalchemy.ext.asyncio"):
        if "sqlalchemy.ext.asyncio" not in missing:
            missing = "sqlalchemy.ext.asyncio" + str(
                missing if missing[0] == "." else "." + missing
            )

        msg = """
        {package} is missing, please install using 'pip install sqlalchemy[asyncio]' or set async_ = False when initializing fastapi_sqlalchemy.SQLAlchemy.
        """.format(
            package=missing
        )

        super().__init__(msg)


class BuiltinNonExistent(AttributeError):
    """Exception raised when the user attempts to map a builtin property that does not exist."""

    def __init__(self, prop: str):
        msg = f"""Builtin {prop} does not exist!"""

        super().__init__(msg)


class TooManyBuiltinOverrides(AttributeError):
    """Exception raised when the user attempts to map a builtin property that does not exist."""

    def __init__(self, prop: str):
        msg = f"""Too many builtin overrides! Strict maximum of 1 builtin override per model."""

        super().__init__(msg)
