from bs4 import Tag

from src.common.model.method import Method
from src.common.model.symbol import Symbol
from src.extraction.document.model.function_doc import FunctionDoc


class MethodDoc(FunctionDoc, Method):
    def __init__(self, method_name: Symbol, method_tag: Tag):
        super().__init__(method_name, method_tag)
