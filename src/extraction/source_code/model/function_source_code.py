from __future__ import annotations

import ast
from typing import Optional, Type

from src.common.model.function import Function
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.extraction.source_code.model.parameter_source_code import ParameterSourceCode


class FunctionSourceCode(Function):

    __function_node: ast.FunctionDef

    def __init__(
            self,
            function_node: ast.FunctionDef,
            symbol: Symbol = None,
            param_list: list[Parameter] = None,
            return_type: Optional[Type] = None
    ):
        self.__function_node = function_node
        if symbol is None:
            symbol: Symbol = self.__extract_function_name()
        if param_list is None:
            param_list: list[Parameter] = self.__extract_param_list()
        if return_type is None:
            return_type: Optional[Type] = self.__extract_return_type()
        super().__init__(symbol, param_list, return_type)

    def __extract_function_name(self) -> Symbol:
        return Symbol(self.__function_node.name)

    def __extract_param_list(self) -> list[Parameter]:
        arguments: ast.arguments = self.__function_node.args
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

    def __extract_return_type(self) -> Optional[Type]:
        pass

    def as_name(self, as_name: str) -> FunctionSourceCode:
        return FunctionSourceCode(
            self.__function_node,
            Symbol(as_name),
            self.param_list,
            self.return_type
        )
