import ast
from typing import Optional

from lark import LarkError

from src.common.constant.source_code_type_mapping import SourceCodeTypeMapping
from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.extraction.source_code.common.type_parser.source_code_type_parse_tree_transformer import \
    SourceCodeTypeParseTreeTransformer
from src.extraction.source_code.common.type_parser.source_code_type_parser import SourceCodeTypeParser


class TypeSourceCode(Type):

    __type_parser: SourceCodeTypeParser = SourceCodeTypeParser()
    __parse_tree_transformer: SourceCodeTypeParseTreeTransformer = SourceCodeTypeParseTreeTransformer()

    def __init__(self, symbol: Symbol):
        super().__init__(symbol)

    @classmethod
    def extract_type(cls, annotation: Optional[ast.expr]) -> Type:
        if annotation is None:
            return Type.none_type()
        try:
            type_str: str = ast.unparse(annotation)
            type_str = SourceCodeTypeMapping.mapping(type_str)
            parse_tree = cls.__type_parser.parse(type_str)
        except LarkError:
            print("Warning: type that in content parsing error.")
            print(type_str)
            return Type.parse_error_type()
        return cls.__parse_tree_transformer.transform(parse_tree)

    @classmethod
    def extract_type_by_str(cls, type_str: str) -> Type:
        try:
            type_str = SourceCodeTypeMapping.mapping(type_str)
            parse_tree = cls.__type_parser.parse(type_str)
        except LarkError:
            print("Warning: type that in content parsing error.")
            print(type_str)
            return Type.parse_error_type()
        return cls.__parse_tree_transformer.transform(parse_tree)
