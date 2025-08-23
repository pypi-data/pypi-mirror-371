# Copyright (c) 2025 Adam Karpierz
# SPDX-License-Identifier: MIT

from typing import Any
from collections.abc import Callable
import abc
import functools

__all__ = ('decorator',)


class decorator(abc.ABC):
    """Decorator defined entirely as class."""

    func: Callable[..., Any] | None
    options: dict[str, Any]  | None

    def __new__(cls, func: Callable[..., Any] | None = None, /, **options: Any) -> 'decorator':
        """Constructor"""
        self = super().__new__(cls)
        self.func = func
        self.options = options
        if self.func is not None:
            self.options = None
            functools.update_wrapper(self, self.func)
        return self

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call"""
        if self.func is not None:
            return self.__wrapper__(self.func, *args, **kwargs)
        else:
            self.func = args[0]
            wrapper = lambda *args, **kwargs: self.__wrapper__(self.func, *args, **kwargs)
            functools.update_wrapper(wrapper, self.func)
            return wrapper

    @abc.abstractmethod
    def __wrapper__(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Call wrapper"""
        raise NotImplementedError()


del Any, Callable
del abc
