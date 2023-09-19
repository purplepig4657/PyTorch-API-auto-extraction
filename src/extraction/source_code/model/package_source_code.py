from typing import Optional, Union

from src.common.model.class_object import ClassObject
from src.common.model.function import Function
from src.common.model.method import Method
from src.common.model.source_code.module import Module
from src.common.model.source_code.package import Package
from src.common.model.symbol import Symbol
from src.extraction.source_code.model.file_model.file_leaf import FileLeaf
from src.extraction.source_code.model.file_model.file_tree import FileTree
from src.extraction.source_code.model.module_source_code import ModuleSourceCode


class PackageSourceCode(Package):

    __package_file_tree: FileTree
    __package_list: list[Package]
    __module_list: list[Module]
    __init_py: Module

    def __init__(self, package_file_tree: FileTree):
        self.__package_file_tree = package_file_tree
        symbol: Symbol = Symbol(package_file_tree.name)
        self.__package_list = self.__extract_all_package_list()
        self.__module_list = self.__extract_all_module_list()
        super().__init__(symbol, self.__package_list, self.__module_list)

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

        for package in self.__package_list:
            if not isinstance(package, PackageSourceCode):
                return None
            if package.symbol.name == target_name:
                return package.search(fully_qualified_name_list[1:])

        for module in self.__module_list:
            if not isinstance(module, ModuleSourceCode):
                return None
            if module.symbol.name == target_name:
                return module.search(fully_qualified_name_list[1:])

        return None

    def resolve_init_py(self) -> None:
        pass

    @property
    def init_py(self) -> Module:
        return self.__init_py
