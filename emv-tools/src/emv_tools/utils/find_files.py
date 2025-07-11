import os
import pathlib
import logging
import re
from collections import namedtuple

InputFiles = namedtuple("InputFile", ["emdb_map", "deepres_vol", "structure", "mask"])


def _glob_re(pattern, strings):
    pattern = re.compile(pattern)
    return filter(lambda x: pattern.match(str(x)), strings)


def _find_file(path, *, suffix, label, pattern=".*"):
    print(str(path).strip(os.sep).split(os.sep))

    assert False
    cands = list(_glob_re(pattern, directory.glob(f"*.{suffix}")))
    if len(cands) > 1:
        cands_str = "\n".join(map(str, cands))
        logging.warning(
            f"More than one candidate found for {label}, the behavior is undefined:\n{cands_str}"
        )
    elif len(cands) == 0:
        raise ValueError(f"No results for {label} in scipion project")

    return cands[0]


def find_files(*, scipion_project_root: os.PathLike):
    scipion_project_root = pathlib.Path(scipion_project_root)

    # EMDB map
    emdb_map = _find_file(
        scipion_project_root / "Runs" / "([0-9]+)_ProtImportVolumes" / "extra",
        suffix="map",
        pattern="(.*)emd_([0-9]+).map",
        label="map file",
    )

    deepres_vol = _find_file(
        scipion_project_root / "Runs" / "000581_XmippProtDeepRes" / "extra",
        suffix="vol",
        pattern="(.*)deepRes_resolution_originalSize.vol",
        label="DeepRes volume",
    )

    # 000289_XmippProtCreateMask3D
    deepres_mask = _find_file(
        scipion_project_root / "Runs" / "000289_XmippProtCreateMask3D",
        suffix="mrc",
        pattern="(.*).mrc",
        label="DeepRes mask",
    )

    structure = _find_file(scipion_project_root, suffix="cif", label="CIF file")

    return InputFiles(
        str(emdb_map), str(deepres_vol), str(structure), str(deepres_mask)
    )
