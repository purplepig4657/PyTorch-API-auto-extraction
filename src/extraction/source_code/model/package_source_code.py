from __future__ import annotations

import ast
from typing import Optional, Union

from src.common.model.class_object import ClassObject
from src.common.model.function import Function
from src.common.model.source_code.module import Module
from src.common.model.source_code.package import Package
from src.common.model.symbol import Symbol
from src.extraction.source_code.model.class_object_source_code import ClassObjectSourceCode
from src.extraction.source_code.model.file_model.file_leaf import FileLeaf
from src.extraction.source_code.model.file_model.file_tree import FileTree
from src.extraction.source_code.model.function_source_code import FunctionSourceCode
from src.extraction.source_code.model.module_source_code import ModuleSourceCode


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

    def search(self, fully_qualified_name_list: list[str]) -> Optional[Union[Module, ClassObject, Function]]:
        if len(fully_qualified_name_list) == 0:  # it points this package
            return self.__init_py

        target_name: str = fully_qualified_name_list[0]

        if not isinstance(self.__init_py, ModuleSourceCode):
            return None
        else:
            result = self.__init_py.search(fully_qualified_name_list)

        if result is not None:
            return result

        for package in self.package_list:
            if not isinstance(package, PackageSourceCode):
                return None
            if package.symbol.name == target_name:
                return package.search(fully_qualified_name_list[1:])

        for module in self.module_list:
            if not isinstance(module, ModuleSourceCode):
                return None
            if module.symbol.name == target_name:
                return module.search(fully_qualified_name_list[1:])

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

            for name_alias in import_names:
                path: list[str] = fully_qualified_name_list.copy()[1:]
                name: str = name_alias.name
                as_name: str = name_alias.asname if name_alias.asname is not None else name
                result: Optional[Union[ClassObject, Function]]
                if level == -1:  # absolute path
                    module_list_tmp = module_list[1:]
                    module_list_tmp.append(name)
                    result = root_package.search(module_list_tmp)
                elif level == 0:  # relative path
                    path.extend(module_list)
                    path.append(name)
                    result = root_package.search(path)
                else:  # relative path
                    path = path[:-level]
                    path.extend(module_list)
                    path.append(name)
                    result = root_package.search(path)

                if result is None:
                    continue
                if isinstance(result, ClassObjectSourceCode):
                    self.__init_py.add_class_object(result.as_name(as_name))
                if isinstance(result, FunctionSourceCode):
                    self.__init_py.add_function(result.as_name(as_name))

        for package in self.package_list:
            if isinstance(package, PackageSourceCode):
                fully_qualified_name_list.append(package.symbol.name)
                package.resolve_init_py(fully_qualified_name_list, root_package)
                fully_qualified_name_list.pop()

    def __extract_import_from(self) -> list[ast.ImportFrom]:
        if self.__init_py is None:
            return list()
        if not isinstance(self.__init_py, ModuleSourceCode):
            return list()
        stmts: list[ast.stmt] = self.__init_py.ast.body
        import_from_list: list[ast.ImportFrom] = list[ast.ImportFrom]()
        for stmt in stmts:
            if isinstance(stmt, ast.ImportFrom):
                import_from_list.append(stmt)
        return import_from_list

    @property
    def init_py(self) -> Module:
        return self.__init_py
