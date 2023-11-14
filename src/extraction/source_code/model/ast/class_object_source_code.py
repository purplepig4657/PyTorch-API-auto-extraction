from __future__ import annotations

import ast
from typing import Optional, Union

from src.common.model.class_object import ClassObject
from src.common.model.function import Function
from src.common.model.method import Method
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.extraction.source_code.model.ast.function_source_code import FunctionSourceCode
from src.extraction.source_code.model.ast.method_source_code import MethodSourceCode
from src.extraction.source_code.model.ast.parameter_source_code import ParameterSourceCode


class ClassObjectSourceCode(ClassObject):

    __class_node: ast.ClassDef
    __symbol: Symbol
    __method_list: list[Method]
    __param_list: list[Parameter]

    def __init__(
            self,
            class_node: ast.ClassDef,
            symbol: Symbol = None,
            param_list: list[Parameter] = None,
            method_list: list[Method] = None
    ):
        self.__class_node = class_node
        self.__symbol = self.__extract_class_name() if symbol is None else symbol
        self.__method_list = self.__extract_method_list() if method_list is None else method_list
        self.__param_list = self.__extract_param_list() if param_list is None else param_list
        super().__init__(self.__symbol, self.__param_list, self.__method_list)

    def __extract_class_name(self) -> Symbol:
        return Symbol(self.__class_node.name)

    def __extract_param_list(self) -> list[Parameter]:
        init_method: Optional[ast.FunctionDef] = None
        for method in self.__method_list:
            if method.symbol.name == '__init__':
                assert isinstance(method, MethodSourceCode)
                init_method = method.node
        if init_method is None:
            return []
        arguments: ast.arguments = init_method.args
        args: list[ast.arg] = arguments.args
        posonlyargs: list[ast.arg] = arguments.posonlyargs
        kwonlyargs: list[ast.arg] = arguments.kwonlyargs
        kwarg: ast.arg = arguments.kwarg
        vararg: ast.arg = arguments.vararg
        defaults: list[ast.expr] = arguments.defaults
        kw_defaults: list[ast.expr] = arguments.kw_defaults

        args_and_posonlyargs: list[ast.arg] = posonlyargs + args  # posonlyargs declare first. Order is important!
        args_and_posonlyargs_with_default: list[tuple[ast.arg, Optional[ast.expr]]] = [
            (args_and_posonlyargs[i], defaults[i - (len(args_and_posonlyargs) - len(defaults))]
            if i >= len(args_and_posonlyargs) - len(defaults) else None)
            for i in range(len(args_and_posonlyargs))
        ]
        kwonlyargs_with_default: list[tuple[ast.arg, Optional[ast.expr]]] = [
            (kwonlyargs[i], kw_defaults[i]) for i in range(len(kwonlyargs))
        ]

        all_args: list[tuple[ast.arg, Optional[ast.expr]]] = args_and_posonlyargs_with_default + kwonlyargs_with_default

        if kwarg is not None:
            kwarg_with_default: tuple[ast.arg, None] = (kwarg, None)
            all_args.append(kwarg_with_default)
        if vararg is not None:
            vararg_with_default: tuple[ast.arg, None] = (vararg, None)
            all_args.append(vararg_with_default)

        parameter_list: list[Parameter] = list[Parameter]()
        for arg in all_args:
            parameter_list.append(ParameterSourceCode(*arg))
        return parameter_list

    def __extract_method_list(self) -> list[Method]:
        method_list: list[Method] = list[Method]()
        method_def_list: list[ast.FunctionDef] = self.__collect_method_def()
        for method_def in method_def_list:
            method_list.append(MethodSourceCode(method_def))
        return method_list

    def __collect_method_def(self) -> list[ast.FunctionDef]:
        stmts: list[ast.stmt] = self.__class_node.body
        function_def_list: list[ast.FunctionDef] = list[ast.FunctionDef]()
        for stmt in stmts:
            self.__recursive_find_method_def(stmt, function_def_list)
        return function_def_list

    def __recursive_find_method_def(
            self,
            node: ast.AST,
            function_def_list: list[ast.FunctionDef]
    ) -> list[ast.FunctionDef]:
        if isinstance(node, ast.ClassDef):
            return []
        if isinstance(node, ast.FunctionDef):
            function_def_list.append(node)
            return []
        for child in ast.iter_child_nodes(node):
            self.__recursive_find_method_def(child, function_def_list)
        return function_def_list

    def search(self, fully_qualified_name_list: list[str]) -> Optional[Union[ClassObject, list[Function]]]:
        if len(fully_qualified_name_list) == 0:
            return self

        target_name: str = fully_qualified_name_list[0]

        method_list: list[Function] = list()

        for method in self.method_list:
            if not isinstance(method, FunctionSourceCode):
                return None
            if method.symbol.name == target_name:
                method_list.append(method)

        if len(method_list) != 0:
            return method_list

        return None

    def as_name(self, as_name: str) -> ClassObjectSourceCode:
        return ClassObjectSourceCode(
            self.__class_node,
            Symbol(as_name),
            self.param_list,
            self.method_list
        )

    @property
    def node(self) -> ast.ClassDef:
        return self.__class_node
