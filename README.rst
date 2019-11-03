FastAPI-SQLAlchemy
==================

FastAPI-SQLAlchemy provides a simple integration between `FastAPI`_ and `SQLAlchemy`_ in your application. It gives access to useful helpers to facilitate the completion of common tasks.


Installing
----------

Install and update using `pip`_:

.. code-block:: text

  $ pip install fastapi-sqlalchemy


A Simple Example
----------------

.. code-block:: python

    from fastapi import FastAPI
    from fastapi_sqlalchemy import db, DBSessionMiddleware

    from app.models import User

    app = FastAPI()

    app.add_middleware(DBSessionMiddleware)

    @app.get("/users")
    def get_users():
    users = db.session.query(User).all()