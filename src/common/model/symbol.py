from __future__ import annotations


class Symbol:
    __name: str

    def __init__(self, name: str):
        self.__name = name

    @property
    def name(self):
        return self.__name

    def __eq__(self, other: Symbol) -> bool:
        return self.name == other.name

    def __str__(self) -> str:
        return f"\"{self.name}\""
