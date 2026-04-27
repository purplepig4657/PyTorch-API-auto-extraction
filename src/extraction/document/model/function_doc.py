from typing import Optional

from bs4 import Tag, ResultSet

from src.common.library_spec import LibrarySpec
from src.common.model.function import Function
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.common.model.type import Type
from src.extraction.document.common.doc_url_utils import DocUrlUtils
from src.extraction.document.model.parameter_doc import ParameterDoc
from src.extraction.document.model.type_doc import TypeDoc


class FunctionDoc(Function):

    def __init__(self, function_name: Symbol, function_tag: Tag, library_spec: LibrarySpec):
        # print(function_name)
        self.__library_spec = library_spec
        self.symbol = function_name if isinstance(function_name, Symbol) else Symbol(function_name)
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

        if len(parameter_list_from_content) == 0:
            result_return_type = return_type_from_content.merge(return_type_from_box)
            super().__init__(function_name, parameter_list_from_box, result_return_type)
            return

        if len(parameter_list_from_box) == 0:
            result_return_type = return_type_from_content.merge(return_type_from_box)
            super().__init__(function_name, parameter_list_from_content, result_return_type)
            return

        if len(parameter_list_from_box) != len(parameter_list_from_content):
            print(f"Warning: parameter count doesn't match: {function_name}")

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
                print(f"Warning: unmatched parameter, {function_name}, {box_parameter.symbol}")
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
                print(f"Warning: unmatched parameter, {function_name}, {cont_parameter.symbol}")
                result_parameter_list.append(cont_parameter)
            else:
                result_parameter_list.append(cont_parameter.merge(box_parameter))

        result_return_type = return_type_from_content.merge(return_type_from_box)

        super().__init__(function_name, result_parameter_list, result_return_type)

    def __extract_parameter_tag_list_from_box(self, function_tag: Tag) -> list[Tag]:
        torch_function_object: Optional[Tag] = self.__extract_definition_object(function_tag)
        if torch_function_object is None:
            return []
        return [
            child for child in torch_function_object.find_all(recursive=False)
            if DocUrlUtils.has_class(child, self.__library_spec.parameter_from_box_literal)
        ]

    # noinspection PyMethodMayBeStatic
    def __extract_parameter_list_from_box(self, parameter_tag_list: list[Tag]) -> list[Parameter]:
        parameter_list: list[Parameter] = list[Parameter]()
        for parameter_tag in parameter_tag_list:
            parameter = ParameterDoc.from_box(parameter_tag, self)
            if parameter.symbol.name in {"*", "/"}:
                continue
            parameter_list.append(parameter)
        return parameter_list

    def __extract_return_type_tag_from_box(self, function_tag: Tag) -> Optional[Tag]:
        torch_function_object: Optional[Tag] = self.__extract_definition_object(function_tag)
        if torch_function_object is None:
            return None
        return torch_function_object.find(
            lambda tag: isinstance(tag, Tag) and DocUrlUtils.has_class(tag, self.__library_spec.return_type_from_box_literal)
        )

    # noinspection PyMethodMayBeStatic
    def __extract_return_type_from_box(self, return_type_tag: Tag) -> Type:
        if return_type_tag is None:
            return Type.none_type()
        else:
            return TypeDoc.from_box_a_tag(return_type_tag, self, None)

    def __extract_parameter_tag_list_from_content(self, function_tag: Tag) -> list[Tag]:
        tag_list: list[Tag] = []
        field_map = self.__extract_field_map(function_tag)

        if "Parameters" in field_map:
            tag_list.extend(self.__extract_parameter_paragraphs(field_map["Parameters"]))
        if "Keyword Arguments" in field_map:
            tag_list.extend(self.__extract_parameter_paragraphs(field_map["Keyword Arguments"]))

        return [item for item in tag_list if isinstance(item, Tag)]

    # noinspection PyMethodMayBeStatic
    def __extract_parameter_list_from_content(self, parameter_tag_list: list[Tag]) -> list[Parameter]:
        parameter_list: list[Parameter] = list[Parameter]()
        for parameter_tag in parameter_tag_list:
            parameter_list.append(ParameterDoc.from_content(parameter_tag, self))
        return parameter_list

    def __extract_return_type_tag_from_content(self, function_tag: Tag) -> Optional[Tag]:
        field_map = self.__extract_field_map(function_tag)
        return field_map.get("Return type")

    # noinspection PyMethodMayBeStatic
    def __extract_return_type_from_content(self, return_type_tag: Tag) -> Type:
        if return_type_tag is None:
            return Type.none_type()
        else:
            return TypeDoc.from_content_type_str(return_type_tag.text, self, None)

    def __extract_definition_object(self, function_tag: Tag) -> Optional[Tag]:
        for child in function_tag.find_all(recursive=False):
            if DocUrlUtils.has_class(child, self.__library_spec.object_literal):
                return child
        return None

    def __extract_field_map(self, function_tag: Tag) -> dict[str, Tag]:
        torch_content_object = function_tag.find(
            lambda tag: isinstance(tag, Tag) and DocUrlUtils.has_class(tag, "field-list"),
            recursive=True
        )
        if torch_content_object is None:
            return {}

        if torch_content_object.name == "dl":
            result: dict[str, Tag] = {}
            current_dt: Optional[Tag] = None
            for child in torch_content_object.find_all(recursive=False):
                if child.name == "dt":
                    current_dt = child
                    continue
                if child.name == "dd" and current_dt is not None:
                    result[current_dt.text.strip().rstrip(":")] = child
                    current_dt = None
            return result

        content_items: list[Tag] = []
        content_items.extend(torch_content_object.find_all(attrs={"class": "field-odd"}, recursive=False))
        content_items.extend(torch_content_object.find_all(attrs={"class": "field-even"}, recursive=False))

        result: dict[str, Tag] = {}
        for i in range(0, len(content_items), 2):
            if i + 1 >= len(content_items):
                break
            result[content_items[i].text.strip().rstrip(":")] = content_items[i + 1]
        return result

    @staticmethod
    def __extract_parameter_paragraphs(content_tag: Tag) -> list[Tag]:
        if content_tag is None:
            return []

        list_tag = content_tag.find("ul", recursive=False)
        if list_tag is not None:
            return [
                paragraph for paragraph in
                [item.find("p", recursive=False) for item in list_tag.find_all("li", recursive=False)]
                if paragraph is not None
            ]

        paragraph_list = content_tag.find_all("p", recursive=False)
        if paragraph_list:
            return paragraph_list

        if content_tag.find("strong", recursive=False) is not None:
            return [content_tag]

        return []
