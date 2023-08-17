---
title: FastAPI-SQLAlchemy
---

[![image](https://github.com/mfreeborn/fastapi-sqlalchemy/workflows/ci/badge.svg)](https://github.com/mfreeborn/fastapi-sqlalchemy/actions)
[![image](https://codecov.io/gh/mfreeborn/fastapi-sqlalchemy/branch/master/graph/badge.svg)](https://codecov.io/gh/mfreeborn/fastapi-sqlalchemy)
[![image](https://img.shields.io/pypi/v/fastapi_sqlalchemy?color=blue)](https://pypi.org/project/fastapi-sqlalchemy)

FastAPI-SQLAlchemy provides a simple integration between
[FastAPI](https://github.com/tiangolo/fastapi) and
[SQLAlchemy](https://github.com/pallets/flask-sqlalchemy) in your
application. It gives access to useful helpers to facilitate the
completion of common tasks.

# Installing
Install and update using
[pip](https://pip.pypa.io/en/stable/quickstart/):
``` text
$ pip install fastapi-sqlalchemy
```
# Examples
## Models definition
``` python
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeMeta, declarative_base, sessionmaker

from fastapi_sqlalchemy import SQLAlchemy
db = SQLAlchemy(url="sqlite:///example.db")
#Define User class
class User(db.Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

    def __repr__(self):
        return f"User(id={self.id}, name='{self.name}',email='{self.email}')"
```
## Usage inside of a route
``` python
from fastapi import FastAPI
from models import User, db
from pydantic import BaseModel

from fastapi_sqlalchemy import DBSessionMiddleware

app = FastAPI()

# Add SQLAlchemy session middleware to manage database sessions
app.add_middleware(DBSessionMiddleware, db=db)


# Endpoint to retrieve all users
@app.get("/users")
def get_users():
    """
    Retrieve a list of all users.

    Returns:
        List[User]: A list of User objects.
    """
    return User.query.all()


# Pydantic model for creating new users
class UserCreate(BaseModel):
    name: str
    email: str


# Endpoint to add a new user
@app.post("/add_user")
def add_user(user_data: UserCreate):
    """
    Add a new user to the database.

    Args:
        user_data (UserCreate): User data including name and email.

    Returns:
        dict: A message indicating the success of the operation.
    """
    user = User(**user_data.model_dump())
    print(user)
    user.save()
    return {"message": "User created successfully"}

```
You can initialize the SQLAlchemy() class similar to the way
flask-sqlalchemy, this allows for multiple database connections to work
at the same time.
## Usage outside of a route

Sometimes it is useful to be able to access the database outside the
context of a request, such as in scheduled tasks which run in the
background:

``` python
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # other schedulers are available
from fastapi import FastAPI
from models import User, db
from fastapi_sqlalchemy import DBSessionMiddleware

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url="sqlite:///example.db")


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
        user_count = User.query.count()

        user_count = UserCount(user_count)
        user_count.save()

    # no longer able to access a database session once the db() context manager has ended

    return users
```
## Custom Model Base
You can define custom BaseModels, or extend the built in ModelBase to provide extended shared functionality for you database models.
```python
import inspect
from typing import List

from sqlalchemy import Column

from fastapi_sqlalchemy import ModelBase


class BaseModel(ModelBase):
    @classmethod
    def new(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()
        return obj

    @classmethod
    def get(cls, **kwargs):
        result: cls = cls.query.filter_by(**kwargs).first()
        return result

    @classmethod
    def get_all(cls, **kwargs):
        result: List[cls] = cls.query.filter_by(**kwargs).all()
        return result

    def update(self, **kwargs):
        for column, value in kwargs.items():
            setattr(self, column, value)

        self.save()
        return self

```
As you can see the above BaseModel class adds support for various common functions and operations.
## Complete examples

- [Using single database](examples/single_db/)

- [Using multiple databases](examples/multi_db/)

- [Legacy method](examples/legacy/)
# Legacy Examples

## Models definition
Note the only change that you need to make is to add the db.Base inheritance to each of your
model classes
``` python
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from fastapi_sqlalchemy import ModelBase, SQLAlchemy

db = SQLAlchemy(url="sqlite:///example.db")


# Define the User class representing the "users" database table
# Using the SQLAlchemy Base property instead of defining your own
# And inheriting from the BaseModel class for type hinting and helpful builtin methods and properties
class User(ModelBase, db.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

    def __repr__(self):
        return f"User(id={self.id}, name='{self.name}',email='{self.email}')"

```
## Usage inside of a route

``` python
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware  # middleware helper
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from app.models import User

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url="sqlite:///example.db")

# once the middleware is applied, any route can then access the database session 
# from the global ``db``

@app.get("/users")
def get_users():
    users = db.session.query(User).all()

    return users
```

Note that the session object provided by `db.session` is based on the
Python3.7+ `ContextVar`. This means that each session is linked to the
individual request context in which it was created.

## Usage outside of a route

Sometimes it is useful to be able to access the database outside the
context of a request, such as in scheduled tasks which run in the
background:

``` python
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # other schedulers are available
from fastapi import FastAPI
from fastapi_sqlalchemy import db

from app.models import User, UserCount

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url="sqlite:///example.db")


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
```
