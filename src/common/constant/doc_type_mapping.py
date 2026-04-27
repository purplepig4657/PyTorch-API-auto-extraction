import re
from typing import Union

from src.common.model.function import Function
from src.common.model.parameter import Parameter
from src.common.model.class_object import ClassObject
from src.common.classified_result import classified_result


class DocTypeMapping:

    __MAPPING_TABLE = {
        'int64': 'int',  # Is this warning about builtin type ?
        'int32': 'int',  # Is this warning about builtin type ?
        'Dict': 'dict',
        '_dtype': 'dtype',
        '_device': 'device',
        '_qscheme': 'qscheme',
        '_layout': 'layout',
        '_size': "Union[torch.Size, List[int], Tuple[int, ...]]",
        'torch.Size': 'Size',
        'torch.layout': 'layout',
        'torch.dtype': 'dtype',
        'torch.device': 'device',
        'torch.memory_format': 'memory_format',
        'torch.Generator': 'Generator',
        'torch.nn.Module': 'Module',
        'torch.nn.Optimizer': 'Optimizer',
        'torch.nn.Parameter': 'Parameter',
        'torch._C._monitor.Aggregation': 'Aggregation',
        'torch._C.Value': 'Value',
        'torch.fx.GraphModule': 'GraphModule',
        'torch.jit.ScriptModule': 'ScriptModule',
        'torch._C.PyTorchFileReader': 'PyTorchFileReader',
        'torch.Tensor': 'Tensor',
        'torch.futures.Future': 'Future',
        'torch.cuda.memory._CUDAAllocator': '_CUDAAllocator',
        'torch.utils.hooks.RemovableHandle': 'RemovableHandle',
        '_size_any_t': 'Union[int, Tuple[int, ...]]',
        '_size_1_t': 'Union[int, Tuple[int]]',
        '_size_2_t': 'Union[int, Tuple[int, int]]',
        '_size_3_t': 'Union[int, Tuple[int, int, int]]',
        '_size_4_t': 'Union[int, Tuple[int, int, int, int]]',
        '_size_5_t': 'Union[int, Tuple[int, int, int, int, int]]',
        '_size_6_t': 'Union[int, Tuple[int, int, int, int, int, int]]',
        '_ratio_any_t': 'Union[float, Tuple[float, ...]]',
        '_ratio_2_t': 'Union[float, Tuple[float, float]]',
        '_ratio_3_t': 'Union[float, Tuple[float, float, float]]',
        'CompilerFn': 'Callable[[GraphModule, List[Tensor]], CompiledFn]',
        '_collate_fn_t': 'Callable[[List[T]], Any]',
        '_worker_init_fn_t': 'Callable[[int], None]',
        '_TensorOrTensors': 'Union[torch.Tensor, Sequence[torch.Tensor]]',
        'in_dims_t': 'Union[int, Tuple]',
        'out_dims_t': 'Union[int, Tuple[int, ...]]',
        '_dispatchkey': "Union[str, torch._C.DispatchKey]",
        'FILE_LIKE': 'Union[str, PathLike, BinaryIO, IO[bytes]]',
        'MAP_LOCATION': 'Optional[Union[Callable[[Tensor, str], Tensor], device, str, Dict[str, str]]]',
        'GlobPattern': 'Union[str, Iterable[str]]',
        '_tensor_or_tensors': 'Union[Tensor, Iterable[Tensor]]',
        'Number': "Union[int, float, bool]",
        'Device': "Union[device, str, int, None]",
        'NamedShape': "Union[int, str]",
        'ProcessGroupType': "Optional[Union[ProcessGroup, Tuple[ProcessGroup, ProcessGroup]]]",
    }

    __WARNING_MAPPING_TABLE = {
        'any': 'Any',
        'callable': 'Callable',
        'generator': 'Generator',
        'Tuple': 'tuple',
        'List': 'list',
        'Int': 'int',
        'ints': 'int',
        'integer': 'int',
        'Tensors': 'Tensor',
        'sequence': 'Sequence',
        'iterable': 'Iterable',
        'tensor': 'Tensor',
        'string': 'str',
        '_int': 'int',
        '_float': 'float',
        '_bool': 'bool',
        'builtins.int': 'int',
        'builtins.bool': 'bool',
    }

    __LETTER_CASE_WARNING = ['Tuple', 'List', 'Int', 'sequence', 'iterable', 'any', 'tensor', 'callable', 'generator']
    __PLURAL_WARNING = ['ints', 'Tensors']
    __BUILTIN_TYPE_WARNING = ['integer', 'string', '_int', '_float', '_bool', 'builtins.int', 'builtins.bool']
    __UNKNOWN_DELIMITER = []
    __UNKNOWN_NON_TYPE_WORD = []

    @classmethod
    def mapping(cls, type_str: str, grand_parent_object: Union[Function, ClassObject], parent_object: Parameter) -> str:
        type_str = cls.__normalize_modern_typing_syntax(type_str)
        for key, value in cls.__MAPPING_TABLE.items():
            type_str = re.sub(r'\b' + re.escape(key) + r'\b', value, type_str)
        type_str = cls.__normalize_pipe_union(type_str)
        type_str = cls.warning_type_mapping(type_str, grand_parent_object, parent_object)
        return type_str

    @classmethod
    def __normalize_modern_typing_syntax(cls, type_str: str) -> str:
        type_str = cls.__strip_outer_string_literal(type_str)
        type_str = cls.__strip_inner_string_type_refs(type_str)
        type_str = cls.__normalize_annotated(type_str)
        type_str = cls.__normalize_literal(type_str)
        type_str = cls.__normalize_numpy_literal_alias(type_str)
        type_str = cls.__normalize_empty_tuple_type(type_str)
        type_str = cls.__trim_unmatched_closing_brackets(type_str)
        return type_str

    @classmethod
    def __normalize_pipe_union(cls, type_str: str) -> str:
        parts: list[str] = []
        current_part: list[str] = []
        bracket_depth = 0
        paren_depth = 0

        for char in type_str:
            if char == "[":
                bracket_depth += 1
            elif char == "]":
                bracket_depth -= 1
            elif char == "(":
                paren_depth += 1
            elif char == ")":
                paren_depth -= 1

            if char == "|" and bracket_depth == 0 and paren_depth == 0:
                part = "".join(current_part).strip()
                if part != "":
                    parts.append(part)
                current_part = []
                continue

            current_part.append(char)

        last_part = "".join(current_part).strip()
        if last_part != "":
            parts.append(last_part)

        if len(parts) <= 1:
            return type_str

        return f"Union[{', '.join(parts)}]"

    @classmethod
    def __strip_outer_string_literal(cls, type_str: str) -> str:
        if len(type_str) >= 2 and type_str[0] == type_str[-1] and type_str[0] in {"'", '"'}:
            return type_str[1:-1]
        return type_str

    @classmethod
    def __strip_inner_string_type_refs(cls, type_str: str) -> str:
        return re.sub(r"""(['"])([A-Za-z_][A-Za-z0-9_.]*)\1""", r"\2", type_str)

    @classmethod
    def __normalize_annotated(cls, type_str: str) -> str:
        while "Annotated[" in type_str:
            start = type_str.find("Annotated[")
            bracket_start = start + len("Annotated[") - 1
            bracket_end = cls.__find_matching_bracket(type_str, bracket_start)
            if bracket_end == -1:
                break
            inner = type_str[bracket_start + 1: bracket_end]
            replacement = cls.__first_top_level_segment(inner)
            type_str = f"{type_str[:start]}{replacement}{type_str[bracket_end + 1:]}"
        return type_str

    @classmethod
    def __normalize_literal(cls, type_str: str) -> str:
        while "Literal[" in type_str:
            start = type_str.find("Literal[")
            bracket_start = start + len("Literal[") - 1
            bracket_end = cls.__find_matching_bracket(type_str, bracket_start)
            if bracket_end == -1:
                break
            type_str = f"{type_str[:start]}Any{type_str[bracket_end + 1:]}"
        return type_str

    @classmethod
    def __normalize_numpy_literal_alias(cls, type_str: str) -> str:
        while "L[" in type_str:
            start = type_str.find("L[")
            bracket_start = start + 1
            bracket_end = cls.__find_matching_bracket(type_str, bracket_start)
            if bracket_end == -1:
                break
            type_str = f"{type_str[:start]}Any{type_str[bracket_end + 1:]}"
        return type_str

    @classmethod
    def __normalize_empty_tuple_type(cls, type_str: str) -> str:
        return type_str.replace("tuple[()]", "tuple[EmptyTuple]").replace("Tuple[()]", "Tuple[EmptyTuple]")

    @classmethod
    def __trim_unmatched_closing_brackets(cls, type_str: str) -> str:
        while True:
            square_balance = 0
            changed = False
            result_chars = []
            for char in type_str:
                if char == "[":
                    square_balance += 1
                elif char == "]":
                    if square_balance == 0:
                        changed = True
                        continue
                    square_balance -= 1
                result_chars.append(char)
            type_str = "".join(result_chars)
            if not changed:
                return type_str

    @classmethod
    def __find_matching_bracket(cls, text: str, open_index: int) -> int:
        depth = 0
        for index in range(open_index, len(text)):
            if text[index] == "[":
                depth += 1
            elif text[index] == "]":
                depth -= 1
                if depth == 0:
                    return index
        return -1

    @classmethod
    def __first_top_level_segment(cls, text: str) -> str:
        bracket_depth = 0
        paren_depth = 0
        for index, char in enumerate(text):
            if char == "[":
                bracket_depth += 1
            elif char == "]":
                bracket_depth -= 1
            elif char == "(":
                paren_depth += 1
            elif char == ")":
                paren_depth -= 1
            elif char == "," and bracket_depth == 0 and paren_depth == 0:
                return text[:index].strip()
        return text.strip()

    @classmethod
    def warning_type_mapping(cls, type_str: str, grand_parent_object: Union[Function, ClassObject], parent_object: Parameter) -> str:
        for key, value in cls.__WARNING_MAPPING_TABLE.items():
            original_str = type_str
            type_str = re.sub(r'\b' + re.escape(key) + r'\b', value, type_str)
            if type_str != original_str:
                print(f"[Doc Type Mapping Warning] There is {key} -> {value} mapping exist.")
                if key in cls.__LETTER_CASE_WARNING:
                    classified_result["warning"]["break_format"]["letter_case"].append(
                        f"{grand_parent_object.symbol.name}:{parent_object.symbol.name if parent_object is not None else 'return_type'}")
                elif key in cls.__PLURAL_WARNING:
                    classified_result["warning"]["break_format"]["plural"].append(
                        f"{grand_parent_object.symbol.name}:{parent_object.symbol.name if parent_object is not None else 'return_type'}")
                elif key in cls.__BUILTIN_TYPE_WARNING:
                    classified_result["warning"]["break_format"]["builtin_type"].append(
                        f"{grand_parent_object.symbol.name}:{parent_object.symbol.name if parent_object is not None else 'return_type'}")


        return type_str
