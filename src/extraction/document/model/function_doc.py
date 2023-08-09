from bs4 import Tag, ResultSet

from src.common.constant.pytorch_doc_constant import PyTorchDocConstant
from src.common.model.function import Function
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.extraction.document.model.parameter_doc import ParameterDoc


class FunctionDoc(Function):

    def __init__(self, function_name: Symbol, function_tag: Tag):
        print(function_name)
        parameter_tag_list_from_box: list[Tag] = self.__extract_parameter_tag_list_from_box(function_tag)
        parameter_list_from_box: list[Parameter] = self.__extract_parameter_list_from_box(parameter_tag_list_from_box)
        parameter_list_from_content: list[Tag] = self.__extract_parameter_tag_list_from_content(function_tag)
        parameter_list_from_content: list[Parameter] = \
            self.__extract_parameter_list_from_content(parameter_list_from_content)

    # noinspection PyMethodMayBeStatic
    def __extract_parameter_tag_list_from_box(self, function_tag: Tag) -> list[Tag]:
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
    def __extract_parameter_tag_list_from_content(self, function_tag: Tag) -> list[Tag]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        torch_content_object: Tag = function_tag.find(
            attrs={'class', PyTorchDocConstant.TORCH_PARAMETER_FROM_CONTENT_LITERAL},
            recursive=True
        )

        if torch_content_object is None:
            return list[Tag]()

        content_items: ResultSet[Tag] = torch_content_object.find_all(
            attrs={'class', "field-odd"},
            recursive=False
        )
        content_items.extend(torch_content_object.find_all(attrs={'class', "field-even"}, recursive=False))
        parameter_item_index: int = -1
        for i in range(0, len(content_items), 2):
            if 'Parameters' in content_items[i].text:
                parameter_item_index = i
                break

        if parameter_item_index < 0:
            return list[Tag]()

        # Parameter list is item next sibling of title item.
        parameter_content_list_item: Tag = content_items[parameter_item_index + 1]

        parameter_content_list_tag: Tag = parameter_content_list_item.find(name="ul", recursive=False)
        parameter_tag_list: list[Tag]
        if parameter_content_list_tag is None:
            parameter_tag_list = list[Tag](parameter_content_list_item)
        else:
            parameter_tag_list = list(map(
                lambda x: x.find(name="p", recursive=False),
                parameter_content_list_tag.find_all(name="li", recursive=False)
            ))

        parameter_tag_list: list[Tag] = [item for item in parameter_tag_list if not isinstance(item, str)]

        return parameter_tag_list

    # noinspection PyMethodMayBeStatic
    def __extract_parameter_list_from_content(self, parameter_tag_list: list[Tag]) -> list[Parameter]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        parameter_list: list[Parameter] = list[Parameter]()
        for parameter_tag in parameter_tag_list:
            parameter_list.append(ParameterDoc.from_content(parameter_tag))
        return parameter_list
