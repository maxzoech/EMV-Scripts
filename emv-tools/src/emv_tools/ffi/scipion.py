from functools import partial
from emv_tools.utils.external_call import foreign_function
from emv_tools.utils.proxy import proxify

@proxify
@partial(
    foreign_function,
    args_map={"inputs": "i", "outputs": "o"},
    args_validation={
        "outputs": "(.+)\.vol",
        "inputs": "(.+)\.vol",
        "fourier": "low_pass [0-9]+\.[0-9]+"
    }
)
def xmipp_transform_filter(inputs: str, outputs: str, *, fourier: str) -> int:
    pass


@proxify
@partial(
    foreign_function,
    args_map={"inputs": "i", "outputs": "o"},
    args_validation={
        "outputs": "(.+)\.vol",
        "inputs": "(.+)\.vol"
    }
)
def xmipp_image_resize(inputs: str, outputs: str, *, dim: int) -> int:
    pass


@proxify
@partial(
    foreign_function,
    args_map={"output": "o", "volume": "vol"},
)
def xmipp_pdb_label_from_volume(output: str, *, pdb: str, volume: str, mask: str, sampling, origin: str):
    pass


@partial(
    foreign_function,
    args_map={
        "inputs": "i",
        "outputs": "o",
        "center_pdb": "centerPDB"
    }
)
def xmipp_volume_from_pdb(inputs: str, outputs: str, v: int, *, center_pdb: str, sampling: float, size):
    pass