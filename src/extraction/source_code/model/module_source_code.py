import ast
from typing import Optional, Union

from src.common.model.class_object import ClassObject
from src.common.model.function import Function
from src.common.model.source_code.module import Module
from src.common.model.symbol import Symbol
from src.extraction.source_code.model.class_object_source_code import ClassObjectSourceCode
from src.extraction.source_code.model.file_model.file_leaf import FileLeaf
from src.extraction.source_code.model.function_source_code import FunctionSourceCode


class ModuleSourceCode(Module):

    __ast: ast.Module

    def __init__(self, module_file_leaf: FileLeaf):
        symbol: Symbol = Symbol(module_file_leaf.name)
        source_code: str = module_file_leaf.content
        self.__ast = ast.parse(source_code)
        class_object_list: list[ClassObject] = self.__extract_all_class_list()
        function_list: list[Function] = self.__extract_all_function_list()
        super().__init__(symbol, class_object_list, function_list, source_code)

    def __extract_all_class_list(self) -> list[ClassObject]:
        class_list: list[ClassObject] = list[ClassObject]()
        class_def_list: list[ast.ClassDef] = self.__collect_class_def()
        for class_def in class_def_list:
            class_list.append(ClassObjectSourceCode(class_def))
        return class_list

    def __extract_all_function_list(self) -> list[Function]:
        function_list: list[Function] = list[Function]()
        function_def_list: list[ast.FunctionDef] = self.__collect_function_def()
        function_assign_list: list[Symbol] = self.__collect_function_assign()
        for function_def in function_def_list:
            function_list.append(FunctionSourceCode(function_def))
        for function_assign in function_assign_list:
            function_list.append(FunctionSourceCode(
                function_node=None,
                symbol=function_assign,
                param_list=[],
                return_type=None
            ))
        return function_list

    def __collect_class_def(self) -> list[ast.ClassDef]:
        stmts: list[ast.stmt] = self.__ast.body
        class_def_list: list[ast.ClassDef] = list[ast.ClassDef]()
        for stmt in stmts:
            self.__recursive_find_class_def(stmt, class_def_list)
        return class_def_list

    def __recursive_find_class_def(
            self,
            node: ast.AST,
            class_def_list: list[ast.ClassDef]
    ) -> list[ast.ClassDef]:
        if isinstance(node, ast.ClassDef):
            class_def_list.append(node)
            return []
        for child in ast.iter_child_nodes(node):
            self.__recursive_find_class_def(child, class_def_list)
        return class_def_list

    def __collect_function_def(self) -> list[ast.FunctionDef]:
        stmts: list[ast.stmt] = self.__ast.body
        function_def_list: list[ast.FunctionDef] = list[ast.FunctionDef]()
        for stmt in stmts:
            self.__recursive_find_function_def(stmt, function_def_list)
        return function_def_list

    def __recursive_find_function_def(
            self,
            node: ast.AST,
            function_def_list: list[ast.FunctionDef]
    ) -> list[ast.FunctionDef]:
        if isinstance(node, ast.ClassDef):
            return []
        if isinstance(node, ast.FunctionDef):
            function_def_list.append(node)
            return []
        for child in ast.iter_child_nodes(node):
            self.__recursive_find_function_def(child, function_def_list)
        return function_def_list

    def __collect_function_assign(self) -> list[Symbol]:
        stmts: list[ast.stmt] = self.__ast.body
        function_assign_list: list[Symbol] = list[Symbol]()
        for stmt in stmts:
            self.__recursive_find_function_assign(stmt, function_assign_list)
        return function_assign_list

    def __recursive_find_function_assign(self, node: ast.AST, function_assign_list: list[Symbol]) -> list[Symbol]:
        if isinstance(node, ast.Assign):
            name_list: list[ast.expr] = node.targets  # Not exactly function. It has possibility to be function
            for name in name_list:
                if isinstance(name, ast.Name):
                    function_assign_list.append(Symbol(name.id))
        for child in ast.iter_child_nodes(node):
            self.__recursive_find_function_assign(child, function_assign_list)
        return function_assign_list

    def search(self, fully_qualified_name_list: list[str]) -> Optional[Union[Module, ClassObject, Function]]:
        if len(fully_qualified_name_list) == 0:  # it points this module
            return self

        target_name: str = fully_qualified_name_list[0]

        for class_object in self.class_list:
            if not isinstance(class_object, ClassObjectSourceCode):
                return None
            if class_object.symbol.name == target_name:
                return class_object.search(fully_qualified_name_list[1:])

        for function in self.function_list:
            if not isinstance(function, FunctionSourceCode):
                return None
            if function.symbol.name == target_name:
                return function

    @property
    def ast(self) -> ast.Module:
        return self.__ast
