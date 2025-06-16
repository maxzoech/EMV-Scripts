import os

import xmippLib
from .ffi.scipion import *
from .utils.proxy import Proxy, OutputInfo

from functools import partial
import tempfile

VOLUME_PATH = "/home/max/Documents/val-server/data/val-report-service/EMD-41510/EMD-41510_intermediateData/Runs/000727_XmippProtDeepRes/extra/deepRes_resolution_originalSize.vol"
EMDB_MAP = "/home/max/Documents/val-server/EMV-Script-fork/emv-tools/data/emd_41510/emd_41510.map"
CIF_FILE = "/home/max/Documents/val-server/data/val-report-service/EMD-41510/EMD-41510_intermediateData/8tqo.cif"

PDB_PATH = "/home/max/Documents/val-server/EMV-Script-fork/emv-tools/data/emd_41510/structure.pdb"

from emv_tools.metadata import EMDBMetadata, download_emdb_metadata

@proxify
def resize_volume(input_path, size: int, resolution: int):
    print(f"Resize volume input: {input_path}")
    
    resize_samp = 1.0 if resolution >= 2.7 else 0.5 

    V = xmippLib.Image(input_path).getData()
    (z, _, _) = V.shape

    factor = size / z
    final_samp = resize_samp / factor
    fourier_V = resize_samp / 2 * final_samp

    result = xmipp_transform_filter(input_path, OutputInfo("vol"), fourier=f"low_pass {fourier_V}")
    result = xmipp_image_resize(result, OutputInfo("vol"), dim=factor)
    
    return result


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

    metadata = download_emdb_metadata(41510)

    # Create DeepRes mask
    deep_res_mask = create_deepres_mask(PDB_PATH, EMDB_MAP, metadata)
    deep_res_mask = resize_volume(deep_res_mask, metadata.size, metadata.resolution)

    volume = resize_volume(VOLUME_PATH, size=metadata.size, resolution=metadata.resolution)
    
    print(deep_res_mask, volume)

    # create_deepres_mask(volume, pdb_file, sampling=metadata.sampling, size=metadata.size)

    # with tempfile.NamedTemporaryFile(suffix=".vol") as file:
    #     print(file.name)


    # io.save("../data/structure.pdb")

    # exit_code = xmipp_pdb_label_from_volume(
    #     "/dev/null/deepres/atom.pub",
    #     pdb="pdb_path",
    #     volume=VOLUME_PATH,
    #     mask="mask_path",
    #     sampling="sampling_path",
    #     origin="origin"
    # )

#     # subprocess.run(["scipion", "run", "xmipp_pdb_label_from_volume"])

#     # os.system(
#     #     'scipion3'
#     # )

if __name__ == "__main__":
    main()