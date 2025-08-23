# Copyright (c) 2016 Alex Sherman
# Copyright (c) 2025 Adam Karpierz
# SPDX-License-Identifier: MIT

import unittest
import types

from deco import concurrent, synchronized


@concurrent  # pragma: no cover
def kwarg_func(kwarg = None):
    kwarg[0] = "kwarged"
    return kwarg


@concurrent  # pragma: no cover
def add_one(value):
    return value + 1


@synchronized  # pragma: no cover
def for_loop(values):
    output = []
    for i in values:
        output.append(add_one(i))
    return [i - 1 for i in output]


@concurrent  # pragma: no cover
def conc_with_assign_error():
    return [0, 1, 2, 3]


@synchronized  # pragma: no cover
def with_assign_mult_targets_error():
    y = z = conc_with_assign_error()
    return [2, 3, 4, 5]


@synchronized  # pragma: no cover
def with_assign_no_index_error():
    y = conc_with_assign_error()
    return [6, 7, 8, 9]


@concurrent.threaded  # pragma: no cover
def conc_threaded0():
    return [0, 1, 2, 3]


@concurrent.threaded  # pragma: no cover
def conc_threaded1():
    conc_threaded0()
    return [0, -1, -2, -3]


@synchronized  # pragma: no cover
def sync_threaded():
    conc_threaded1()
    return [11, 12, 13, 14]


