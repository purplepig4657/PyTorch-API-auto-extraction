from __future__ import annotations

from typing import Optional, Tuple

from bs4 import Tag, ResultSet

from src.common.constant.pytorch_doc_constant import PyTorchDocConstant
from src.common.model.class_object import ClassObject
from src.common.model.method import Method
from src.common.model.parameter import Parameter
from src.common.model.symbol import Symbol
from src.extraction.document.common.doc_url_utils import DocUrlUtils
from src.extraction.document.model.method_doc import MethodDoc
from src.extraction.document.model.parameter_doc import ParameterDoc


class ClassObjectDoc(ClassObject):

    def __init__(self, class_object_name: Symbol, class_object_tag: Tag):
        self.symbol = class_object_name if isinstance(class_object_name, Symbol) else Symbol(class_object_name)
        parameter_tag_list_from_box: list[Tag] = self.__extract_parameter_tag_list_from_box(class_object_tag)
        parameter_list_from_box: list[Parameter] = self.__extract_parameter_list_from_box(parameter_tag_list_from_box)
        parameter_list_from_content: list[Tag] = self.__extract_parameter_tag_list_from_content(class_object_tag)
        parameter_list_from_content: list[Parameter] = \
            self.__extract_parameter_list_from_content(parameter_list_from_content)

        method_name_list, method_tag_list = self.__extract_method_name_list_and_tag_list(class_object_tag)
        method_list: list[Method] = self.__extract_method_list(method_name_list, method_tag_list)

        result_parameter_list: list[Parameter] = list[Parameter]()

        for method in method_list:  # Class parameter definition is in __init__ method definition box.
            if method.symbol.name.split('.')[-1] == '__init__':
                result_parameter_list.extend(method.param_list)

        if len(parameter_list_from_content) == 0:
            result_parameter_list.extend(parameter_list_from_box)
            super().__init__(class_object_name, result_parameter_list, method_list)
            return

        if len(parameter_list_from_box) == 0:
            result_parameter_list.extend(parameter_list_from_content)
            super().__init__(class_object_name, result_parameter_list, method_list)
            return

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

        super().__init__(class_object_name, result_parameter_list, method_list)

    def __extract_parameter_tag_list_from_box(self, class_object_tag: Tag) -> list[Tag]:
        torch_function_object: Optional[Tag] = self.__extract_definition_object(class_object_tag)
        if torch_function_object is None:
            return []
        return [
            child for child in torch_function_object.find_all(recursive=False)
            if DocUrlUtils.has_class(child, PyTorchDocConstant.TORCH_PARAMETER_FROM_BOX_LITERAL)
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

    def __extract_parameter_tag_list_from_content(self, class_object_tag: Tag) -> list[Tag]:
        tag_list: list[Tag] = []
        field_map = self.__extract_field_map(class_object_tag)

        if "Parameters" in field_map:
            tag_list.extend(self.__extract_parameter_paragraphs(field_map["Parameters"]))
        if "Keyword Arguments" in field_map:
            tag_list.extend(self.__extract_parameter_paragraphs(field_map["Keyword Arguments"]))

        return [item for item in tag_list if isinstance(item, Tag)]

    def __extract_parameter_list_from_content(self, parameter_tag_list: list[Tag]) -> list[Parameter]:
        parameter_list: list[Parameter] = []
        for parameter_tag in parameter_tag_list:
            parameter_list.append(ParameterDoc.from_content(parameter_tag, self))
        return parameter_list

    def __extract_method_name_list_and_tag_list(self, class_object_tag: Tag) -> Tuple[list[Symbol], list[Tag]]:
        class_content: Tag = class_object_tag.find(name="dd", recursive=False)
        if class_content is None:
            return [], []
        method_tag_list: list[Tag] = [
            child for child in class_content.find_all(recursive=False)
            if DocUrlUtils.has_class(child, "py") and DocUrlUtils.has_class(child, "method")
        ]
        result_method_tag_list: list[Tag] = []
        name_list: list[Symbol] = []
        if len(method_tag_list) == 0:
            return name_list, method_tag_list
        for torch_method in method_tag_list:
            torch_method_object: Optional[Tag] = self.__extract_definition_object(torch_method)
            if torch_method_object is None:
                continue
            torch_method_name: str = torch_method_object.get('id')
            if torch_method_name is None:
                continue
            name_list.append(Symbol(torch_method_name))
            result_method_tag_list.append(torch_method)
        return name_list, result_method_tag_list

    def __extract_method_list(self, method_name_list: list[Symbol], method_tag_list: list[Tag]) -> list[Method]:
        method_list: list[Method] = []
        for name, tag in zip(method_name_list, method_tag_list):
            method_list.append(MethodDoc(name, tag))
        return method_list

    @staticmethod
    def __extract_definition_object(definition_tag: Tag) -> Optional[Tag]:
        for child in definition_tag.find_all(recursive=False):
            if DocUrlUtils.has_class(child, PyTorchDocConstant.TORCH_OBJECT_LITERAL):
                return child
        return None

    def __extract_field_map(self, class_object_tag: Tag) -> dict[str, Tag]:
        torch_content = class_object_tag.find(name="dd", recursive=False)
        if torch_content is None:
            return {}

        torch_content_object = torch_content.find(
            lambda tag: isinstance(tag, Tag) and DocUrlUtils.has_class(tag, "field-list"),
            recursive=False
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
