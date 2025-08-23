# Copyright (c) 2016 Alex Sherman
# Copyright (c) 2025 Adam Karpierz
# SPDX-License-Identifier: MIT

from __future__ import annotations

import typing
from typing import Any
from collections.abc import KeysView
import inspect
import ast


class SchedulerRewriter(ast.NodeTransformer):

    def __init__(self, concurrent_funcs: KeysView[Any],
                 frame_info: inspect.Traceback) -> None:
        """Initializer"""
        self.concurrent_funcs: KeysView[Any] = concurrent_funcs
        self.encountered_funcs: set[Any] = set()
        self.arguments:         set[Any] = set()
        self.line_offset = frame_info.lineno - 1
        self.filename    = frame_info.filename

    @classmethod
    def top_level_name(cls, node: ast.AST) -> str | None:
        if type(node) is ast.Name:
            return node.id
        elif type(node) is ast.Subscript or type(node) is ast.Attribute:
            return cls.top_level_name(node.value)
        return None

    def is_references_arg(self, node: Any) -> bool:
        if not isinstance(node, ast.AST):
            return False
        if type(node) is ast.Name:
            return type(node.ctx) is ast.Load and node.id in self.arguments
        for field in node._fields:
            if field == "body": continue
            value = getattr(node, field)
            if not hasattr(value, "__iter__"):
                value = [value]
            if any([self.is_references_arg(child) for child in value]):
                return True
        return False

    def is_concurrent_call(self, node: Any) -> bool:
        return (type(node) is ast.Call
                and type(node.func) is ast.Name
                and node.func.id in self.concurrent_funcs)

    def encounter_call(self, call: ast.Call) -> None:
        self.encountered_funcs.add(call.func.id)  # type: ignore[attr-defined]
        for arg in call.args:
            arg_name = self.top_level_name(arg)
            if arg_name is not None:
                self.arguments.add(arg_name)

    def get_waits(self) -> list[ast.Expr]:
        return [ast.Expr(self.make_Call(func = ast.Attribute(ast.Name(fname,  ast.Load()),
                                                             "wait", ast.Load())))
                for fname in self.encountered_funcs]

    def visit_Call(self, node: ast.Call) -> ast.AST:
        if self.is_concurrent_call(node):  # pragma: no cover # !!!
            raise self.not_implemented_error(node,
                "The usage of the @concurrent function is unsupported")
        return self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> ast.AST:
        node_value = node.value
        if type(node_value) is ast.Call:
            call: ast.Call = node_value
            if self.is_concurrent_call(call):
                self.encounter_call(call)
                return node
            elif any([self.is_concurrent_call(arg) for arg in call.args]):
                conc_args = [(i, arg) for i, arg in enumerate(call.args)
                             if self.is_concurrent_call(arg)]
                if len(conc_args) > 1:  # pragma: no cover # !!!
                    raise self.not_implemented_error(call,
                        "Functions with multiple @concurrent parameters are unsupported")
                conc_call: ast.Call = conc_args[0][1]  # type: ignore[assignment]
                if isinstance(call.func, ast.Attribute):
                    self.arguments.add(self.top_level_name(call.func.value))
                else: pass  # pragma: no cover
                self.encounter_call(conc_call)
                call.args[conc_args[0][0]] = ast.Name("__value__", ast.Load())
                call_lambda = self.make_Lambda(args = [ast.arg("__value__", None)],
                                               body = call)
                return ast.copy_location(ast.Expr(self.make_Call(
                    func = ast.Attribute(conc_call.func, "call", ast.Load()),
                    args = [call_lambda] + conc_call.args,
                    keywords = conc_call.keywords)), node)
        else: pass  # pragma: no cover
        return self.generic_visit(node)

    # List comprehensions are self contained, so no need to add to self.arguments
    def visit_ListComp(self, node: ast.ListComp) -> ast.AST:
        if self.is_concurrent_call(node.elt):
            call: ast.Call = node.elt  # type: ignore[assignment]
            self.encounter_call(call)
            wrapper = self.make_Call(
                func = ast.Name("list", ast.Load()),
                args = [
                    self.make_Call(
                        func = ast.Name("map", ast.Load()),
                        args = [
                            self.make_Lambda(
                                args = [ast.arg(arg="r")],
                                body = self.make_Call(
                                           func = ast.Attribute(ast.Name("r", ast.Load()),
                                                                "result", ast.Load())
                                       )
                            ),
                            typing.cast(ast.expr, node)
                        ]
                    )
                ]
            )
            return wrapper
        else: pass  # pragma: no cover
        return self.generic_visit(node)  # pragma: no cover

    def is_valid_assignment(self, node: Any) -> bool:
        if type(node) is not ast.Assign or not self.is_concurrent_call(node.value):
            return False
        if len(node.targets) != 1:
            raise self.not_implemented_error(node,
                "Concurrent assignment does not support multiple assignment targets")
        if type(node.targets[0]) is not ast.Subscript:
            raise self.not_implemented_error(node,
                "Concurrent assignment only implemented for index based objects")
        return True

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        if self.is_valid_assignment(node):
            call: ast.Call = node.value  # type: ignore[assignment]
            self.encounter_call(call)
            name = node.targets[0].value  # type: ignore[attr-defined]
            self.arguments.add(self.top_level_name(name))
            # Check ast.slice compatibility
            index = node.targets[0].slice  # type: ignore[attr-defined]
            # For Python <= 3.8
            if hasattr(index, "value"): index = index.value
            call.func = ast.Attribute(call.func, "assign", ast.Load())
            call.args = [ast.Tuple([name, index], ast.Load())] + call.args
            return ast.copy_location(ast.Expr(call), node)
        return self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        node.decorator_list = []
        ret_node: ast.FunctionDef = self.generic_visit(node)  # type: ignore[assignment]
        ret_node.body += self.get_waits()
        return ret_node

    def generic_visit(self, node: ast.AST) -> ast.AST:
        if ((isinstance(node, ast.stmt) and self.is_references_arg(node))
           or isinstance(node, ast.Return)):
            return self.get_waits() + [node]  # type: ignore[return-value] # !!!
        return super().generic_visit(node)

    @staticmethod
    def make_Call(*, func: ast.expr, args: list[ast.expr] | None = None,
                  keywords: list[ast.keyword] | None = None) -> ast.Call:
        if args     is None: args     = []
        if keywords is None: keywords = []
        return ast.Call(func, args, keywords)

    @staticmethod
    def make_Lambda(*, args: list[ast.arg] | None = None, body: ast.expr) -> ast.Lambda:
        if args is None: args = []
        return ast.Lambda(ast.arguments(posonlyargs=[], args=args, defaults=[],
                                        kwonlyargs=[], kw_defaults=[]), body)

    def not_implemented_error(self, node: ast.AST, message: str) -> NotImplementedError:
        if hasattr(node, "lineno"):
            lineno = node.lineno + self.line_offset
            message = f"{self.filename}({lineno}) {message}"
        else:  # pragma: no cover
            message = f"{self.filename} {message}"
        return NotImplementedError(message)
