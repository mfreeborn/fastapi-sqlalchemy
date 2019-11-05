FastAPI-SQLAlchemy
==================

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


.. _FastAPI: https://github.com/tiangolo/fastapi
.. _SQLAlchemy: https://github.com/pallets/flask-sqlalchemy
.. _pip: https://pip.pypa.io/en/stable/quickstart/
