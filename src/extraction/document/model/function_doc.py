from typing import Optional

from bs4 import Tag, ResultSet

from src.common.constant.pytorch_doc_constant import PyTorchDocConstant
from src.common.model.function import Function
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.extraction.document.model.parameter_doc import ParameterDoc
from src.extraction.document.model.type_doc import TypeDoc


class FunctionDoc(Function):

    def __init__(self, function_name: Symbol, function_tag: Tag):
        print(function_name)
        parameter_tag_list_from_box: list[Tag] = self.__extract_parameter_tag_list_from_box(function_tag)
        parameter_list_from_box: list[Parameter] = self.__extract_parameter_list_from_box(parameter_tag_list_from_box)
        parameter_list_from_content: list[Tag] = self.__extract_parameter_tag_list_from_content(function_tag)
        parameter_list_from_content: list[Parameter] = \
            self.__extract_parameter_list_from_content(parameter_list_from_content)

        return_type_tag_from_box: Tag = self.__extract_return_type_tag_from_box(function_tag)
        return_type_from_box: Type = self.__extract_return_type_from_box(return_type_tag_from_box)
        return_type_tag_from_content = self.__extract_return_type_tag_from_content(function_tag)
        return_type_from_content = self.__extract_return_type_from_content(return_type_tag_from_content)

        result_parameter_list: list[Parameter] = list[Parameter]()
        result_return_type: Type

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

        result_return_type = return_type_from_content.merge(return_type_from_box)

        super().__init__(function_name, result_parameter_list, result_return_type)

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
    def __extract_return_type_tag_from_box(self, function_tag: Tag) -> Optional[Tag]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        torch_function_object: Tag = function_tag.find(
            attrs={'class', PyTorchDocConstant.TORCH_OBJECT_LITERAL},
            recursive=False
        )
        return_type_tag: Tag = torch_function_object.find(
            attrs={'class', PyTorchDocConstant.TORCH_RETURN_TYPE_FROM_BOX_LITERAL},
            recursive=True
        )
        return return_type_tag

    # noinspection PyMethodMayBeStatic
    def __extract_return_type_from_box(self, return_type_tag: Tag) -> Type:
        if return_type_tag is None:
            return Type.none_type()
        else:
            return TypeDoc.from_box_a_tag(return_type_tag)

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

        keyword_arguments_item_index: int = -1
        for i in range(0, len(content_items), 2):
            if 'Keyword Arguments' in content_items[i].text:
                keyword_arguments_item_index = i
                break

        tag_list: list[Tag] = list[Tag]()
        parameter_tag_list: list[Tag] = list[Tag]()
        keyword_arguments_tag_list: list[Tag] = list[Tag]()

        if parameter_item_index >= 0:
            # Parameter list is item next sibling of title item.
            parameter_content_list_item: Tag = content_items[parameter_item_index + 1]

            parameter_content_list_tag: Tag = parameter_content_list_item.find(name="ul", recursive=False)
            if parameter_content_list_tag is None:
                parameter_tag_list = list[Tag](parameter_content_list_item)
            else:
                parameter_tag_list = list(map(
                    lambda x: x.find(name="p", recursive=False),
                    parameter_content_list_tag.find_all(name="li", recursive=False)
                ))

        if keyword_arguments_item_index >= 0:
            # Parameter list is item next sibling of title item.
            keyword_arguments_content_list_item: Tag = content_items[keyword_arguments_item_index + 1]

            keyword_arguments_content_list_tag: Tag = \
                keyword_arguments_content_list_item.find(name="ul", recursive=False)
            if keyword_arguments_content_list_tag is None:
                keyword_arguments_tag_list = list[Tag](keyword_arguments_content_list_item)
            else:
                keyword_arguments_tag_list = list(map(
                    lambda x: x.find(name="p", recursive=False),
                    keyword_arguments_content_list_tag.find_all(name="li", recursive=False)
                ))

        tag_list.extend(parameter_tag_list)
        tag_list.extend(keyword_arguments_tag_list)

        tag_list: list[Tag] = [item for item in tag_list if not isinstance(item, str)]

        return tag_list

    # noinspection PyMethodMayBeStatic
    def __extract_parameter_list_from_content(self, parameter_tag_list: list[Tag]) -> list[Parameter]:
        parameter_list: list[Parameter] = list[Parameter]()
        for parameter_tag in parameter_tag_list:
            parameter_list.append(ParameterDoc.from_content(parameter_tag))
        return parameter_list

    # noinspection PyMethodMayBeStatic
    def __extract_return_type_tag_from_content(self, function_tag: Tag) -> Optional[Tag]:
        # Warning: This code is highly dependent on the PyTorch documentation HTML structure.
        # No need to delve deeply this code.
        torch_content_object: Tag = function_tag.find(
            attrs={'class', PyTorchDocConstant.TORCH_PARAMETER_FROM_CONTENT_LITERAL},
            recursive=True
        )

        if torch_content_object is None:
            return None

        content_items: ResultSet[Tag] = torch_content_object.find_all(
            attrs={'class', "field-odd"},
            recursive=False
        )
        content_items.extend(torch_content_object.find_all(attrs={'class', "field-even"}, recursive=False))
        return_type_item_index: int = -1
        for i in range(0, len(content_items), 2):
            if 'Return type' in content_items[i].text:
                return_type_item_index = i
                break

        if return_type_item_index < 0:
            return None

        # Parameter list is item next sibling of title item.
        return_type_item: Tag = content_items[return_type_item_index + 1]

        return return_type_item

    # noinspection PyMethodMayBeStatic
    def __extract_return_type_from_content(self, return_type_tag: Tag) -> Type:
        if return_type_tag is None:
            return Type.none_type()
        else:
            return TypeDoc.from_content_type_str(return_type_tag.text)
