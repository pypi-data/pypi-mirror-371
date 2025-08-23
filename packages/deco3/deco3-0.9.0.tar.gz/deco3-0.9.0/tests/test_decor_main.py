# Copyright (c) 2025 Adam Karpierz
# SPDX-License-Identifier: MIT

from deco._decorator import decorator


class test_decorator(decorator):

    def __wrapper__(self, func, *args, **kwargs):
        # code to run prior to function call
        result = func(*args, **kwargs)
        # code to run after function call
        print()
        print("Decorator options: ", self.options)
        print("Function arguments:", args, kwargs)
        return result


@test_decorator(a=11, b=12)
def decorated_with_options(self, *args, **kwargs):
    """decorated_with_options docstring"""
    return dict(a=11, b=12)


@test_decorator()
def decorated_with_empty_options(self, *args, **kwargs):
    """decorated_with_empty_options docstring"""
    return {}


@test_decorator
def decorated_withou_options(self, *args, **kwargs):
    """decorated_withou_options docstring"""
    return None
