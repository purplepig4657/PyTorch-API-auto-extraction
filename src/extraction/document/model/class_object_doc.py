from __future__ import annotations

from typing import Optional

from bs4 import Tag, ResultSet

from src.common.constant.pytorch_doc_constant import PyTorchDocConstant
from src.common.model.class_object import ClassObject
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.extraction.document.model.parameter_doc import ParameterDoc


class ClassObjectDoc(ClassObject):

    def __init__(self, class_object_name: Symbol, class_object_tag: Tag):
        parameter_tag_list_from_box: list[Tag] = self.__extract_parameter_tag_list_from_box(class_object_tag)
        parameter_list_from_box: list[Parameter] = self.__extract_parameter_list_from_box(parameter_tag_list_from_box)
        parameter_list_from_content: list[Tag] = self.__extract_parameter_tag_list_from_content(class_object_tag)
        parameter_list_from_content: list[Parameter] = \
            self.__extract_parameter_list_from_content(parameter_list_from_content)

        result_parameter_list: list[Parameter] = list[Parameter]()

        if len(parameter_list_from_box) != len(parameter_list_from_content):
            print("Warning: parameter count doesn't match.")

        while len(parameter_list_from_box) > 0:
            box_parameter: Parameter = parameter_list_from_box[0]
            parameter_list_from_box.pop(0)
            cont_parameter: Optional[Parameter] = None

            for i in range(len(parameter_list_from_content)):
                if parameter_list_from_content[i].symbol == box_parameter.symbol:
                    cont_parameter = parameter_list_from_content[i]
                    parameter_list_from_content.pop(i)
                    break

            if cont_parameter is None:
                print(f"Warning: unmatched parameter, {box_parameter.symbol}")
                result_parameter_list.append(box_parameter)
            else:
                result_parameter_list.append(cont_parameter.merge(box_parameter))

        while len(parameter_list_from_content) > 0:
            cont_parameter: Parameter = parameter_list_from_content[0]
            parameter_list_from_content.pop(0)
            box_parameter: Optional[Parameter] = None

            for i in range(len(parameter_list_from_box)):
                if parameter_list_from_box[i].symbol == cont_parameter.symbol:
                    box_parameter = parameter_list_from_box[i]
                    parameter_list_from_box.pop(i)
                    break

            if box_parameter is None:
                print(f"Warning: unmatched parameter, {cont_parameter.symbol}")
                result_parameter_list.append(cont_parameter)
            else:
                result_parameter_list.append(cont_parameter.merge(box_parameter))

        super().__init__(class_object_name, result_parameter_list, [])

    # noinspection PyMethodMayBeStatic
    def __extract_parameter_tag_list_from_box(self, class_object_tag: Tag) -> list[Tag]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        torch_function_object: Tag = class_object_tag.find(
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
    def __extract_parameter_tag_list_from_content(self, class_object_tag: Tag) -> list[Tag]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        torch_content: Tag = class_object_tag.find(name="dd", recursive=False)
        torch_content_object: Tag = torch_content.find(
            attrs={'class', PyTorchDocConstant.TORCH_PARAMETER_FROM_CONTENT_LITERAL},
            recursive=False
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

