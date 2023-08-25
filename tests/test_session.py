from unittest.mock import Mock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi_sqlalchemy.exceptions import MissingSessionError, SessionNotInitialisedError

# TODO Add tests.
