from functools import partial
from emv_tools.utils.external_call import foreign_function
from emv_tools.utils.proxy import proxify

@proxify
@partial(
    foreign_function,
    args_map={"inputs": "i", "outputs": "o"},
    args_validation={
        "outputs": "(.+)\.vol",
        # "inputs": "(.+)\.vol",
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
        # "inputs": "(.+)\.vol"
    }
)
def xmipp_image_resize(inputs: str, outputs: str, *, factor=None, dim=None) -> int:
    pass


@proxify
@partial(
    foreign_function,
    args_map={
        "inputs": "i",
        "outputs": "o",
        "center_pdb": "centerPDB"
    },
    args_validation={
        # "inputs": "(.+)\.ent",
        # "outputs": "(.+)\.vol",
    }
)
def xmipp_volume_from_pdb(inputs: str, outputs: str, *, center_pdb: str, sampling: float, size):
    pass


def postprocess_volume_align_args(raw_args):
    _, out_path = raw_args[0]
    return raw_args[1:] + [[out_path]]

@proxify
@partial(
    foreign_function,
    args_map={
        "embdb_map": "i1",
        "volume": "i2",
    },
    args_validation={
        "embdb_map": "(.+)\.map",
        "volume": "(.+)\.vol",
    },
    postprocess_fn=postprocess_volume_align_args
)
def xmipp_volume_align(outputs: str, *, embdb_map: str, volume: str, local="--apply"):
    pass


@proxify
@partial(
    foreign_function,
    args_map={
        "aligned_vol": "i",
        "outputs": "o",
    },
    args_validation={
        "aligned_vol": "(.+)\.vol",
        "outputs": "(.+)\.vol",
    },
)
def xmipp_transform_threshold(aligned_vol: str, outputs: str, *, select: str, substitute: str):
    pass


@proxify
@partial(
    foreign_function,
    args_map={
        "inputs": "i",
        "outputs": "o",
        "binary_operation": "binaryOperation"
    },
    args_validation={
        "inputs": "(.+)\.vol",
        "outputs": "(.+)\.vol",
    },
)
def xmipp_transform_morphology(inputs: str, outputs: str, *, binary_operation: str, size: int):
    pass


@proxify
@partial(
    foreign_function,
    args_map={
        "output": "o",
        "volume": "vol",
    },
)
def xmipp_pdb_label_from_volume(output: str, *, pdb: str, volume: str, mask: str, sampling, origin: str):
    pass


@proxify
@partial(
    foreign_function,
    args_map={
        "inputs": "i",
        "outputs": "o",
    },
    args_validation={
        # "inputs": "(.+)\.vol",
        "outputs": "(.+)\.vol",
    },
)
def xmipp_transform_threshold(inputs: str, outputs: str, *, select: str, substitute: str):
    pass


@proxify
@partial(
    foreign_function,
    args_map={
        "outputs": "o",
        "volume": "vol",
    },
    args_validation={
        "outputs": "(.+)\.atom.pdb",
        # "pdb": "(.+)\.pdb",
        # "volume": "(.+)\.vol",
    }
)
def xmipp_pdb_label_from_volume(outputs, *, pdb: str, volume: str, mask: str, sampling: str, origin: str):
    pass