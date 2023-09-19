import ast
from typing import Optional, Union

from src.common.model.class_object import ClassObject
from src.common.model.function import Function
from src.common.model.method import Method
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.extraction.source_code.model.function_source_code import FunctionSourceCode
from src.extraction.source_code.model.method_source_code import MethodSourceCode


class ClassObjectSourceCode(ClassObject):

    __class_node: ast.ClassDef
    __method_list: list[Method]

    def __init__(self, class_node: ast.ClassDef):
        self.__class_node = class_node
        symbol: Symbol = self.__extract_class_name()
        param_list: list[Parameter] = self.__extract_param_list()
        self.__method_list = self.__extract_method_list()
        super().__init__(symbol, param_list, self.__method_list)

    def __extract_class_name(self) -> Symbol:
        return Symbol(self.__class_node.name)

    def __extract_param_list(self) -> list[Parameter]:
        pass

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
            if isinstance(stmt, ast.FunctionDef):
                function_def_list.append(stmt)
        return function_def_list

    def search(self, fully_qualified_name_list: list[str]) -> Optional[Union[ClassObject, Function]]:
        if len(fully_qualified_name_list) == 0:
            return self

        target_name: str = fully_qualified_name_list[0]

        for method in self.__method_list:
            if not isinstance(method, FunctionSourceCode):
                return None
            if method.symbol.name == target_name:
                return method
