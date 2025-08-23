# Copyright (c) 2016 Alex Sherman
# Copyright (c) 2025 Adam Karpierz
# SPDX-License-Identifier: MIT

from __future__ import annotations

import typing
from typing import Any
from collections.abc import Callable
import inspect
import ast
from multiprocessing import Pool
from multiprocessing.pool import AsyncResult, ThreadPool

from ._decorator import decorator
from ._astutil   import SchedulerRewriter


class synchronized(decorator):

    def __init__(self, func: Callable[..., Any] | None = None) -> None:
        """Initializer"""
        caller_frame = inspect.stack()[1][0]
        self.frame_info: inspect.Traceback = inspect.getframeinfo(caller_frame)
        self.func_rewritten: Callable[..., Any] | None = None
        self.ast: ast.Module | None = None

    def __get__(self, *args: Any) -> Any:
        """Access handler"""
        raise NotImplementedError("Decorators from deco cannot be used on "
                                  "class methods")

    def __wrapper__(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Call wrapper"""
        if self.func_rewritten is None:
            source_lines = inspect.getsourcelines(func)[0]
            self._unindent(source_lines)
            source = "".join(source_lines)
            self.ast = ast.parse(source)
            rewriter = SchedulerRewriter(concurrent.functions.keys(),
                                         self.frame_info)
            rewriter.visit(self.ast.body[0])
            ast.fix_missing_locations(self.ast)
            out = compile(self.ast, "<string>", "exec")
            scope = dict(func.__globals__)
            exec(out, scope)
            self.func_rewritten = scope[func.__name__]
        else: pass  # pragma: no cover
        return self.func_rewritten(*args, **kwargs)

    @staticmethod
    def _unindent(source_lines: list[str]) -> None:
        for i, line in enumerate(source_lines):
            source_lines[i] = line = line.lstrip()
            if line.startswith("def"):
                break
        else: pass  # pragma: no cover


class concurrent(decorator):

    functions: dict[str, Callable[..., Any]] = {}

    threaded: Callable[..., concurrent]

    @staticmethod
    def custom(constructor: Callable[..., Any] | None = None,
               apply_async: Callable[..., AsyncResult[Any]] | None = None) \
               -> Callable[..., concurrent]:
        def _custom_concurrent(*args: Any, **kwargs: Any) -> concurrent:
            conc = concurrent(*args, **kwargs)
            if constructor is not None: conc.conc_constructor = constructor
            if apply_async is not None: conc.apply_async = apply_async
            return conc
        return _custom_concurrent

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializer"""
        self.in_progress: bool = False
        self.conc_args: tuple[Any, ...]  = ()
        self.conc_kwargs: dict[str, Any] = {}
        if self.func is not None:
            self.set_function()
        else:  # pragma: no cover # !!!
            self.conc_args   = args
            self.conc_kwargs = kwargs
        self.results: list[ConcurrentResult] = []
        self.assigns: list[tuple[Any, ConcurrentResult]] = []
        self.calls:   list[tuple[Any, ConcurrentResult]] = []
        self.arg_proxies: dict[int, ArgProxy] = {}
        self.conc_constructor = Pool
        # def apply_async(self, func, args=(), kwds={},
        #                 callback=None, error_callback=None) -> AsyncResult[Any]:
        self.apply_async: Callable[..., AsyncResult[Any]] = lambda self, func, args: \
                                                          self.concurrency.apply_async(func, args)
        self.concurrency: Any = None

    def set_function(self) -> None:
        func = typing.cast(Callable[..., Any], self.func)
        concurrent.functions[func.__name__] = func
        self.fun_name = func.__name__

    def __get__(self, *args: Any) -> Any:
        """Access handler"""
        raise NotImplementedError("Decorators from deco cannot be used on "
                                  "class methods")

    def assign(self, target: Any, *args: Any, **kwargs: Any) -> None:
        self.assigns.append((target, self(*args, **kwargs)))

    def call(self, target: Any, *args: Any, **kwargs: Any) -> None:
        self.calls.append((target, self(*args, **kwargs)))

    def __wrapper__(self, func: Callable[..., Any],
                    *args: Any, **kwargs: Any) -> ConcurrentResult:
        """Call wrapper"""
        self.in_progress = True
        if self.concurrency is None:
            self.concurrency = self.conc_constructor(*self.conc_args,
                                                     **self.conc_kwargs)
        largs = list(args)
        self.replace_with_proxies(largs)
        self.replace_with_proxies(kwargs)
        result = ConcurrentResult(self.apply_async(self, self.concurrent_wrapper,
                                                   [self.fun_name, largs, kwargs]))
        self.results.append(result)
        return result

    def replace_with_proxies(self, args: list[Any] | dict[str, Any]) -> None:
        iterable: Any
        if isinstance(args, list):
            iterable = enumerate(args)
        elif isinstance(args, dict):
            iterable = args.items()
        else:  # pragma: no cover
            raise TypeError(f"Unsupported type: {type(args)}")
        for i, arg in iterable:
            if type(arg) is dict or type(arg) is list:
                arg_id = id(arg)
                if arg_id in self.arg_proxies:  # pragma: no cover
                    args[i] = self.arg_proxies[arg_id]
                else:
                    args[i] = self.arg_proxies[arg_id] = ArgProxy(arg_id, arg)

    @staticmethod
    def concurrent_wrapper(fun_name: str, args: list[Any],
                           kwargs: dict[str, Any]) -> tuple[Any, list[Any]]:
        result = concurrent.functions[fun_name](*args, **kwargs)
        operations = [inner for outer in args + list(kwargs.values())
                      if type(outer) is ArgProxy for inner in outer.operations]
        return result, operations

    def _apply_operations(self, operations: list[tuple[int, Any, Any]]) -> None:
        for arg_id, key, value in operations:
            self.arg_proxies[arg_id].value.__setitem__(key, value)

    def wait(self) -> list[Any]:
        results: list[Any] = []
        while self.results:
            result, operations = self.results.pop().get()
            self._apply_operations(operations)
            results.append(result)
        for assign in self.assigns:
            assign[0][0][assign[0][1]] = assign[1].result()
        self.assigns = []
        for call in self.calls:
            call[0](call[1].result())
        self.calls = []
        self.arg_proxies = {}
        self.in_progress = False
        return results


concurrent.threaded = staticmethod(concurrent.custom(constructor=ThreadPool))


class ArgProxy:

    def __init__(self, arg_id: int, value: Any) -> None:
        """Initializer"""
        self.arg_id: int = arg_id
        self.value:  Any = value
        self.operations: list[tuple[int, Any, Any]] = []

    def __getattr__(self, name: str) -> Any:
        """Attribute access"""
        if name in ("__getstate__", "__setstate__"):
            raise AttributeError()
        if not hasattr(self, "value") or not hasattr(self.value, name):
            raise AttributeError()
        return getattr(self.value, name)

    def __getitem__(self, key: Any) -> Any:
        """Item access"""
        return self.value.__getitem__(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        """Item assignment"""
        self.value.__setitem__(key, value)
        self.operations.append((self.arg_id, key, value))


class ConcurrentResult:

    def __init__(self, async_result: AsyncResult[Any]) -> None:
        """Initializer"""
        self.async_result = async_result

    def get(self) -> Any:
        return self.async_result.get(timeout=3e+6)

    def result(self) -> Any:
        return self.get()[0]
