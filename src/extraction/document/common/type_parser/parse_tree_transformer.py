from lark import Transformer, Token, v_args

from src.common.model.callable_type import CallableType
from src.common.model.generic_type import GenericType
from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.common.classified_result import classified_result


class ParseTreeTransformer(Transformer):

    def __init__(self):
        self.additional_arg = None

    # noinspection PyMethodMayBeStatic
    def type(self, items: list[Token]) -> Token:
        return items[0]

    # noinspection PyMethodMayBeStatic
    def _type(self, items: list[Token]) -> Token:
        return items[0]

    # noinspection PyMethodMayBeStatic
    def t(self, items: list[Token]) -> Token:
        return items[0]

    # noinspection PyMethodMayBeStatic
    def weird_optional_type(self, items: list[Type]) -> Type:
        return GenericType(Symbol("DocumentOptional"), items)

    # noinspection PyMethodMayBeStatic
    def weird_required_type(self, items: list[Type]) -> Type:
        return items[0]

    # noinspection PyMethodMayBeStatic
    def union_type(self, items: list[Type]) -> Type:
        return GenericType(Symbol("Union"), items)

    # noinspection PyMethodMayBeStatic
    def weird_delimeter_union_type(self, items: list[Type]) -> Type:
        classified_result["warning"]["break_format"]["unknown_delimiter"].append(self.additional_arg)
        return GenericType(Symbol("Union"), items)

    def transform_with_args(self, tree, additional_arg) -> Type:
        self.additional_arg = additional_arg
        return self.transform(tree)

    # noinspection PyMethodMayBeStatic
    def union_type_generic(self, items: list[Type]) -> Type:
        return GenericType(Symbol("Union"), items)

    # noinspection PyMethodMayBeStatic
    def callable_type_generic(self, items: list[Type]) -> Type:
        return GenericType(Symbol("Callable"), [GenericType(Symbol(""), items[:-1]), items[-1]])
        # return CallableType(Symbol("Callable"), parameter_type_list=items[:-1], return_type=items[-1])

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
    def tuple_type_generic(self, items: list[Type]) -> Type:
        return GenericType(Symbol("tuple"), items)

    # noinspection PyMethodMayBeStatic
    def generic_type(self, items: list[Type]) -> Type:
        return GenericType(items[0].symbol, items[1:])

    # noinspection PyMethodMayBeStatic
    def type_name(self, items: list[Token]) -> Type:
        return Type(Symbol(items[0]))

    # noinspection PyMethodMayBeStatic
    def type_list(self, items: list[Token]) -> Type:
        return Type(Symbol(items[0]))

    # noinspection PyMethodMayBeStatic
    def optional(self, items: list[Token]) -> Type:
        return Type(Symbol(items[0]))


# tree = TypeParser().parse("str, int, str, optional")
# print(ParseTreeTransformer().transform(tree))
# print(tree.pretty())
