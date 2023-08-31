import inspect
from functools import wraps
from typing import Any, Awaitable, Callable, Self

from curio.meta import from_coroutine


def awaitable(asyncfunc):
    def coroutine(syncfunc):
        @wraps(syncfunc)
        def wrapper(cls, *args, **kwargs):
            if from_coroutine():
                return asyncfunc(cls, *args, **kwargs)
            else:
                return syncfunc(cls, *args, **kwargs)

        return wrapper

    return coroutine
