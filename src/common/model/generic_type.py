from src.common.model.symbol import Symbol
from src.common.model.type import Type


class GenericType(Type):
    __type_list = list[Type]

    def __init__(self, symbol: Symbol, type_list: list[Type]) -> None:
        super().__init__(symbol)
        self.__type_list = type_list

    @property
    def type_list(self) -> list[Type]:
        return self.__type_list

    def __str__(self) -> str:
        return f"{self.symbol}{list(map(str, self.type_list))}"
