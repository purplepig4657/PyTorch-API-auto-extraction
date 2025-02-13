from __future__ import annotations

from src.common.model.method import Method
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol


class ClassObject:
    __symbol: Symbol
    __param_list: list[Parameter]
    __method_list: list[Method]

    def __init__(self, symbol: Symbol, param_list: list[Parameter], method_list: list[Method]) -> None:
        self.__symbol = symbol
        self.__param_list = param_list
        self.__method_list = method_list

    def add_method(self, method: Method):
        self.method_list.append(method)

    @property
    def symbol(self) -> Symbol:
        return self.__symbol

    @property
    def param_list(self) -> list[Parameter]:
        return self.__param_list

    @property
    def method_list(self) -> list[Method]:
        return self.__method_list

    @symbol.setter
    def symbol(self, symbol):
        self.__symbol = symbol

    def to_json(self) -> str:
        return f"{{ \"symbol\": {self.symbol.to_json()}, \"param_list\": " \
               f"{[param.to_json() for param in self.param_list]}, " \
               f"\"method_list\": {[method.to_json() for method in self.method_list]} }}"

    def __str__(self) -> str:
        return f"{self.symbol}({list(map(str, self.param_list))})"

    def __eq__(self, other: ClassObject):
        if len(self.param_list) != len(other.param_list):
            return False
        for self_parameter, other_parameter in zip(self.param_list, other.param_list):
            if self_parameter != other_parameter:
                return False
        for self_method, other_method in zip(self.method_list, other.method_list):
            if self_method != other_method:
                return False
        if self.symbol != other.symbol:
            return False
        return True
