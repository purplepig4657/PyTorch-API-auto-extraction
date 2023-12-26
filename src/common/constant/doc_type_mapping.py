import re


class DocTypeMapping:

    __MAPPING_TABLE = {
        'torch.layout': 'layout',
        'torch.dtype': 'dtype',
        'torch.device': 'device',
        'torch.memory_format': 'memory_format',
        'torch.Generator': 'Generator',
        'torch.nn.Module': 'Module',
        'torch.nn.Optimizer': 'Optimizer',
        'torch._C._monitor.Aggregation': 'Aggregation',
        'torch._C.Value': 'Value',
        'torch.fx.GraphModule': 'GraphModule',
        'torch.jit.ScriptModule': 'ScriptModule',
        'torch._C.PyTorchFileReader': 'PyTorchFileReader',
        'torch.Tensor': 'Tensor',
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
        '_size': "Union[torch.Size, List[int], Tuple[int, ...]]",
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
        'Tuple': 'tuple',
        'Dict': 'dict',
        'List': 'list',
        'Int': 'int',
        'Sequence': 'sequence',
        'iterable': 'Iterable',
        'tensor': 'Tensor',
        'string': 'str',
        'int64': 'int',
        'int32': 'int',
        '_int': 'int',
        '_float': 'float',
        '_bool': 'bool',
        '_dtype': 'dtype',
        '_device': 'device',
        'builtins.int': 'int',
        'builtins.bool': 'bool',
        '_qscheme': 'qscheme',
        '_layout': 'layout',
    }

    @classmethod
    def mapping(cls, type_str: str) -> str:
        for key, value in cls.__MAPPING_TABLE.items():
            type_str = re.sub(r'\b' + re.escape(key) + r'\b', value, type_str)
        type_str = cls.warning_type_mapping(type_str)
        return type_str

    @classmethod
    def warning_type_mapping(cls, type_str: str) -> str:
        for key, value in cls.__WARNING_MAPPING_TABLE.items():
            original_str = type_str
            type_str = re.sub(r'\b' + re.escape(key) + r'\b', value, type_str)
            if type_str != original_str:
                print(f"[Doc Type Mapping Warning] There is {key} -> {value} mapping exist.")
        return type_str
