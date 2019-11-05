import pytest
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi_sqlalchemy.exceptions import MissingSessionError

db_url = "sqlite://"


def test_init(app):
    mw = DBSessionMiddleware(app, db_url=db_url)
    assert isinstance(mw, BaseHTTPMiddleware)


def test_init_required_args(app):
    with pytest.raises(TypeError) as exc_info:
        DBSessionMiddleware(app)

    assert exc_info.value.args[0] == "__init__() missing 1 required positional argument: 'db_url'"


def test_init_optional_args(app):
    engine_args = {}
    session_args = {}

    DBSessionMiddleware(app, db_url, engine_args=engine_args, session_args=session_args)

    with pytest.raises(TypeError) as exc_info:
        DBSessionMiddleware(app, db_url=db_url, invalid_args="test")

    assert exc_info.value.args[0] == "__init__() got an unexpected keyword argument 'invalid_args'"


def test_inside_route(app, client):
    app.add_middleware(DBSessionMiddleware, db_url="sqlite://")

    @app.get("/")
    def test_get():
        assert isinstance(db.session, Session)

    client.get("/")


def test_inside_route_without_middleware(app, client):
    @app.get("/")
    def test_get():
        with pytest.raises(MissingSessionError):
            sess = db.session
            assert isinstance(sess, None)

    client.get("/")
