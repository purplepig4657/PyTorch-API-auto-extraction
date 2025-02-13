from bs4 import Tag
from lark import LarkError

from typing import Union

from src.common.constant.doc_type_mapping import DocTypeMapping
from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.common.model.parameter import Parameter
from src.common.model.function import Function
from src.common.model.class_object import ClassObject
from src.extraction.document.common.type_parser.parse_tree_transformer import ParseTreeTransformer
from src.extraction.document.common.type_parser.type_parser import TypeParser


class TypeDoc(Type):

    type_parser: TypeParser = TypeParser()
    parse_tree_transformer: ParseTreeTransformer = ParseTreeTransformer()

    def __init__(
            self, 
            symbol: Symbol, 
            grand_parent_object: Union[Function, ClassObject] = None, 
            parent_object: Parameter = None
        ):
        self.grand_parent_object = grand_parent_object
        self.parent_object = parent_object
        super().__init__(symbol)

    @classmethod
    def from_box_a_tag(cls, type_tag: Tag, grand_parent_object: Union[Function, ClassObject], parent_object: Parameter):
        try:
            type_str: str = type_tag.text
            type_str = DocTypeMapping.mapping(type_str, grand_parent_object, parent_object)
            parse_tree = cls.type_parser.parse(type_str)
        except LarkError:
            print("Warning: type that in content parsing error.")
            return Type.parse_error_type()
        result: Type = cls.parse_tree_transformer.transform_with_args(parse_tree, 
                            additional_arg=f"{grand_parent_object.symbol.name}:{parent_object.symbol.name if parent_object is not None else 'return_type'}")
        # t: TypeDoc = cls(result.symbol, grand_parent_object, parent_object)
        return result

    @classmethod
    def from_str(cls, name: str, grand_parent_object: Union[Function, ClassObject], parent_object: Parameter):
        name = DocTypeMapping.mapping(name, grand_parent_object, parent_object)
        return cls(Symbol(name), parent_object)

    @classmethod
    def from_content_type_str(cls, type_str: str, grand_parent_object: Union[Function, ClassObject], parent_object: Parameter) -> Type:
        try:
            type_str = DocTypeMapping.mapping(type_str, grand_parent_object, parent_object)
            parse_tree = cls.type_parser.parse(type_str)
        except LarkError:
            print("Warning: type that in content parsing error.")
            return Type.parse_error_type()
        result: Type = cls.parse_tree_transformer.transform_with_args(parse_tree, 
                            additional_arg=f"{grand_parent_object.symbol.name}:{parent_object.symbol.name if parent_object is not None else 'return_type'}")
        # t: TypeDoc = cls(result.symbol, grand_parent_object, parent_object)
        return result
