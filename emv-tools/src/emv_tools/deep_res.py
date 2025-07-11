import pathlib

import emv_tools.scipion_bridge.environment
import logging
import argparse

import emv_tools
from .ffi.scipion import *
from .scipion_bridge.proxy import TempFileProxy
from .utils.conversion import load_cif_as_pdb
from .utils.validate_pdb import validate_pdb_lines
from .utils.bws import save_for_bws

from emv_tools.download import download_emdb_metadata
from .utils.find_files import find_files, InputFiles


def _setup_parser_args(parser):
    parser.add_argument(
        "--project",
        "-p",
        help="Path to the root folder of the Scipion project to convert",
        required=False,
    )
    parser.add_argument(
        "--output", "-o", help="Path to write the converted .json file", required=True
    )

    parser.add_argument("--map", "-map", help="EMDB .map file")
    parser.add_argument("--volume", "-v", help="Volume file produced by DeepRes")
    parser.add_argument("--mask", "-msk", help="Volume mask for DeepRes")
    parser.add_argument("--structure", "-s", help="Aligned atomic model as a CIF file")


def _default(default, override):
    return override if override is not None else default


def run(args):
    input_files = (
        find_files(scipion_project_root=args.project)
        if args.project is not None
        else InputFiles(None, None, None)
    )

    emdb_map = _default(input_files.emdb_map, args.map)
    deepres_vol = _default(input_files.deepres_vol, args.volume)
    mask_vol = _default(input_files.mask, args.mask)
    cif_path = _default(input_files.structure, args.structure)

    output_path = pathlib.Path(args.output) / "deepres_converted.json"

    if emdb_map is None:
        logging.error("No file provided for EMDB map")
        exit(-1)

    if deepres_vol is None:
        logging.error("No file provided for DeepRes volume")
        exit(-1)

    if mask_vol is None:
        logging.error("No file provided for mask volume")
        exit(-1)

    if cif_path is None:
        logging.error("No file provided for atomic model")
        exit(-1)

    # Load files
    metadata = download_emdb_metadata(12665)  # Get from header instead

    pdb_file = load_cif_as_pdb(cif_path)
    validate_pdb_lines(pdb_file)

    print(cif_path)
    print(emdb_map)
    print(deepres_vol)
    print(mask_vol)

    pdb_file = TempFileProxy.concatenated_strings(pdb_file, file_ext="pdb")

    # Join the two parts
    deepres_atomic_model = xmipp_pdb_label_from_volume(
        pdb=pdb_file,
        volume=deepres_vol,
        mask=mask_vol,
        sampling=metadata.sampling,
        origin="%f %f %f" % (metadata.org_x, metadata.org_y, metadata.org_z),
    )

    print(deepres_atomic_model)

    save_for_bws(deepres_atomic_model, output_path, volume_map="", atomic_model="")


def main():

    parser = argparse.ArgumentParser(
        "Convert validation data created on the validation report service (VRS) to a format compatible with 3DBionotes."
    )
    _setup_parser_args(parser)

    args = parser.parse_args()
    run(args)


if __name__ == "__main__":

    emv_tools.scipion_bridge.environment.configure_default_env()

    main()
