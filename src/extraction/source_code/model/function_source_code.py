import ast
from typing import Optional, Type

from src.common.model.function import Function
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol


class FunctionSourceCode(Function):

    __function_node: ast.AST

    def __init__(self, function_node: ast.AST):
        symbol: Symbol = self.__extract_function_name()
        param_list: list[Parameter] = self.__extract_param_list()
        return_type: Optional[Type] = self.__extract_return_type()
        self.__function_node = function_node
        super().__init__(symbol, param_list, return_type)

    def __extract_function_name(self) -> Symbol:
        pass

    def __extract_param_list(self) -> list[Parameter]:
        pass

    def __extract_return_type(self) -> Optional[Type]:
        pass
