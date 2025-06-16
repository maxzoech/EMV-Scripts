import os

import xmippLib
from .ffi.scipion import *
from .utils.proxy import ReferenceProxy, OutputInfo

from functools import partial
import tempfile

VOLUME_PATH = "/home/max/Documents/val-server/data/val-report-service/EMD-41510/EMD-41510_intermediateData/Runs/000727_XmippProtDeepRes/extra/deepRes_resolution_originalSize.vol"
EMD_MAP = "/home/max/Documents/val-server/EMV-Script-fork/emv-tools/data/emd_41510/emd_41510.map"
CIF_FILE = "/home/max/Documents/val-server/data/val-report-service/EMD-41510/EMD-41510_intermediateData/8tqo.cif"

PDB_PATH = "/home/max/Documents/val-server/EMV-Script-fork/emv-tools/data/emd_41510/structure.pdb"

from emv_tools.metadata import download_emdb_metadata

def resize_volume(input_path: str, size: int, resolution: int):
    resize_samp = 1.0 if resolution >= 2.7 else 0.5 

    V = xmippLib.Image(input_path).getData()
    (z, _, _) = V.shape

    factor = size / z
    final_samp = resize_samp / factor
    fourier_V = resize_samp / 2 * final_samp

    result = xmipp_transform_filter(input_path, OutputInfo("vol"), fourier=f"low_pass {fourier_V}")
    result = xmipp_image_resize(result, OutputInfo("vol"), dim=factor)
    
    return result

# @partial(proxify, outputs=OutputInfo(arg_name="output", file_ext="pdbmap"))
# def create_deepres_mask(volume, pdb, output, *, sampling, size):
#     print(volume, pdb, output, sampling, size)


def delete_hidrogens(pdb_path: os.PathLike):
    with open(pdb_path) as file:
        lines = [l for l in file.readlines() if l.strip()[-1] != "H"]

    return lines


def main():

    metadata = download_emdb_metadata(41510)

    # pdb_file = delete_hidrogens(PDB_PATH)
    pdb_file = ReferenceProxy(PDB_PATH, owned=False) # Set owned to false to avoid deleting the PDB file
    #TempFileProxy.proxy_for_lines(pdb_file, file_ext="pdb")


    volume = resize_volume(VOLUME_PATH, size=metadata.size, resolution=metadata.resolution)
    
    volume_pdb = xmipp_volume_from_pdb(
        pdb_file,
        OutputInfo(None),
        center_pdb="-v 0",
        sampling=metadata.sampling,
        size=metadata.size
    ).reasign("vol")

    print(volume_pdb)

    aligned = xmipp_volume_align(
        OutputInfo(file_ext="vol"),
        embdb_map=EMD_MAP,
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

    import os
    print(os.path.getsize(mask.path))

    # print(pdb_file, volume)
    # print(pdb_file)

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