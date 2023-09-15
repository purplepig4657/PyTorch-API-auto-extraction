from __future__ import annotations

from src.common.model.source_code.module import Module
from src.common.model.symbol import Symbol


class Package:
    __symbol: Symbol
    __package_list: list[Package]
    __module_list: list[Module]

    def __init__(self, symbol: Symbol, package_list: list[Package], module_list: list[Module]):
        self.__symbol = symbol
        self.__package_list = package_list
        self.__module_list = module_list

    @property
    def symbol(self) -> Symbol:
        return self.__symbol

    @property
    def package_list(self) -> list[Package]:
        return self.__package_list

    @property
    def module_list(self) -> list[Module]:
        return self.__module_list
