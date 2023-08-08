from bs4 import Tag

from src.common.model.symbol import Symbol
from src.common.model.type import Type


class TypeDoc(Type):

    def __init__(self, symbol: Symbol):
        super().__init__(symbol)

    @classmethod
    def from_a_tag(cls, type_tag: Tag):
        return cls(Symbol("asdf"))

    @classmethod
    def from_str(cls, name: str):
        return cls(Symbol(name))
