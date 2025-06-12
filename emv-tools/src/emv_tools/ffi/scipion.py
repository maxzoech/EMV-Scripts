from functools import partial
from emv_tools.ffi.utils import foreign_function


@partial(foreign_function, args_map={"output": "o", "volume": "vol"})
def xmipp_pdb_label_from_volume(output: str, *, pdb: str, volume: str, mask: str, sampling, origin: str):
    pass

@partial(foreign_function, args_map={"inputs": "i", "outputs": "o"})
def xmipp_transform_filter(inputs: str, outputs: str, *, fourier: str) -> int:
    pass

@partial(foreign_function, args_map={"inputs": "i", "outputs": "o"})
def xmipp_image_resize(inputs: str, outputs: str, *, dim: int) -> int:
    pass
