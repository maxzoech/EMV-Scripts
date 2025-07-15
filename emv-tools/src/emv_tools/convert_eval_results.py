import os
from pathlib import Path
from .utils.find_files import _find_file, find_dependency_filenames

from .scipion_bridge.environment import configure_default_env
from .ffi.scipion import xmipp_pdb_label_from_volume
from .scipion_bridge.proxy import TempFileProxy
from .utils.pdb import load_cif_as_pdb

import argparse
from collections import namedtuple

InputFiles = namedtuple("InputFile", ["volume", "mask", "structure"])


def fetch_files(protocol: str, *, project_root: os.PathLike):
    project_root = Path(project_root)

    vol_path = _find_file(
        project_root / "Runs" / f"*_{protocol}" / "extra",
        suffix="vol",
        pattern="(.*)deepRes_resolution_originalSize.vol",
        label="DeepRes volume",
    )

    (mask_filename,) = find_dependency_filenames(
        project_root,
        protocol=protocol,
        query=["XmippProtCreateMask3D"],
    )

    mask_path = _find_file(
        project_root / "Runs" / mask_filename,
        suffix="mrc",
        pattern="(.*).mrc",
        label="DeepRes mask",
    )

    structure_path = _find_file(project_root, suffix="cif", label="CIF file")

    return InputFiles(volume=vol_path, mask=mask_path, structure=structure_path)


def convert(protocol: str, *, project_root: os.PathLike):

    inputs = fetch_files(protocol, project_root=project_root)

    structure = load_cif_as_pdb(inputs.structure)
    structure = TempFileProxy.proxy_for_string(structure, file_ext="pdb")

    atomic_model = xmipp_pdb_label_from_volume(
        pdb=structure,
        volume=inputs.volume,
        mask=inputs.mask,
        sampling=0.825,  # metadata.sampling,
        origin="0 0 0",  # "%f %f %f" % (0.0, 0.0, 0.0) #(metadata.org_x, metadata.org_y, metadata.org_z),
    )

    print(atomic_model)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--name",
        dest="protocol",
        required=True,
        help="Name of the protocol to convert (e.g. XmippProtDeepRes)",
    )

    parser.add_argument(
        "--project",
        dest="project_root",
        type=Path,
        required=True,
        help="Root directory of the Scipion project",
    )

    configure_default_env()
    converted = convert(**vars(parser.parse_args()))


if __name__ == "__main__":
    main()
