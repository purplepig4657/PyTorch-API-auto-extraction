from bs4 import Tag
from lark import LarkError

from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.extraction.document.common.type_parser.parse_tree_transformer import ParseTreeTransformer
from src.extraction.document.common.type_parser.type_parser import TypeParser


class TypeDoc(Type):

    type_parser: TypeParser = TypeParser()
    parse_tree_transformer: ParseTreeTransformer = ParseTreeTransformer()

    def __init__(self, symbol: Symbol):
        super().__init__(symbol)

    @classmethod
    def from_box_a_tag(cls, type_tag: Tag):
        try:
            parse_tree = cls.type_parser.parse(type_tag.text)
        except LarkError:
            print("Warning: type that in content parsing error.")
            return Type.parse_error_type()
        result: Type = cls.parse_tree_transformer.transform(parse_tree)
        return result

    @classmethod
    def from_str(cls, name: str):
        return cls(Symbol(name))

    @classmethod
    def from_content_type_str(cls, type_str: str) -> Type:
        try:
            parse_tree = cls.type_parser.parse(type_str)
        except LarkError:
            print("Warning: type that in content parsing error.")
            return Type.parse_error_type()
        result: Type = cls.parse_tree_transformer.transform(parse_tree)
        return result
