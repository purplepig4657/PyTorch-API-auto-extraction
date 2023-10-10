import os

from lark import Lark, Tree, Token


class SourceCodeTypeParser:

    __parser: Lark
    __GRAMMAR_PATH = f"{os.path.dirname(os.path.realpath(__file__))}/python_source_code_type_grammar.lark"

    def __init__(self):
        self.__parser = Lark.open(self.__GRAMMAR_PATH, start='type')

    def parse(self, text: str) -> Tree[Token]:
        return self.__parser.parse(text)
