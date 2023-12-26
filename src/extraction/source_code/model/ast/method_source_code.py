import ast

from src.common.model.method import Method
from src.extraction.source_code.model.ast.function_source_code import FunctionSourceCode


class MethodSourceCode(FunctionSourceCode, Method):

    def __init__(self, last_fully_qualified_name: str, function_node: ast.FunctionDef):
        super().__init__(last_fully_qualified_name, function_node)
