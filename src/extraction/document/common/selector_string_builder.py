from __future__ import annotations


class SelectorStringBuilder:
    __tag_literal: str
    __class_literal: str
    __id_literal: str

    def __init__(self, tag_literal: str = None, class_literal: str = None, id_literal: str = None):
        self.__tag_literal = tag_literal
        self.__class_literal = class_literal
        self.__id_literal = id_literal

    def __tag_literal_processing(self) -> str:
        if not self.__tag_literal:
            return ""

        return self.__tag_literal

    def __class_literal_processing(self) -> str:
        if not self.__class_literal:
            return ""

        class_list: list[str] = self.__class_literal.split()
        return '.' + (self.__class_literal if len(class_list) <= 1 else '.'.join(class_list))

    def __id_literal_processing(self) -> str:
        if not self.__id_literal:
            return ""

        substitution_list: dict[str, str] = {
            '.': '\\.',
            '>': '\\>'
        }

        substitution_result: str = self.__id_literal
        for target, result in substitution_list.items():
            substitution_result = substitution_result.replace(target, result)
        return '#' + substitution_result

    def build(self) -> str:
        tag_literal_processing_result: str = self.__tag_literal_processing()
        class_literal_processing_result: str = self.__class_literal_processing()
        id_literal_processing_result: str = self.__id_literal_processing()
        return tag_literal_processing_result + id_literal_processing_result + class_literal_processing_result

    def set_tag(self, tag_literal: str) -> SelectorStringBuilder:
        self.__tag_literal = tag_literal
        return self

    def set_class(self, class_literal: str) -> SelectorStringBuilder:
        self.__class_literal = class_literal
        return self

    def set_id(self, id_literal: str) -> SelectorStringBuilder:
        self.__id_literal = id_literal
        return self
