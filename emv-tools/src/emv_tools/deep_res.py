import os

import xmippLib
from .ffi.scipion import *
from .utils.proxy import Proxy, TempFileProxy, OutputInfo
from .utils.conversion import load_cif_as_pdb

from functools import partial
import tempfile

VOLUME_PATH = "/home/max/Documents/val-server/data/val-report-service/EMD-41510/EMD-41510_intermediateData/Runs/000727_XmippProtDeepRes/extra/deepRes_resolution_originalSize.vol"
EMDB_MAP = "/home/max/Documents/val-server/EMV-Script-fork/emv-tools/data/emd_41510/emd_41510.map"
CIF_FILE = "/home/max/Documents/val-server/data/val-report-service/EMD-41510/EMD-41510_intermediateData/8tqo.cif"

PDB_PATH = "/home/max/Documents/val-server/EMV-Script-fork/emv-tools/data/emd_41510/structure.pdb"

from emv_tools.download import EMDBMetadata, download_emdb_map, download_emdb_metadata, download_pdb_model

@proxify
def resize_volume(input_path, resolution, sampling):

    if resolution >= 2.7:
        new_sampling = 1.0
    else:
        new_sampling = 0.5

    sampling_factor = sampling / new_sampling
    fourier_val = sampling / (2 * new_sampling)

    inputs = input_path
    if sampling < new_sampling:
        inputs = xmipp_transform_filter(
            inputs,
            OutputInfo("vol"),
            fourier=f"low_pass {fourier_val}",
        )

    return xmipp_image_resize(
        inputs,
        OutputInfo("vol"),
        factor=sampling_factor
    )


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


def delete_hidrogens(pdb_path: os.PathLike):
    with open(pdb_path) as file:
        lines = [l for l in file.readlines() if l.strip()[-1] != "H"]

    return lines


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

def main():

    os.makedirs("../data/input_data", exist_ok=True)
    embd_map = download_emdb_map(41510, path="../data/input_data")
    metadata = download_emdb_metadata(41510)

    pdb_file = download_pdb_model(metadata.pdb_id, "../data/input_data")
    pdb_file = TempFileProxy.proxy_for_lines(delete_hidrogens(pdb_file), file_ext="ent")

    # pdb_contents = load_cif_as_pdb(CIF_FILE)
    # pdb_file = TempFileProxy.proxy_for_lines(pdb_contents, file_ext="ent")

    # print(pdb_contents)

    # return
    # Create DeepRes mask
    deep_res_mask = create_deepres_mask(pdb_file, EMDB_MAP, metadata)
    deep_res_mask = resize_volume(deep_res_mask, metadata.resolution, metadata.sampling)    

    deep_res_mask = xmipp_transform_threshold(
        deep_res_mask,
        OutputInfo("vol"),
        select="below 0.15",
        substitute="binarize"
    )

    deepres_resized = resize_output_volume(
        VOLUME_PATH,
        metadata.resolution,
        metadata.size
    )

    # import shutil
    # shutil.copy(
    #     deep_res_mask.path,
    #     "../data/deepres_mask-aligned-resized.vol"
    # )

    # shutil.copy(
    #     deepres_resized.path,
    #     "../data/deep_res-output-resized.vol"
    # )
    # return


    # pdb_size = os.path.getsize(PDB_PATH)
    # volume_size = os.path.getsize(deepres_resized.path)
    # mask_size = os.path.getsize(deep_res_mask.path)

    # print(f"Sizes: pdb {pdb_size}, volume: {volume_size}, mask: {mask_size}")

    xmipp_pdb_label_from_volume(
        "../data/output.atom.pdb", 
        pdb=PDB_PATH,
        volume=deepres_resized,
        mask=deep_res_mask,
        sampling=metadata.sampling,
        origin="%f %f %f" % (metadata.org_x, metadata.org_y, metadata.org_z),
    )


if __name__ == "__main__":
    main()