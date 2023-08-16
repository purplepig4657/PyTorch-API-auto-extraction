from __future__ import annotations

from src.common.model.symbol import Symbol


class Type:
    __symbol: Symbol

    def __init__(self, symbol: Symbol) -> None:
        self.__symbol = symbol

    @property
    def symbol(self) -> Symbol:
        return self.__symbol

    def __eq__(self, other: Type) -> bool:
        return self.symbol == other.symbol

    def __str__(self):
        return self.symbol.__str__()