class TestConcurent(unittest.TestCase):

    def test_kwargs(self):
        list_ = [0]
        kwarg_func(kwarg = list_)
        kwarg_func.wait()
        self.assertEqual(list_[0], "kwarged")

    def test_for_loop(self):
        values = range(30)
        self.assertEqual(for_loop(values), list(values))

    def test_with_assign_mult_targets_error(self):
        with self.assertRaisesRegex(NotImplementedError,
                                    "Concurrent assignment does not support "
                                    "multiple assignment targets"):
            with_assign_mult_targets_error()

    def test_with_assign_no_index_error(self):
        with self.assertRaisesRegex(NotImplementedError,
                                    "Concurrent assignment only implemented "
                                    "for index based objects"):
            with_assign_no_index_error()

    def test_threaded(self):
        sync_threaded()

    def test_utils(self):

        from deco._concurrent import ArgProxy

        obj = "any text" ; obj_id = id(obj)
        arg_proxy = ArgProxy(arg_id=obj_id, value=obj)
        self.assertEqual(arg_proxy.arg_id, obj_id)
        self.assertEqual(arg_proxy.value,  obj)
        self.assertEqual(arg_proxy.operations, [])

        obj = None ; obj_id = id(obj)
        arg_proxy = ArgProxy(arg_id=obj_id, value=obj)
        self.assertEqual(arg_proxy.arg_id, obj_id)
        self.assertIsNone(arg_proxy.value)
        self.assertEqual(arg_proxy.operations, [])

        obj = 123 ; obj_id = id(obj)
        arg_proxy = ArgProxy(obj_id, obj)
        self.assertEqual(arg_proxy.arg_id, obj_id)
        self.assertEqual(arg_proxy.value,  obj)
        self.assertEqual(arg_proxy.operations, [])
        # with self.assertRaises(AttributeError):
        #     attr = arg_proxy.__getstate__
        with self.assertRaises(AttributeError):
            attr = arg_proxy.__setstate__
        with self.assertRaises(AttributeError):
            attr = arg_proxy.nonexistent
        self.assertEqual(arg_proxy.numerator, obj)
        self.assertEqual(arg_proxy.denominator, 1)
        self.assertIsInstance(getattr(arg_proxy, "bit_count", None),
                              (types.BuiltinFunctionType, types.MethodType))
        self.assertEqual(arg_proxy.bit_count(), 6)

        obj = [5, "abc", 45.67] ; obj_id = id(obj)
        arg_proxy = ArgProxy(obj_id, value=obj)
        self.assertEqual(arg_proxy.arg_id, obj_id)
        self.assertEqual(arg_proxy.value,  obj)
        self.assertEqual(arg_proxy.operations, [])
        self.assertIsInstance(getattr(arg_proxy, "insert", None),
                              (types.BuiltinFunctionType, types.MethodType))
        self.assertIsInstance(getattr(arg_proxy, "append", None),
                              (types.BuiltinFunctionType, types.MethodType))
        self.assertIsInstance(getattr(arg_proxy, "sort",   None),
                              (types.BuiltinFunctionType, types.MethodType))
        self.assertIsInstance(getattr(arg_proxy, "clear",  None),
                              (types.BuiltinFunctionType, types.MethodType))
        self.assertIsInstance(getattr(arg_proxy, "count",  None),
                              (types.BuiltinFunctionType, types.MethodType))
        self.assertEqual(arg_proxy[0], obj[0])
        self.assertEqual(arg_proxy[1], obj[1])
        self.assertEqual(arg_proxy[2], obj[2])
        arg_proxy[0] = 55
        self.assertEqual(arg_proxy.operations, [(obj_id, 0, 55)])
        arg_proxy[1] = "ABCabc"
        self.assertEqual(arg_proxy.operations, [(obj_id, 0, 55),
                                                (obj_id, 1, "ABCabc")])
        arg_proxy[2] = 545.67
        self.assertEqual(arg_proxy.operations, [(obj_id, 0, 55),
                                                (obj_id, 1, "ABCabc"),
                                                (obj_id, 2, 545.67)])
        self.assertEqual(arg_proxy[0], 55)
        self.assertEqual(arg_proxy[1], "ABCabc")
        self.assertEqual(arg_proxy[2], 545.67)

        obj = dict(x=66, y="uvwx", z=78.4) ; obj_id = id(obj)
        arg_proxy = ArgProxy(obj_id, value=obj)
        self.assertEqual(arg_proxy.arg_id, obj_id)
        self.assertEqual(arg_proxy.value,  obj)
        self.assertEqual(arg_proxy.operations, [])
        self.assertIsInstance(getattr(arg_proxy, "keys",   None),
                              (types.BuiltinFunctionType, types.MethodType))
        self.assertIsInstance(getattr(arg_proxy, "values", None),
                              (types.BuiltinFunctionType, types.MethodType))
        self.assertIsInstance(getattr(arg_proxy, "items",  None),
                              (types.BuiltinFunctionType, types.MethodType))
        self.assertIsInstance(getattr(arg_proxy, "get",    None),
                              (types.BuiltinFunctionType, types.MethodType))
        self.assertIsInstance(getattr(arg_proxy, "update", None),
                              (types.BuiltinFunctionType, types.MethodType))
        self.assertIsInstance(getattr(arg_proxy, "clear",  None),
                              (types.BuiltinFunctionType, types.MethodType))
        self.assertEqual(arg_proxy["x"], obj["x"])
        self.assertEqual(arg_proxy["y"], obj["y"])
        self.assertEqual(arg_proxy["z"], obj["z"])
        arg_proxy["x"] = 666
        self.assertEqual(arg_proxy.operations, [(obj_id, "x", 666)])
        arg_proxy["y"] = "UVWuvwx"
        self.assertEqual(arg_proxy.operations, [(obj_id, "x", 666),
                                                (obj_id, "y", "UVWuvwx")])
        arg_proxy["z"] = 778.4
        self.assertEqual(arg_proxy.operations, [(obj_id, "x", 666),
                                                (obj_id, "y", "UVWuvwx"),
                                                (obj_id, "z", 778.4)])
        self.assertEqual(arg_proxy["x"], 666)
        self.assertEqual(arg_proxy["y"], "UVWuvwx")
        self.assertEqual(arg_proxy["z"], 778.4)


if __name__ == "__main__":
    unittest.main(exit=False)
