from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi_sqlalchemy.exceptions import MissingSessionError, SessionNotInitialisedError

db_url = "sqlite+aiosqlite://"


@pytest.mark.anyio
async def test_init(app, AsyncDBSessionMiddleware):
    mw = AsyncDBSessionMiddleware(app, db_url=db_url)
    assert isinstance(mw, BaseHTTPMiddleware)


@pytest.mark.anyio
async def test_init_required_args(app, AsyncDBSessionMiddleware):
    with pytest.raises(ValueError) as exc_info:
        AsyncDBSessionMiddleware(app)

    assert exc_info.value.args[0] == "You need to pass a db_url or a custom_engine parameter."


@pytest.mark.anyio
async def test_init_required_args_custom_engine(app, async_db, AsyncDBSessionMiddleware):
    custom_engine = create_engine(db_url)
    AsyncDBSessionMiddleware(app, custom_engine=custom_engine)


@pytest.mark.anyio
async def test_init_correct_optional_args(app, async_db, AsyncDBSessionMiddleware):
    engine_args = {"echo": True}
    session_args = {"autoflush": False}

    AsyncDBSessionMiddleware(app, db_url, engine_args=engine_args, session_args=session_args)

    async with async_db():
        assert not async_db.session.autoflush

        engine = async_db.session.bind
        assert engine.echo


@pytest.mark.anyio
async def test_init_incorrect_optional_args(app, AsyncDBSessionMiddleware):
    with pytest.raises(TypeError) as exc_info:
        AsyncDBSessionMiddleware(app, db_url=db_url, invalid_args="test")

    assert exc_info.value.args[0] == "AsyncDBSessionMiddleware.__init__() got an unexpected keyword argument 'invalid_args'"


@pytest.mark.anyio
async def test_inside_route(app, async_client, async_db, AsyncDBSessionMiddleware):
    app.add_middleware(AsyncDBSessionMiddleware, db_url=db_url)

    @app.get("/")
    async def test_get():
        assert isinstance(async_db.session, AsyncSession)

    await async_client.get("/")


@pytest.mark.anyio
async def test_inside_route_without_middleware_fails(app, async_client, async_db):
    @app.get("/")
    async def test_get():
        with pytest.raises(SessionNotInitialisedError):
            async_db.session

    await async_client.get("/")


@pytest.mark.anyio
async def test_outside_of_route(app, async_db, AsyncDBSessionMiddleware):
    app.add_middleware(AsyncDBSessionMiddleware, db_url=db_url)

    async with async_db():
        assert isinstance(async_db.session, AsyncSession)


@pytest.mark.anyio
async def test_outside_of_route_without_middleware_fails(async_db):
    with pytest.raises(SessionNotInitialisedError):
        async_db.session

    with pytest.raises(SessionNotInitialisedError):
        async with async_db():
            pass


@pytest.mark.anyio
async def test_outside_of_route_without_context_fails(app, async_db, AsyncDBSessionMiddleware):
    app.add_middleware(AsyncDBSessionMiddleware, db_url=db_url)

    with pytest.raises(MissingSessionError):
        async_db.session


@pytest.mark.anyio
async def test_db_context_temporary_session_args(app, async_db, AsyncDBSessionMiddleware):
    app.add_middleware(AsyncDBSessionMiddleware, db_url=db_url)

    session_args = {}
    async with async_db(session_args=session_args):
        assert isinstance(async_db.session, AsyncSession)

    session_args = {"autoflush": False}
    async with async_db(session_args=session_args):
        assert not async_db.session.autoflush


@pytest.mark.anyio
async def test_rollback(app, async_db, AsyncDBSessionMiddleware):
    app.add_middleware(AsyncDBSessionMiddleware, db_url=db_url)

    with pytest.raises(Exception):
        async with async_db():
            raise Exception


@pytest.mark.anyio
@pytest.mark.parametrize("commit_on_exit", [True, False])
async def test_commit_on_exit(app, async_client, async_db, AsyncDBSessionMiddleware, commit_on_exit):

    with patch("fastapi_sqlalchemy.async_middleware._session") as session_var:

        mock_session = AsyncMock()
        session_var.get.return_value = mock_session

        app.add_middleware(AsyncDBSessionMiddleware, db_url=db_url, commit_on_exit=commit_on_exit)

        @app.get("/")
        async def test_get():
            pass

        await async_client.get("/")

        assert mock_session.commit.called == commit_on_exit
