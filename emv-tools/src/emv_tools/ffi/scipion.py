from functools import partial
from emv_tools.ffi.utils import foreign_function


@partial(foreign_function, args_map={"output": "o", "volume": "vol"}, shell=False)
def xmipp_pdb_label_from_volume(output: str, *, pdb: str, volume: str, mask: str, sampling, origin: str):
    pass
