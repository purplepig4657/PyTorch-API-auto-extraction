from lark import Transformer, Token

from src.common.model.generic_type import GenericType
from src.common.model.symbol import Symbol
from src.common.model.type import Type

# import os
# 
# from lark import Lark, Tree, Token

# class Symbol:
#     def __init__(self, name: str):
#         self.name = name
# 
# class Type:
#     def __init__(self, symbol):
#         self.symbol = symbol
# 
# class GenericType(Type):
#     def __init__(self, symbol, items):
#         super().__init__(symbol)
#         self.items = items


class SourceCodeTypeParseTreeTransformer(Transformer):
    # noinspection PyMethodMayBeStatic
    def type(self, items: list[Token]) -> Token:
        return items[0]

    # noinspection PyMethodMayBeStatic
    def t(self, items: list[Token]) -> Token:
        return items[0]

    # noinspection PyMethodMayBeStatic
    def generic_type(self, items: list[Type]) -> Type:
        # if items[0].symbol.name == "Union" and items[-1].symbol.name == "None":
        #     return GenericType(Symbol("Optional"), [GenericType(items[0].symbol.name, items[1:])])
        # if items[0].symbol.name == "Union":
        #     union_list: list[Type] = list()
        #     for item in items[1:]:
        #         if isinstance(item, GenericType) and item.symbol.name == "Union":
        #             union_list.extend(item.generic_list)
        #         else:
        #             union_list.append(item)
        #     return GenericType(items[0].symbol, union_list)
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

# class SourceCodeTypeParser:

#     __parser: Lark
#     __GRAMMAR_PATH = f"{os.path.dirname(os.path.realpath(__file__))}/python_source_code_type_grammar.lark"

#     def __init__(self):
#         self.__parser = Lark.open(self.__GRAMMAR_PATH, start='type')

#     def parse(self, text: str) -> Tree[Token]:
#         return self.__parser.parse(text)


# parser = SourceCodeTypeParser()
# print(parser.parse('Union[str, Iterable[str]]'))
# transformer = SourceCodeTypeParseTreeTransformer()
# print(transformer.transform(parser.parse('Union[str, Iterable[str]]')))
# tmp = transformer.transform(parser.parse('Union[str, Iterable[str]]'))
