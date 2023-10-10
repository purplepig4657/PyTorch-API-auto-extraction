from lark import Transformer, Token

from src.common.model.generic_type import GenericType
from src.common.model.symbol import Symbol
from src.common.model.type import Type


class SourceCodeTypeParseTreeTransformer(Transformer):
    # noinspection PyMethodMayBeStatic
    def type(self, items: list[Token]) -> Token:
        return items[0]

    # noinspection PyMethodMayBeStatic
    def t(self, items: list[Token]) -> Token:
        return items[0]

    # noinspection PyMethodMayBeStatic
    def generic_type(self, items: list[Type]) -> Type:
        return GenericType(items[0].symbol, items[1:])

    # noinspection PyMethodMayBeStatic
    def list_type(self, items: list[Type]) -> Type:
        return GenericType(Symbol(""), items)  # 임시 제네릭으로 퉁침

    # noinspection PyMethodMayBeStatic
    def const_t(self, items: list[Type]) -> Type:
        return Type(items[0].symbol)

    # noinspection PyMethodMayBeStatic
    def type_list(self, items: list[Token]) -> Type:
        return Type(Symbol(items[0]))

    # noinspection PyMethodMayBeStatic
    def type_name(self, items: list[Token]) -> Type:
        return Type(Symbol(items[0]))
