import sys

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette.testclient import TestClient


@pytest.fixture
def app():
    return FastAPI()


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client(app):
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest.fixture
def DBSessionMiddleware():
    from fastapi_sqlalchemy import DBSessionMiddleware

    yield DBSessionMiddleware


@pytest.fixture
def AsyncDBSessionMiddleware():
    from fastapi_sqlalchemy import AsyncDBSessionMiddleware

    yield AsyncDBSessionMiddleware


@pytest.fixture
def db():
    from fastapi_sqlalchemy import db

    yield db

    # force reloading of module to clear global state

    try:
        del sys.modules["fastapi_sqlalchemy"]
    except KeyError:
        pass

    try:
        del sys.modules["fastapi_sqlalchemy.middleware"]
    except KeyError:
        pass


@pytest.fixture
def async_db():
    from fastapi_sqlalchemy import async_db

    yield async_db

    # force reloading of module to clear global state

    try:
        del sys.modules["fastapi_sqlalchemy"]
    except KeyError:
        pass

    try:
        del sys.modules["fastapi_sqlalchemy.async_middleware"]
    except KeyError:
        pass
