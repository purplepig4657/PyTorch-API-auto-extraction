import ast

from src.common.model.method import Method
from src.extraction.source_code.model.function_source_code import FunctionSourceCode


class MethodSourceCode(FunctionSourceCode, Method):

    def __init__(self, function_node: ast.FunctionDef):
        super().__init__(function_node)
