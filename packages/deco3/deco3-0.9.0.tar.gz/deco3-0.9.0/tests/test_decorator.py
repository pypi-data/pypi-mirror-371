# Copyright (c) 2016 Alex Sherman
# Copyright (c) 2025 Adam Karpierz
# SPDX-License-Identifier: MIT

import unittest
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from test_decor_main import (
    decorated_with_options,
    decorated_with_empty_options,
    decorated_withou_options)
from deco import concurrent, synchronized


@concurrent  # pragma: no cover
def kwarg_func(kwarg = None):
    """kwarg_func docstring"""
    kwarg[0] = "kwarged"
    return kwarg


@concurrent  # pragma: no cover
def add_one(value):
    """add_one docstring"""
    return value + 1


@synchronized  # pragma: no cover
def for_loop(values):
    """for_loop docstring"""
    output = []
    for i in values:
        output.append(add_one(i))
    return [i - 1 for i in output]


@synchronized()  # pragma: no cover
def sync_with_params0():
    return [5,6,7,8]


class TestDecorator(unittest.TestCase):

    def test_general_decorator(self):

        self.assertEqual(decorated_with_options.__name__,
                        "decorated_with_options")
        self.assertEqual(decorated_with_empty_options.__name__,
                         "decorated_with_empty_options")
        self.assertEqual(decorated_withou_options.__name__,
                         "decorated_withou_options")

        self.assertEqual(decorated_with_options.__doc__,
                         "decorated_with_options docstring")
        self.assertEqual(decorated_with_empty_options.__doc__,
                         "decorated_with_empty_options docstring")
        self.assertEqual(decorated_withou_options.__doc__,
                         "decorated_withou_options docstring")

        self.assertEqual(decorated_with_options.__module__,
                         "test_decor_main")
        self.assertEqual(decorated_with_empty_options.__module__,
                         "test_decor_main")
        self.assertEqual(decorated_withou_options.__module__,
                         "test_decor_main")

        self.assertEqual(decorated_with_options(3,4,5), dict(a=11, b=12))
        self.assertEqual(decorated_with_empty_options(7,8,9,0, yyy= 5), {})
        self.assertIsNone(decorated_withou_options(9,8,3,5,6, ddd = 3))

    def test_deco_decorators(self):

        self.assertEqual(kwarg_func.__name__, "kwarg_func")
        self.assertEqual(add_one.__name__,  "add_one")
        self.assertEqual(for_loop.__name__, "for_loop")
        self.assertEqual(sync_with_params0.__name__, "sync_with_params0")

        self.assertEqual(kwarg_func.__doc__, "kwarg_func docstring")
        self.assertEqual(add_one.__doc__,  "add_one docstring")
        self.assertEqual(for_loop.__doc__, "for_loop docstring")
        self.assertEqual(sync_with_params0.__doc__, None)

        self.assertEqual(kwarg_func.__module__, "__main__")
        self.assertEqual(add_one.__module__,  "__main__")
        self.assertEqual(for_loop.__module__, "__main__")
        self.assertEqual(sync_with_params0.__module__, "__main__")

    def test_deco_sync_with_params0(self):
        self.assertEqual(sync_with_params0(), [5,6,7,8])


if __name__ == "__main__":
    unittest.main(exit=False)
