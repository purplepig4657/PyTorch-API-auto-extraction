from __future__ import annotations
from typing import Union, TypeVar, Generic


T = TypeVar('T', bound=Union[int, str, None])


class Value(Generic[T]):
    __value: T

    def __init__(self, value: T) -> None:
        self.__value = value

    @classmethod
    def none_value(cls) -> Value:
        return cls("None")

    @property
    def value(self) -> T:
        return self.__value

    def __eq__(self, other: Value) -> bool:
        return self.value == other.value

    def __ne__(self, other: Value) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        if type(self.value) == int:
            return f"{self.value}"
        else:
            return f"\"{self.value}\""
