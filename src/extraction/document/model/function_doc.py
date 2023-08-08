from functools import reduce

from bs4 import Tag, ResultSet

from src.common.constant.pytorch_doc_constant import PyTorchDocConstant
from src.common.model.function import Function
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.common.model.value import Value
from src.extraction.document.model.parameter_doc import ParameterDoc
from src.extraction.document.model.type_doc import TypeDoc


class FunctionDoc(Function):

    def __init__(self, function_name: Symbol, function_tag: Tag):
        print(function_name)
        parameter_tag_list_from_box: ResultSet[Tag] = self.__extract_parameter_tag_list_from_box(function_tag)
        parameter_list_from_box: list[Parameter] = self.__extract_parameter_list_from_box(parameter_tag_list_from_box)

    # noinspection PyMethodMayBeStatic
    def __extract_parameter_tag_list_from_box(self, function_tag: Tag) -> ResultSet[Tag]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        torch_function_object: Tag = function_tag.find(
            attrs={'class', PyTorchDocConstant.TORCH_OBJECT_LITERAL},
            recursive=False
        )
        parameter_tag_list: ResultSet[Tag] = torch_function_object.find_all(
            attrs={'class', PyTorchDocConstant.TORCH_PARAMETER_FROM_BOX_LITERAL},
            recursive=False
        )

        return parameter_tag_list

    # noinspection PyMethodMayBeStatic
    def __extract_parameter_list_from_box(self, parameter_tag_list: list[Tag]) -> list[Parameter]:
        parameter_list: list[Parameter] = list[Parameter]()
        for parameter_tag in parameter_tag_list:
            parameter_list.append(ParameterDoc.from_box(parameter_tag))
        return parameter_list

    # noinspection PyMethodMayBeStatic
    def __extract_parameter_tag_list_from_content(self, function_tag: Tag) -> ResultSet[Tag]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        pass

    # noinspection PyMethodMayBeStatic
    def __extract_parameter_list_from_content(self, parameter_tag_list: list[Tag]) -> list[Parameter]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        pass
