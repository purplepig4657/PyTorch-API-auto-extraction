import ast
from typing import Optional, Union

from src.common.model.class_object import ClassObject
from src.common.model.function import Function
from src.common.model.source_code.module import Module
from src.common.model.symbol import Symbol
from src.extraction.source_code.model.ast.class_object_source_code import ClassObjectSourceCode
from src.extraction.source_code.model.file_model.file_leaf import FileLeaf
from src.extraction.source_code.model.ast.function_source_code import FunctionSourceCode


class ModuleSourceCode(Module):

    __ast: ast.Module

    __fully_qualified_name: str

    def __init__(self, last_fully_qualified_name: str, module_file_leaf: FileLeaf):
        symbol: Symbol = Symbol(module_file_leaf.name)
        self.__fully_qualified_name = f"{last_fully_qualified_name}.{symbol.name}" \
            if last_fully_qualified_name != "" else symbol.name
        source_code: str = module_file_leaf.content
        self.__ast = ast.parse(source_code)
        class_object_list: list[ClassObject] = self.__extract_all_class_list()
        function_list: list[Function] = self.__extract_all_function_list()
        super().__init__(symbol, class_object_list, function_list, source_code)

    def __extract_all_class_list(self) -> list[ClassObject]:
        class_list: list[ClassObject] = list[ClassObject]()
        class_def_list: list[ast.ClassDef] = self.__collect_class_def()
        for class_def in class_def_list:
            class_list.append(ClassObjectSourceCode(self.__fully_qualified_name, class_def))
        return class_list

    def __extract_all_function_list(self) -> list[Function]:
        function_list: list[Function] = list[Function]()
        function_def_list: list[ast.FunctionDef] = self.__collect_function_def()
        function_assign_list: list[Symbol] = self.__collect_function_assign()
        for function_def in function_def_list:
            function_list.append(FunctionSourceCode(self.__fully_qualified_name, function_def))
        for function_assign in function_assign_list:
            function_list.append(FunctionSourceCode(
                self.__fully_qualified_name,
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

    def resolve_import(
            self,
            fully_qualified_name_list: list[str],
            root_package: 'PackageSourceCode'
    ) -> None:
        import_from_list: list[ast.ImportFrom] = self.__extract_import_from()
        for import_from in import_from_list:
            level: int = import_from.level - 1
            module: str = import_from.module
            if module is None:
                module_list = []
            else:
                module_list: list[str] = module.split('.')
            import_names: list[ast.alias] = import_from.names

            if import_names[0].name == '*':
                path: list[str] = fully_qualified_name_list.copy()[1:-1]
                name: str = module_list[-1]
                resolved_path: list[str] = self.__path_resolve(level, name, module_list[:-1], path)
                result: Optional[Module] = root_package.search(resolved_path)  # only module can be out.
                if result is None:
                    continue
                function_list_len: int = len(result.function_list)
                for i in range(function_list_len):
                    self.add_function(result.function_list[i])
                class_list_len: int = len(result.class_list)
                for i in range(class_list_len):
                    self.add_class_object(result.class_list[i])
                continue

            for name_alias in import_names:
                path: list[str] = fully_qualified_name_list.copy()[1:-1]
                name: str = name_alias.name
                as_name: str = name_alias.asname if name_alias.asname is not None else name
                resolved_path: list[str] = self.__path_resolve(level, name, module_list, path)
                result: Optional[Union[ClassObject, list[Function]]] = root_package.search(resolved_path)

                if result is None:
                    continue
                if isinstance(result, ClassObjectSourceCode):
                    self.add_class_object(result.as_name(as_name))
                if not isinstance(result, list):
                    continue
                for function in result:
                    if isinstance(function, FunctionSourceCode):
                        self.add_function(function.as_name(as_name))

        self.class_list = self.remove_duplicates(self.class_list)
        self.function_list = self.remove_duplicates(self.function_list)

    def resolve_class_inheritance(
            self,
            class_object: ClassObjectSourceCode
    ):
        class_bases: list[ast.expr] = class_object.node.bases
        for expr in class_bases:
            parent_name: Symbol = Symbol(ast.unparse(expr))
            for same_module_class_object in self.class_list:
                # 일단 같은 모듈에 있는(import 된 것 포함) class만 상속 가능..
                # parent class name 에 . 으로 붙여서 상속해놓은 건 제외
                if same_module_class_object.symbol == parent_name:
                    for parent_method in same_module_class_object.method_list:
                        same_name_method_exist = False
                        for method in class_object.method_list:
                            if method.symbol == parent_method.symbol:
                                same_name_method_exist = True
                                break
                        if same_name_method_exist:
                            continue
                        class_object.add_method(parent_method)
                    break

    @staticmethod
    def remove_duplicates(original_list):
        unique_list = []

        for item in original_list:
            is_duplicate = False
            for unique_item in unique_list:
                if item == unique_item:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_list.append(item)

        return unique_list

    @staticmethod
    def __path_resolve(level: int, name: str, module_list: list[str], path: list[str]) -> list[str]:
        if level == -1:  # absolute path
            module_list_tmp = module_list[1:]
            module_list_tmp.append(name)
            return module_list_tmp
        elif level == 0:  # relative path
            path.extend(module_list)
            path.append(name)
            return path
        else:  # relative path
            path = path[:-level]
            path.extend(module_list)
            path.append(name)
            return path

    def __extract_import_from(self) -> list[ast.ImportFrom]:
        stmts: list[ast.stmt] = self.ast.body
        import_from_list: list[ast.ImportFrom] = list[ast.ImportFrom]()
        for stmt in stmts:
            self.__recursive_find_import_from(stmt, import_from_list)
        return import_from_list

    def __recursive_find_import_from(
            self,
            node: ast.AST,
            import_from_list: list[ast.ImportFrom]
    ) -> list[ast.ImportFrom]:
        if isinstance(node, ast.ImportFrom):
            import_from_list.append(node)
        for child in ast.iter_child_nodes(node):
            self.__recursive_find_import_from(child, import_from_list)
        return import_from_list

    def search(self, fully_qualified_name_list: list[str]) -> Optional[Union[Module, ClassObject, list[Function]]]:
        if len(fully_qualified_name_list) == 0:  # it points this module
            return self

        target_name: str = fully_qualified_name_list[0]

        for class_object in self.class_list:
            if not isinstance(class_object, ClassObjectSourceCode):
                return None
            if class_object.symbol.name == target_name:
                return class_object.search(fully_qualified_name_list[1:])

        function_list: list[Function] = list()

        for function in self.function_list:
            if not isinstance(function, FunctionSourceCode):
                return None
            if function.symbol.name == target_name:
                function_list.append(function)

        if len(function_list) != 0:
            return function_list

        return None

    @property
    def ast(self) -> ast.Module:
        return self.__ast
