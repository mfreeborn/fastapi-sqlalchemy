from unittest.mock import Mock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi_sqlalchemy.exceptions import MissingSessionError, SessionNotInitialisedError

db_url = "sqlite://"


def test_init(app, DBSessionMiddleware):
    mw = DBSessionMiddleware(app, db_url=db_url)
    assert isinstance(mw, BaseHTTPMiddleware)


def test_init_required_args(app, DBSessionMiddleware):
    with pytest.raises(ValueError) as exc_info:
        DBSessionMiddleware(app)

    assert exc_info.value.args[0] == "You need to pass a db_url or a custom_engine parameter."


def test_init_required_args_custom_engine(app, db, DBSessionMiddleware):
    custom_engine = create_engine(db_url)
    DBSessionMiddleware(app, custom_engine=custom_engine)


def test_init_correct_optional_args(app, db, DBSessionMiddleware):
    engine_args = {"echo": True}
    session_args = {"expire_on_commit": False}

    DBSessionMiddleware(app, db_url, engine_args=engine_args, session_args=session_args)

    with db():
        assert not db.session.expire_on_commit

        engine = db.session.bind
        assert engine.echo


def test_init_incorrect_optional_args(app, DBSessionMiddleware):
    with pytest.raises(TypeError) as exc_info:
        DBSessionMiddleware(app, db_url=db_url, invalid_args="test")

    assert exc_info.value.args[0] == "__init__() got an unexpected keyword argument 'invalid_args'"


def test_inside_route(app, client, db, DBSessionMiddleware):
    app.add_middleware(DBSessionMiddleware, db_url=db_url)

    @app.get("/")
    def test_get():
        assert isinstance(db.session, Session)

    client.get("/")


def test_inside_route_without_middleware_fails(app, client, db):
    @app.get("/")
    def test_get():
        with pytest.raises(SessionNotInitialisedError):
            db.session

    client.get("/")


def test_outside_of_route(app, db, DBSessionMiddleware):
    app.add_middleware(DBSessionMiddleware, db_url=db_url)

    with db():
        assert isinstance(db.session, Session)


def test_outside_of_route_without_middleware_fails(db):
    with pytest.raises(SessionNotInitialisedError):
        db.session

    with pytest.raises(SessionNotInitialisedError):
        with db():
            pass


def test_outside_of_route_without_context_fails(app, db, DBSessionMiddleware):
    app.add_middleware(DBSessionMiddleware, db_url=db_url)

    with pytest.raises(MissingSessionError):
        db.session


def test_db_context_temporary_session_args(app, db, DBSessionMiddleware):
    app.add_middleware(DBSessionMiddleware, db_url=db_url)

    session_args = {}
    with db(session_args=session_args):
        assert isinstance(db.session, Session)

        assert db.session.expire_on_commit

    session_args = {"expire_on_commit": False}
    with db(session_args=session_args):
        assert not db.session.expire_on_commit


def test_rollback(app, db, DBSessionMiddleware):
    #  pytest-cov shows that the line in db.__exit__() rolling back the db session
    #  when there is an Exception is run correctly. However, it would be much better
    #  if we could demonstrate somehow that db.session.rollback() was called e.g. once
    app.add_middleware(DBSessionMiddleware, db_url=db_url)

    with pytest.raises(Exception):
        with db():
            raise Exception


@pytest.mark.parametrize("commit_on_exit", [True, False])
def test_commit_on_exit(app, client, db, DBSessionMiddleware, commit_on_exit):

    with patch("fastapi_sqlalchemy.middleware._session") as session_var:

        mock_session = Mock()
        session_var.get.return_value = mock_session

        app.add_middleware(DBSessionMiddleware, db_url=db_url, commit_on_exit=commit_on_exit)

        @app.get("/")
        def test_get():
            pass

        client.get("/")

        assert mock_session.commit.called == commit_on_exit
