import ast

from src.common.model.class_object import ClassObject
from src.common.model.method import Method
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol


class ClassObjectSourceCode(ClassObject):

    __class_node: ast.AST

    def __init__(self, class_node: ast.AST):
        symbol: Symbol = self.__extract_class_name()
        param_list: list[Parameter] = self.__extract_param_list()
        method_list: list[Method] = self.__extract_method_list()
        self.__class_node = class_node
        super().__init__(symbol, param_list, method_list)

    def __extract_class_name(self) -> Symbol:
        pass

    def __extract_param_list(self) -> list[Parameter]:
        pass

    def __extract_method_list(self) -> list[Method]:
        pass
