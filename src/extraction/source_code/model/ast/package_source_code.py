from __future__ import annotations

import ast
from typing import Optional, Union

from src.common.model.class_object import ClassObject
from src.common.model.function import Function
from src.common.model.source_code.module import Module
from src.common.model.source_code.package import Package
from src.common.model.symbol import Symbol
from src.extraction.source_code.model.ast.class_object_source_code import ClassObjectSourceCode
from src.extraction.source_code.model.file_model.file_leaf import FileLeaf
from src.extraction.source_code.model.file_model.file_tree import FileTree
from src.extraction.source_code.model.ast.function_source_code import FunctionSourceCode
from src.extraction.source_code.model.ast.module_source_code import ModuleSourceCode


class PackageSourceCode(Package):

    __package_file_tree: FileTree
    __init_py: Optional[Module] = None

    def __init__(self, package_file_tree: FileTree):
        self.__package_file_tree = package_file_tree
        symbol: Symbol = Symbol(package_file_tree.name)
        package_list: list[Package] = self.__extract_all_package_list()
        module_list: list[Module] = self.__extract_all_module_list()
        super().__init__(symbol, package_list, module_list)

    def __extract_all_package_list(self) -> list[Package]:
        package_list: list[Package] = list[Package]()
        directories: list[FileTree] = self.__package_file_tree.directories
        for directory in directories:
            package_list.append(PackageSourceCode(directory))
        return package_list

    def __extract_all_module_list(self) -> list[Module]:
        module_list: list[Module] = list[Module]()
        files: list[FileLeaf] = self.__package_file_tree.files
        for file in files:
            module_source_code: ModuleSourceCode = ModuleSourceCode(file)
            module_list.append(module_source_code)
            if file.name == "__init__":
                self.__init_py = module_source_code
        return module_list

    def search(self, fully_qualified_name_list: list[str]) -> Optional[Union[Module, ClassObject, list[Function]]]:
        if len(fully_qualified_name_list) == 0:  # it points this package
            return self.__init_py

        target_name: str = fully_qualified_name_list[0]

        for package in self.package_list:
            if not isinstance(package, PackageSourceCode):  # just Type Checking
                return None
            if package.symbol.name == target_name:
                return package.search(fully_qualified_name_list[1:])

        for module in self.module_list:
            if not isinstance(module, ModuleSourceCode):  # just Type Checking
                return None
            if module.symbol.name == target_name:
                return module.search(fully_qualified_name_list[1:])

        if not isinstance(self.__init_py, ModuleSourceCode):  # just Type Checking
            return None
        else:
            result = self.__init_py.search(fully_qualified_name_list)

        if result is not None:
            return result

        return None

    def resolve_init_py(
            self,
            fully_qualified_name_list: list[str],
            root_package: PackageSourceCode
    ) -> None:
        for package in self.package_list:
            if isinstance(package, PackageSourceCode):
                fully_qualified_name_list.append(package.symbol.name)
                package.resolve_init_py(fully_qualified_name_list, root_package)
                fully_qualified_name_list.pop()

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
                path: list[str] = fully_qualified_name_list.copy()[1:]
                name: str = module_list[-1]
                resolved_path: list[str] = self.__path_resolve(level, name, module_list[:-1], path)
                result: Optional[Module] = root_package.search(resolved_path)  # only module can be out.
                if result is None:
                    continue
                function_list_len: int = len(result.function_list)
                for i in range(function_list_len):
                    self.__init_py.add_function(result.function_list[i])
                class_list_len: int = len(result.class_list)
                for i in range(class_list_len):
                    self.__init_py.add_class_object(result.class_list[i])
                continue

            for name_alias in import_names:
                path: list[str] = fully_qualified_name_list.copy()[1:]
                name: str = name_alias.name
                as_name: str = name_alias.asname if name_alias.asname is not None else name
                resolved_path: list[str] = self.__path_resolve(level, name, module_list, path)
                result: Optional[Union[ClassObject, list[Function]]] = root_package.search(resolved_path)

                if result is None:
                    continue
                if isinstance(result, ClassObjectSourceCode):
                    self.__init_py.add_class_object(result.as_name(as_name))
                if not isinstance(result, list):
                    continue
                for function in result:
                    if isinstance(function, FunctionSourceCode):
                        self.__init_py.add_function(function.as_name(as_name))

                # if isinstance(result, FunctionSourceCode):  # overloading 이 제대로 들어오지 않는 것을 확인 -> 은 아닐 수도
                #     self.__init_py.add_function(result.as_name(as_name))

        for package in self.package_list:
            if isinstance(package, PackageSourceCode):
                fully_qualified_name_list.append(package.symbol.name)
                package.resolve_init_py(fully_qualified_name_list, root_package)
                fully_qualified_name_list.pop()

        if self.__init_py is not None:
            self.__init_py.class_list = self.remove_duplicates(self.__init_py.class_list)
            self.__init_py.function_list = self.remove_duplicates(self.__init_py.function_list)

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
        if self.__init_py is None:
            return list()
        if not isinstance(self.__init_py, ModuleSourceCode):
            return list()
        stmts: list[ast.stmt] = self.__init_py.ast.body
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

    @property
    def init_py(self) -> Module:
        return self.__init_py
