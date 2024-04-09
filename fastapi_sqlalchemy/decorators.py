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
            is_awaited = False
            for code in inspect.getframeinfo(inspect.currentframe().f_back).code_context:
                try:
                    ast_tree = ast.parse(code.strip())
                    for node in ast.walk(ast_tree):
                        if isinstance(node, ast.Await):
                            is_awaited = True
                except:
                    pass
            if from_coroutine():
                if is_awaited:
                    return asyncfunc(cls, *args, **kwargs)
                else:
                    return syncfunc(cls, *args, **kwargs)
            else:
                return syncfunc(cls, *args, **kwargs)

        return wrapper

    return coroutine
