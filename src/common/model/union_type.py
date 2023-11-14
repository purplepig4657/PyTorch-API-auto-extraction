from src.common.model.symbol import Symbol
from src.common.model.type import Type


class UnionType(Type):
    __union_list: list[Type]

    def __init__(self, symbol: Symbol, union_list: list[Type]):
        super().__init__(symbol)
        self.__union_list = union_list

    @property
    def union_list(self) -> list[Type]:
        return self.__union_list

    def __eq__(self, other: Type) -> bool:
        if not isinstance(other, UnionType):
            return False
        for t in self.union_list:
            if t not in other.union_list:
                return False
        return True

    def __str__(self) -> str:
        return f"{{\"symbol\": {self.symbol}, \"union_list\": {list(map(str, self.union_list))}}}"
