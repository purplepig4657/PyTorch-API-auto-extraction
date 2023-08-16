from lark import Transformer, Token

from src.common.model.generic_type import GenericType
from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.common.model.union_type import UnionType
from src.extraction.document.common.type_parser.type_parser import TypeParser


class ParseTreeTransformer(Transformer):
    # noinspection PyMethodMayBeStatic
    def type(self, item: list[Token]) -> Token:
        return item[0]

    # noinspection PyMethodMayBeStatic
    def t(self, item: list[Token]) -> Token:
        return item[0]

    # noinspection PyMethodMayBeStatic
    def union_type(self, items: list[Type]) -> Type:
        return GenericType(Symbol("Union"), items)

    # noinspection PyMethodMayBeStatic
    def union_type_generic(self, items: list[Type]) -> Type:
        return GenericType(Symbol("Union"), items)

    # noinspection PyMethodMayBeStatic
    def optional_type_generic(self, items: list[Type]) -> Type:
        return GenericType(Symbol("Optional"), items)

    # noinspection PyMethodMayBeStatic
    def iterable_type_generic(self, items: list[Type]) -> Type:
        return GenericType(Symbol("Iterable"), items)

    # noinspection PyMethodMayBeStatic
    def list_type_generic(self, items: list[Type]) -> Type:
        return GenericType(Symbol("list"), items)

    # noinspection PyMethodMayBeStatic
    def generic_type(self, items: list[Type]) -> Type:
        return GenericType(items[0].symbol, items[1:])

    # noinspection PyMethodMayBeStatic
    def type_name(self, item: list[Token]) -> Type:
        return Type(Symbol(item[0]))

    # noinspection PyMethodMayBeStatic
    def type_list(self, item: list[Token]) -> Type:
        return Type(Symbol(item[0]))

    # noinspection PyMethodMayBeStatic
    def optional(self, item: list[Token]) -> Type:
        return Type(Symbol(item[0]))


# tree = TypeParser().parse("dict[int, str] or Optional[int] or iterable of int, list of str")
# print(ParseTreeTransformer().transform(tree))
# print(tree.pretty())
