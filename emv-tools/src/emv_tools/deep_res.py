
import re
import pathlib
import xmippLib
import logging
import argparse

from .ffi.scipion import *
from .utils.proxy import TempFileProxy, OutputInfo
from .utils.conversion import load_cif_as_pdb
from .utils.validate_pdb import validate_pdb_lines
from .utils.bws import save_for_bws

from collections import namedtuple
from emv_tools.download import EMDBMetadata, download_emdb_metadata

InputFiles = namedtuple("InputFile", ["emdb_map", "deepres_vol", "structure"])


@proxify
def resize_output_volume(output_volume, resolution: int, size: int):
    if resolution >= 2.7:
        resize_samp = 1.0
    else:
        resize_samp = 0.5

    out_v = xmippLib.Image(output_volume).getData()
    z, _, _ = out_v.shape

    factor = size / z
    final_samp = resize_samp / factor
    fourier_v = resize_samp / 2 * final_samp

    output = xmipp_transform_filter(
        output_volume,
        OutputInfo("vol"),
        fourier="low_pass %f" % fourier_v
    )

    return xmipp_image_resize(
        output,
        OutputInfo("vol"),
        dim=size
    )


def create_deepres_mask(pdb_file: str, emdb_map: str, metadata: EMDBMetadata):
    
    volume_pdb = xmipp_volume_from_pdb(
        pdb_file,
        OutputInfo(None),
        center_pdb="-v 0",
        sampling=metadata.sampling,
        size=metadata.size
    ).reassign("vol")

    aligned = xmipp_volume_align(
        OutputInfo(file_ext="vol"),
        embdb_map=emdb_map,
        volume=volume_pdb
    )

    mask = xmipp_transform_threshold(
        aligned,
        OutputInfo(file_ext="vol"),
        select="below 0.02",
        substitute="binarize"
    )

    mask = xmipp_transform_morphology(
        mask,
        OutputInfo("vol"),
        binary_operation="dilation",
        size=2
    )

    return mask


def find_files(*, scipion_project_root):
    scipion_project_root = pathlib.Path(scipion_project_root)

    def _glob_re(pattern, strings):
        pattern = re.compile(pattern)
        return filter(lambda x: pattern.match(str(x)), strings)

    def _find_file(directory, *, suffix, label, pattern=".*"):
        cands = list(_glob_re(pattern, directory.glob(f"*.{suffix}")))
        if len(cands) > 1:
            cands_str = "\n".join(map(str, cands))
            logging.warning(f"More than one candidate found for {label}, the behavior is undefined:\n{cands_str}")
        elif len(cands) == 0:
            raise ValueError(f"No results for {label} in scipion project")

        return cands[0]


    # EMDB map
    emdb_map = _find_file(
        scipion_project_root / "Runs" / "000002_ProtImportVolumes" / "extra",
        suffix="map",
        pattern="(.*)emd_([0-9]+).map",
        label="map file"
    )

    deepres_vol = _find_file(
        scipion_project_root / "Runs" / "000727_XmippProtDeepRes" / "extra",
        suffix="vol",
        pattern="(.*)deepRes_resolution_originalSize.vol",
        label="DeepRes volume"
    )

    structure = _find_file(
        scipion_project_root,
        suffix="cif",
        label="CIF file"
    )

    return InputFiles(str(emdb_map), str(deepres_vol), str(structure))


def _setup_parser_args(parser):
    parser.add_argument("--project", "-p", help="Path to the root folder of the Scipion project to convert", required=False)
    parser.add_argument("--output", "-o", help="Path to write the converted .json file", required=True)

    parser.add_argument("--map", "-m", help="EMDB .map file")
    parser.add_argument("--volume", "-v", help="Volume file produced by DeepRes")
    parser.add_argument("--structure", "-s", help="Aligned atomic model as a CIF file")


def _default(default, override):
    return override if override is not None else default


def run(args):
    input_files = (
        find_files(scipion_project_root=args.project) if args.project is not None
        else InputFiles(None, None, None)
    )

    emdb_map = _default(input_files.emdb_map, args.map)
    deepres_vol = _default(input_files.deepres_vol, args.volume)
    cif_path = _default(input_files.structure, args.structure)

    output_path = pathlib.Path(args.output) / "deepres_converted.json"

    if emdb_map is None:
        logging.error("No file provided for EMDB map")
        exit(-1)

    if deepres_vol is None:
        logging.error("No file provided for DeepRes volume")
        exit(-1)

    if cif_path is None:
        logging.error("No file provided for atomic model")
        exit(-1)


    # Load files
    metadata = download_emdb_metadata(41510) # Get from header instead

    pdb_file = load_cif_as_pdb(cif_path)
    validate_pdb_lines(pdb_file)

    pdb_file = TempFileProxy.proxy_for_lines(pdb_file, file_ext="pdb")

    # Create DeepRes mask
    deepres_mask = create_deepres_mask(pdb_file, emdb_map, metadata)
    # deepres_mask = "/home/max/Documents/val-server/data/val-report-service/EMD-41510/EMD-41510_ScipionProject/Runs/000415_XmippProtCreateMask3D/mask.mrc"
    deepres_mask = resize_output_volume(
        deepres_mask,
        metadata.resolution,
        metadata.size
    )


    # Resize the DeepRes volume
    deepres_vol = resize_output_volume(
        deepres_vol,
        metadata.resolution,
        metadata.size
    )

    # import shutil
    # shutil.copy(pdb_file.path, "../data/pdb_file.pdb")
    # shutil.copy(deepres_vol.path, "../data/deepres_volume.vol")
    # shutil.copy(deepres_mask.path, "../data/deepres_mask.vol")

    # Join the two parts
    deepres_atomic_model = xmipp_pdb_label_from_volume(
        OutputInfo(file_ext="atom.pdb"),
        pdb=pdb_file,
        volume=deepres_vol,
        mask=deepres_mask,
        sampling=metadata.sampling,
        origin="%f %f %f" % (metadata.org_x, metadata.org_y, metadata.org_z),
    )

    save_for_bws(
        deepres_atomic_model,
        output_path,
        volume_map="",
        atomic_model=""
    )


def main():

    parser = argparse.ArgumentParser("Convert validation data created on the validation report service (VRS) to a format compatible with 3DBionotes.")
    _setup_parser_args(parser)

    args = parser.parse_args()
    run(args)

if __name__ == "__main__":
    main()