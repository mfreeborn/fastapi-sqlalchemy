FastAPI-SQLAlchemy
==================

.. image:: https://github.com/mfreeborn/fastapi-sqlalchemy/workflows/ci/badge.svg
    :target: https://github.com/mfreeborn/fastapi-sqlalchemy/actions
.. image:: https://codecov.io/gh/mfreeborn/fastapi-sqlalchemy/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/mfreeborn/fastapi-sqlalchemy
.. image:: https://img.shields.io/pypi/v/fastapi_sqlalchemy?color=blue
    :target: https://pypi.org/project/fastapi-sqlalchemy


FastAPI-SQLAlchemy provides a simple integration between FastAPI_ and SQLAlchemy_ in your application. It gives access to useful helpers to facilitate the completion of common tasks.


Installing
----------

Install and update using pip_:

.. code-block:: text

  $ pip install fastapi-sqlalchemy


Examples
--------

Usage inside of a route
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from fastapi import FastAPI
    from fastapi_sqlalchemy import DBSessionMiddleware  # middleware helper
    from fastapi_sqlalchemy import db  # an object to provide global access to a database session

    from app.models import User

    app = FastAPI()

    app.add_middleware(DBSessionMiddleware, db_url="sqlite://")

    # once the middleware is applied, any route can then access the database session 
    # from the global ``db``

    @app.get("/users")
    def get_users():
        users = db.session.query(User).all()

        return users

Note that the session object provided by ``db.session`` is based on the Python3.7+ ``ContextVar``. This means that
each session is linked to the individual request context in which it was created.

Usage outside of a route
^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes it is useful to be able to access the database outside the context of a request, such as in scheduled tasks which run in the background:

.. code-block:: python

    import pytz
    from apscheduler.schedulers.asyncio import AsyncIOScheduler  # other schedulers are available
    from fastapi import FastAPI
    from fastapi_sqlalchemy import db

    from app.models import User, UserCount

    app = FastAPI()

    app.add_middleware(DBSessionMiddleware, db_url="sqlite://")


    @app.on_event('startup')
    async def startup_event():
        scheduler = AsyncIOScheduler(timezone=pytz.utc)
        scheduler.start()
        scheduler.add_job(count_users_task, "cron", hour=0)  # runs every night at midnight


    def count_users_task():
        """Count the number of users in the database and save it into the user_counts table."""

        # we are outside of a request context, therefore we cannot rely on ``DBSessionMiddleware``
        # to create a database session for us. Instead, we can use the same ``db`` object and 
        # use it as a context manager, like so:

        with db():
            user_count = db.session.query(User).count()

            db.session.add(UserCount(user_count))
            db.session.commit()
        
        # no longer able to access a database session once the db() context manager has ended

        return users

Using a test database fixture with pytest
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A suggested way of to override the database URL and yield a session fixture in your tests is to use environment variables.

.. code-block:: python

    # Contents of app/configs.py
    import json
    import os

    DEV, PROD, TEST = ("development", "production", "test")
    CURRENT_ENV = os.environ.get("PYTHON_ENV", DEV)
    config = {DEV: "sqlite://dev.db", PROD: "postgresql://user:password@sql.mydomain.com/mydb", TEST: "sqlite://"}
    DATABASE_URL = config[CURRENT_ENV]


    # Contents of test_app.py
    import pytest
    from sqlalchemy import create_engine
    from fastapi.testclient import TestClient

    from app.configs import DATABASE_URL
    from app.db import Base  # from sqlalchemy.ext.declarative import declarative_base
    from app.models import User
    from main import app, db


    @pytest.fixture(scope="function", name="session")
    def session_fixture():
        engine = create_engine(DATABASE_URL)
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        with db():
            yield db.session
        engine.dispose()


    @pytest.fixture(scope="function", name="client")
    def client_fixture():
        return TestClient(app)


    def test_users_route(session, client):
        # Save a fake user
        NAME = 'Gontrand'
        user = User(name=NAME)
        session.add(user)
        session.commit()

        response = client.get('users')
        response_user = response.json()[0]
        assert response_user['name'] == NAME

Run your tests with ``PYTHON_ENV=test pytest`` or use dotenv_ to manage these programmatically with an ``.env`` file.

.. _FastAPI: https://github.com/tiangolo/fastapi
.. _SQLAlchemy: https://github.com/pallets/flask-sqlalchemy
.. _pip: https://pip.pypa.io/en/stable/quickstart/
.. _dotenv: https://github.com/theskumar/python-dotenv
