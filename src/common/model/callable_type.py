from __future__ import annotations

from functools import reduce

from src.common.model.symbol import Symbol
from src.common.model.type import Type


class CallableType(Type):
    __parameter_type_list: list[Type]
    __return_type: Type

    def __init__(self, symbol: Symbol, parameter_type_list: list[Type], return_type: Type):
        super().__init__(symbol)
        self.__parameter_type_list = parameter_type_list
        self.__return_type = return_type

    def __eq__(self, other: CallableType) -> bool:
        if not isinstance(other, CallableType):
            return False
        return reduce(
            lambda acc, cur: acc and cur,
            [self_item in other.parameter_type_list for self_item in self.parameter_type_list],
            True
        ) and self.return_type == other.return_type

    def __str__(self) -> str:
        return f"{{ \"symbol\": {self.symbol}, \"parameter_type_list\": {list(map(str, self.parameter_type_list))}, " \
               f"\"return_type\": {self.return_type} }}"

    @property
    def parameter_type_list(self) -> list[Type]:
        return self.__parameter_type_list

    @property
    def return_type(self) -> Type:
        return self.__return_type
