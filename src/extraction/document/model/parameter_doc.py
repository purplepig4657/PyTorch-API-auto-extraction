from __future__ import annotations

import re
from functools import reduce
from typing import Tuple, Optional

from bs4 import Tag, ResultSet

from src.common.constant.pytorch_doc_constant import PyTorchDocConstant
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.common.model.value import Value
from src.extraction.document.model.type_doc import TypeDoc


class ParameterDoc(Parameter):

    def __init__(self, symbol: Symbol, default: Optional[Value], value_type: Optional[Type]):

        super().__init__(symbol, default, value_type)

    @classmethod
    def from_box(cls, parameter_tag: Tag) -> ParameterDoc:
        parameter_name, parameter_type, parameter_default_value = cls.__extract_parameter_info_from_box(parameter_tag)
        # print("## from box")
        # print(parameter_name, parameter_default_value, parameter_type)
        return cls(parameter_name, parameter_default_value, parameter_type)

    @classmethod
    def from_content(cls, parameter_tag: Tag) -> ParameterDoc:
        parameter_name, parameter_type, parameter_default_value = \
            cls.__extract_parameter_info_from_content(parameter_tag)
        # print("## from content")
        # print(parameter_name, parameter_default_value, parameter_type)
        return cls(parameter_name, parameter_default_value, parameter_type)

    @classmethod
    def __extract_parameter_info_from_content(cls, parameter_tag: Tag) \
            -> Tuple[Symbol, Optional[Type], Optional[Value[str]]]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.

        parameter_type: Optional[Type] = None
        parameter_default: Optional[Value[str]] = None

        parameter_name: str = parameter_tag.find(name="strong", recursive=False).text
        parameter_em_tag: ResultSet[Tag] = parameter_tag.select("em, a span")

        parameter_em_str_list: list[str] = [item.text.strip() for item in parameter_em_tag]

        # We do not handle 'deprecated'.
        parameter_em_str_list = [item for item in parameter_em_str_list if item not in ['deprecated']]

        # "a span" text can be existed on parameter description, not type.
        parameter_text_list: list[str] = parameter_tag.text.split('–')
        parameter_type_list = [item for item in parameter_em_str_list if item in parameter_text_list[0]]

        default_value: Optional[str] = None
        for text in parameter_type_list:
            if "default" in text:
                default_value = text.replace("default", "").replace("=", "").strip()
                parameter_type_list.remove(text)
                break

        match = re.search(r'\((.*)\)', parameter_text_list[0])

        parameter_symbol: Symbol = Symbol(parameter_name)
        if match:
            type_str: str = match.group(1).split(", default")[0]
            type_str = type_str.replace("(", "[")
            type_str = type_str.replace(")", "]")
            parameter_type = TypeDoc.from_content_type_str(type_str=type_str)
        else:
            print("Warning: There is no type in content")
        if default_value is not None:
            parameter_default = Value[str](default_value)

        if parameter_default is None:
            parameter_default = Value("None")
        if parameter_type is None:
            parameter_type = Type(Symbol("None"))

        return parameter_symbol, parameter_type, parameter_default

    @classmethod
    def __extract_parameter_info_from_box(cls, parameter_tag: Tag) \
            -> Tuple[Symbol, Optional[Type], Optional[Value[str]]]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        parameter_info: ResultSet[Tag] = parameter_tag.find_all(
            attrs={'class', PyTorchDocConstant.TORCH_PARAMETER_NAME_AND_TYPE_FROM_BOX_LITERAL},
            recursive=False
        )

        parameter_name: Optional[Symbol] = None
        parameter_type: Optional[Type] = None
        parameter_default_value: Optional[Value[str]] = None

        if len(parameter_info) == 0:
            # There is no information of parameter.
            parameter_name = Symbol("*")
            parameter_type = Type(Symbol("None"))
            parameter_default_value = Value("None")
            return parameter_name, parameter_type, parameter_default_value
        if len(parameter_info) == 1:
            # There is only name, no type.
            all_span: ResultSet[Tag] = parameter_info[0].find_all(name="span")
            if len(all_span) > 1:
                print("Warning: invalid doc, several text tag.")
            name: str = reduce(lambda acc, cur: acc + cur.text, all_span, "")
            parameter_name = Symbol(name)
        if len(parameter_info) > 1:
            # There is both name and type exist.
            all_span: ResultSet[Tag] = parameter_info[0].find_all(name="span")
            if len(all_span) > 1:
                print("Warning: invalid doc, several text tag.")
            name: str = reduce(lambda acc, cur: acc + cur.text, all_span, "")
            parameter_name = Symbol(name)
            type_tag: Tag = parameter_info[1].find(name="a")
            if type_tag is not None:
                parameter_type = TypeDoc.from_box_a_tag(type_tag)
            else:
                type_name: str = parameter_info[1].find(name="span").text
                parameter_type = TypeDoc.from_str(type_name)

        parameter_default_value_tag = parameter_tag.find(
            attrs={'class', PyTorchDocConstant.TORCH_PARAMETER_DEFAULT_VALUE_FROM_BOX_LITERAL},
            recursive=False
        )

        if parameter_default_value_tag is not None:
            all_span: ResultSet[Tag] = parameter_default_value_tag.find_all(name="span")
            if len(all_span) > 1:
                print("Warning: invalid doc, several text tag.")
            value: str = reduce(lambda acc, cur: acc + cur.text, all_span, "")
            parameter_default_value = Value(value)

        if '=' in parameter_name.name:
            name, default_value = parameter_name.name.split('=')
            parameter_name = Symbol(name)
            parameter_default_value = Value(default_value)
            print("Warning: invalid doc, default value was not divided tag.")

        if parameter_default_value is None:
            parameter_default_value = Value("None")
        if parameter_type is None:
            parameter_type = Type(Symbol("None"))

        return parameter_name, parameter_type, parameter_default_value
