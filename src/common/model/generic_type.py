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

    def __str__(self) -> str:
        return f"{{ symbol: {self.symbol}, generic_list: {list(map(str, self.generic_list))} }}"
