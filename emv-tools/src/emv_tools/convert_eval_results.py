import os
import re
import logging
from pathlib import Path
from .utils.find_files import _find_file, find_dependency_filenames

from .scipion_bridge.environment import configure_default_env
from .ffi.scipion import xmipp_pdb_label_from_volume
from .scipion_bridge.proxy import TempFileProxy
from .utils.pdb import load_cif_as_pdb
from .utils.bws import save_for_bws
from .utils.download import download_emdb_metadata

import argparse
from collections import namedtuple

InputFiles = namedtuple("InputFile", ["volume", "mask", "structure"])


def fetch_files(protocol: str, *, project_root: os.PathLike, volume: str):
    project_root = Path(project_root)

    suffix = "".join(Path(volume).suffixes)[1:]

    vol_path = _find_file(
        project_root / "Runs" / f"*_{protocol}" / "extra",
        suffix=suffix,
        pattern=f"(.*){volume}",
        label="Volume",
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


def find_emdb_identifier(project_root: os.PathLike):
    project_root = str(project_root)

    pattern = re.compile("EMD-[0-9]+")
    matches = re.findall(pattern, project_root)

    if len(matches) > 1:
        logging.warning("Multiple possible EMDB entries found; behavior is undefined")

    if not matches:
        raise ValueError("No EMDB entry found")

    return int(matches[0][4:])


def convert(
    protocol: str, emb_entry: str, *, project_root: os.PathLike, volume: str, **kwargs
):

    inputs = fetch_files(protocol, project_root=project_root, volume=volume)

    structure = load_cif_as_pdb(inputs.structure)
    structure = TempFileProxy.proxy_for_string(structure, file_ext="pdb")

    if emb_entry is None:
        emb_entry = find_emdb_identifier(project_root)

    pdb_entry = os.path.split(inputs.structure)[-1][:-4]

    metadata = download_emdb_metadata(emb_entry)

    atomic_model = xmipp_pdb_label_from_volume(
        pdb=structure,
        volume=inputs.volume,
        mask=inputs.mask,
        sampling=metadata.sampling,
        origin="%f %f %f" % (metadata.org_x, metadata.org_y, metadata.org_z),
    )

    return atomic_model, (str(emb_entry), pdb_entry)

# Example Usage:
# DeepRes:
# scipion3 python -m emv_tools.convert_eval_results 
# -project '/home/max/Documents/val-server/data/val-report-service/EMD-41510'  
# -o /home/max/Documents/val-server/EMV-Script-fork/emv-tools/data/converted.json 
# -n XmippProtDeepRes -
# vol deepRes_resolution_originalSize.vol

# MonoRes:
# scipion3 python -m emv_tools.convert_eval_results
# -project '/home/max/Documents/val-server/data/val-report-service/EMD-41510'
# -o /home/max/Documents/val-server/EMV-Script-fork/emv-tools/data/converted.json
# -n XmippProtMonoRes
# -vol monoresResolutionMap.mrc

# BlocRes:
# scipion3 python -m emv_tools.convert_eval_results
# -project '/home/max/Documents/val-server/data/val-report-service/EMD-41510'
# -o /home/max/Documents/val-server/EMV-Script-fork/emv-tools/data/converted.json
# -n BsoftProtBlocres
# -vol resolutionMap.map

# FSC-Q
# scipion3 python -m emv_tools.convert_eval_results
# -project '/home/max/Documents/val-server/data/val-report-service/EMD-41510' 
# -o /home/max/Documents/val-server/EMV-Script-fork/emv-tools/data/converted.json
# -n XmippProtValFit
# -vol diferencia.map

# TODO: Map-Q


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-project",
        dest="project_root",
        type=Path,
        required=True,
        help="Root directory of the Scipion project",
    )

    parser.add_argument(
        "-o",
        dest="output_path",
        type=Path,
        help="Path to a JSON file to write the data",
    )

    parser.add_argument(
        "-n",
        "--name",
        dest="protocol",
        required=True,
        help="Name of the protocol to convert (e.g. XmippProtDeepRes)",
    )

    parser.add_argument(
        "-vol",
        "--volume",
        dest="volume",
        required=True,
        help="Path to the volume file containing the evaluation data (e.g. XmippProtDeepRes)",
    )

    parser.add_argument(
        "--entry",
        required=False,
        dest="emb_entry",
        type=int,
        help="The EMD identifier for this project (e.g. (.*)deepRes_resolution_originalSize.vol)",
    )

    configure_default_env()
    args = parser.parse_args()

    try:
        converted, ids = convert(**vars(args))
    except ValueError:
        print(
            "Could not find EMD entry; You can provide this value manually using the --entry flag!"
        )
        exit(-1)

    save_for_bws(converted, args.output_path, *ids, title=args.protocol)


if __name__ == "__main__":
    main()
