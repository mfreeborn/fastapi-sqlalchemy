import ast
import asyncio
import inspect
from functools import wraps
from typing import Any, Awaitable, Callable, Self

from curio.meta import from_coroutine


def awaitable(asyncfunc):
    def coroutine(syncfunc):
        @wraps(syncfunc)
        def wrapper(cls, *args, **kwargs):
            if from_coroutine():
                if any(
                    [
                        isinstance(node, ast.Await)
                        for node in ast.walk(
                            ast.parse(
                                "".join(
                                    i.strip()
                                    for i in inspect.getframeinfo(
                                        inspect.currentframe().f_back
                                    ).code_context
                                )
                            )
                        )
                    ]
                ):
                    return asyncfunc(cls, *args, **kwargs)
                else:
                    return syncfunc(cls, *args, **kwargs)
            else:
                return syncfunc(cls, *args, **kwargs)

        return wrapper

    return coroutine
