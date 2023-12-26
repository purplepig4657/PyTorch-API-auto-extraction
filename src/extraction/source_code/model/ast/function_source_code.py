from __future__ import annotations

import importlib
import inspect
import ast
from typing import Optional

from src.common.model.function import Function
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.extraction.source_code.model.ast.parameter_source_code import ParameterSourceCode
from src.extraction.source_code.model.ast.type_source_code import TypeSourceCode


class FunctionSourceCode(Function):

    __function_node: ast.FunctionDef

    __fully_qualified_name: str
    __function_inspect_signature: Optional[inspect.Signature]

    def __init__(
            self,
            last_fully_qualified_name: str,
            function_node: ast.FunctionDef,
            symbol: Symbol = None,
            param_list: list[Parameter] = None,
            return_type: Optional[Type] = None
    ):
        self.__function_node = function_node
        if symbol is None:
            symbol: Symbol = self.__extract_function_name()
        self.__fully_qualified_name = f"{last_fully_qualified_name}.{symbol.name}" \
            if last_fully_qualified_name != "" else symbol.name
        # self.__function_inspect_signature = self.__extract_function_inspect_signature()
        if param_list is None:
            param_list: list[Parameter] = self.__extract_param_list()
        if return_type is None:
            return_type: Optional[Type] = self.__extract_return_type()
        super().__init__(symbol, param_list, return_type)

    def __extract_function_name(self) -> Symbol:
        return Symbol(self.__function_node.name)

    def __extract_param_list(self) -> list[Parameter]:
        # if self.__function_inspect_signature is not None:
        #     return self.__extract_param_list_with_inspect()
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

    def __extract_return_type(self) -> Type:
        # if self.__function_inspect_signature is not None:
        #     return self.__extract_return_type_with_inspect()
        if self.__function_node is None:
            return TypeSourceCode.none_type()
        return TypeSourceCode.extract_type(self.__function_node.returns)

    def __extract_function_inspect_signature(self) -> Optional[inspect.Signature]:
        last_fully_qualified_name_tmp = self.__fully_qualified_name.split('.')
        last_fully_qualified_name = '.'.join(last_fully_qualified_name_tmp[:-1])
        object_name = last_fully_qualified_name_tmp[-1]
        try:
            return inspect.signature(getattr(importlib.import_module(last_fully_qualified_name), object_name))
        except Exception:
            return None

    def __extract_param_list_with_inspect(self) -> list[Parameter]:
        print(self.__fully_qualified_name, self.__function_inspect_signature)
        return ParameterSourceCode.extract_param_list_with_inspect(self.__function_inspect_signature.parameters)

    def __extract_return_type_with_inspect(self) -> Type:
        if '->' in str(self.__function_inspect_signature):
            type_str: str = str(self.__function_inspect_signature).split('->')[1].strip()
            return TypeSourceCode.extract_type_by_str(type_str)
        else:
            return Type.none_type()

    def as_name(self, as_name: str) -> FunctionSourceCode:
        return FunctionSourceCode(
            self.__fully_qualified_name,
            self.__function_node,
            Symbol(as_name),
            self.param_list,
            self.return_type
        )

    @property
    def node(self) -> ast.FunctionDef:
        return self.__function_node
