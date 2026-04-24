from __future__ import annotations

import re
from typing import Tuple, Optional, Union

from bs4 import Tag

from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.common.model.value import Value
from src.common.model.class_object import ClassObject
from src.common.model.function import Function
from src.extraction.document.model.type_doc import TypeDoc


class ParameterDoc(Parameter):

    def __init__(self, symbol: Symbol, default: Optional[Value], value_type: Optional[Type], parent_object: Union[ClassObject, Function]):
        self.parent_object = parent_object
        super().__init__(symbol, default, value_type)

    @classmethod
    def from_box(cls, parameter_tag: Tag, parent_object: Union[ClassObject, Function]) -> ParameterDoc:
        parameter_name, parameter_type, parameter_default_value = cls.__extract_parameter_info_from_box(parameter_tag, parent_object)
        # print("## from box")
        # print(parameter_name, parameter_default_value, parameter_type)
        return cls(parameter_name, parameter_default_value, parameter_type, parent_object)

    @classmethod
    def from_content(cls, parameter_tag: Tag, parent_object: Union[ClassObject, Function]) -> ParameterDoc:
        parameter_name, parameter_type, parameter_default_value = \
            cls.__extract_parameter_info_from_content(parameter_tag, parent_object)
        # print("## from content")
        # print(parameter_name, parameter_default_value, parameter_type)
        return cls(parameter_name, parameter_default_value, parameter_type, parent_object)

    @classmethod
    def __extract_parameter_info_from_content(cls, parameter_tag: Tag, parent_object: Union[ClassObject, Function]) \
            -> Tuple[Symbol, Optional[Type], Optional[Value[str]]]:
        parameter_type: Optional[Type] = None
        parameter_default: Optional[Value[str]] = None

        strong_tag = parameter_tag.find(name="strong", recursive=False)
        parameter_name = strong_tag.text.strip() if strong_tag is not None else parameter_tag.text.split("–")[0].strip()
        header_text = parameter_tag.text.split("–")[0]
        match = re.search(r"\((.*)\)", header_text)

        parameter_symbol: Symbol = Symbol(cls.__normalize_parameter_name(parameter_name))
        if match:
            type_str: str = match.group(1).split(", default")[0]
            tmp_object: Parameter = Parameter(parameter_symbol, parameter_default, parameter_type)
            parameter_type = TypeDoc.from_content_type_str(type_str=type_str, grand_parent_object=parent_object, parent_object=tmp_object)

        default_match = re.search(r"default\s*=?\s*([^)]+)", header_text)
        if default_match:
            parameter_default = Value[str](default_match.group(1).strip())

        if parameter_default is None:
            parameter_default = Value.none_value()
        if parameter_type is None:
            parameter_type = Type.none_type()

        return parameter_symbol, parameter_type, parameter_default

    @classmethod
    def __extract_parameter_info_from_box(cls, parameter_tag: Tag, parent_object: Union[ClassObject, Function]) \
            -> Tuple[Symbol, Optional[Type], Optional[Value[str]]]:
        raw_text = " ".join(parameter_tag.stripped_strings)
        if raw_text in {"*", "/"}:
            return Symbol(raw_text), Type.none_type(), Value.none_value()

        parameter_type: Optional[Type] = None
        parameter_default_value: Optional[Value[str]] = None

        if ":" in raw_text:
            name_part, type_part = raw_text.split(":", 1)
        else:
            name_part, type_part = raw_text, ""

        if "=" in name_part:
            name_part, default_part = name_part.split("=", 1)
            parameter_default_value = Value(default_part.strip())

        if "=" in type_part:
            type_part, default_part = type_part.split("=", 1)
            parameter_default_value = Value(default_part.strip())

        parameter_name = Symbol(cls.__normalize_parameter_name(name_part))
        if type_part.strip() != "":
            tmp_object: Parameter = Parameter(parameter_name, parameter_default_value, parameter_type)
            parameter_type = TypeDoc.from_content_type_str(type_part.strip(), parent_object, tmp_object)

        if parameter_default_value is None:
            parameter_default_value = Value.none_value()
        if parameter_type is None:
            parameter_type = Type.none_type()

        return parameter_name, parameter_type, parameter_default_value

    @staticmethod
    def __normalize_parameter_name(name: str) -> str:
        return name.replace(" ", "").lstrip("*")
