from __future__ import annotations

from functools import reduce
from typing import Tuple

from src.common.model.symbol import Symbol
from src.common.model.type import Type


class GenericType(Type):
    __generic_list = list[Type]

    def __init__(self, symbol: Symbol, generic_list: list[Type]) -> None:
        super().__init__(symbol)
        self.__generic_list = generic_list

    @property
    def generic_list(self) -> list[Type]:
        return self.__generic_list

    def __eq__(self, other: GenericType) -> bool:
        if not isinstance(other, GenericType):
            return False
        # if self.symbol.name == "Union":
        #     return reduce(
        #         lambda acc, cur: acc and cur,
        #         [self_item in other.generic_list for self_item in self.generic_list],
        #         True
        #     )
        return reduce(
            lambda acc, cur: acc and cur,
            [self_item == other_item for self_item, other_item in zip(self.generic_list, other.generic_list)],
            True
        )

    def equal(self, other: GenericType) -> Tuple[str, str]:  # other is document type
        if not isinstance(other, Type):
            return 'Error', ''
        if self.symbol != other.symbol:
            return 'Error', 'error'
        if not isinstance(other, GenericType):
            if self.symbol == other.symbol:
                return 'Warning', 'generic type is not specified.'
            else:
                return 'Error', 'error'
        match, warning, error = 0, 1, 2
        result = 0

        # if self.symbol == Symbol('Union'):
        #
        #     for other_t in other.generic_list:
        #         is_exist = False
        #         for self_t in self.generic_list:
        #             if self_t.equal(other_t)[0] == 'Match':
        #                 is_exist = True
        #                 break
        #         if not is_exist:
        #             result = max(result, 2)
        # else:
        for self_t, other_t in zip(self.generic_list, other.generic_list):
            equal_result = self_t.equal(other_t)
            if equal_result[0] == 'Match':
                result = max(result, match)
            elif equal_result[0] == 'Warning':
                result = max(result, warning)
            elif equal_result[0] == 'Error':
                result = max(result, error)

        if result == 0:
            return 'Match', ''
        elif result == 1:
            return 'Warning', ''
        else:
            return 'Error', ''

    def __str__(self) -> str:
        return f"{self.symbol}{list(map(str, self.generic_list))}"

    def to_json(self) -> str:
        return f"{{\"symbol\": {self.symbol.to_json()}, \"generic_list\": " \
               f"{[generic.to_json() for generic in self.generic_list]}}}"
