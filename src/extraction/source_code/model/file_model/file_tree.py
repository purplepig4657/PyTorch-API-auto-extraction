from __future__ import annotations

from typing import Optional

from src.extraction.source_code.model.file_model.file_leaf import FileLeaf


class FileTree:
    __name: str
    __directories: list[FileTree]
    __files: list[FileLeaf]

    def __init__(self, name: str, directories: list[FileTree], files: list[FileLeaf]):
        self.__name = name
        self.__directories = directories
        self.__files = files

    def file_search(self, fully_qualified_file_name: str) -> Optional[FileLeaf]:
        # file_name form example: torch.amp.autocast_mode, autocast_mode.py
        file_name_analyze_tmp: list[str] = fully_qualified_file_name.split('.')

        if len(file_name_analyze_tmp) == 1:  # Target file is in this tree
            target_file_name: str = file_name_analyze_tmp[0]
            for file in self.files:
                if file.name == target_file_name:
                    return file

            return None  # There is no leaf match with file name.

        if len(file_name_analyze_tmp) > 0:
            next_directory_name: str = file_name_analyze_tmp[0]
            for directory in self.directories:
                if directory.name == next_directory_name:
                    return directory.file_search('.'.join(file_name_analyze_tmp[1:]))

            return None  # There is no tree match with directory name.

        return None

    @property
    def name(self) -> str:
        return self.__name

    @property
    def directories(self) -> list[FileTree]:
        return self.__directories

    @property
    def files(self) -> list[FileLeaf]:
        return self.__files
