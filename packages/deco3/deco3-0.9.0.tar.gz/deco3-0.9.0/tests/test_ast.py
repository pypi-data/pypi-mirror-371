# Copyright (c) 2016 Alex Sherman
# Copyright (c) 2025 Adam Karpierz
# SPDX-License-Identifier: MIT

import unittest
import time

from deco import concurrent, synchronized


@concurrent  # pragma: no cover
def conc_func(*args, **kwargs):
    time.sleep(0.1)
    return kwargs


@synchronized  # pragma: no cover
def body_cases():
    conc_func()
    a = True if False else False
    b = (lambda: True)()


@synchronized  # pragma: no cover
def tainted_return():
    data = []
    data.append(conc_func(data))
    return data


@synchronized  # pragma: no cover
def len_of_append():
    data = []
    data.append(conc_func([]))
    derp = len(data)
    return derp


def indented():  # pragma: no cover
    @synchronized
    def _indented():
        conc_func()

    return _indented()


@synchronized  # pragma: no cover
def kwarged_sync(**kwargs):
    data = []
    data.append(conc_func(**kwargs))
    return data[0]


@synchronized  # pragma: no cover
def subscript_args():
    d = type('', (object,), {"items": {(0,0): 0}})()
    conc_func(d.items[0, 0])
    # Read d to force a synchronization event
    d = d
    output = conc_func.in_progress
    return output


@synchronized  # pragma: no cover
def list_comp():
    result = [conc_func(i = i) for i in range(10)]
    return result


class TestAST(unittest.TestCase):

    # This just shouldn't throw any exceptions
    def test_body_cases(self):
        body_cases()

    # This just shouldn't throw any exceptions
    def test_indent_cases(self):
        indented()

    # This just shouldn't throw any exceptions
    def test_tainted_return(self):
        tainted_return()

    def test_subscript_args(self):
        self.assertFalse(subscript_args())

    def test_kwarged_sync(self):
        self.assertTrue(kwarged_sync(test = "test")["test"] == "test")

    def test_wait_after_append(self):
        self.assertEqual(len_of_append(), 1)

    def test_list_comp(self):
        self.assertEqual(list_comp(),[{'i': i} for i in range(10)])


if __name__ == "__main__":
    unittest.main(exit=False)
