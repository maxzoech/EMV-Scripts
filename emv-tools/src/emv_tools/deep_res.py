import os

import xmippLib
from .ffi.scipion import xmipp_transform_filter, xmipp_image_resize
from .utils.proxy import OutputInfo

from functools import partial
import tempfile

VOLUME_PATH = "/home/max/Documents/val-server/data/val-report-service/EMD-41510/EMD-41510_intermediateData/Runs/000727_XmippProtDeepRes/extra/deepRes_resolution_originalSize.vol"
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
    result = xmipp_image_resize(result, result, dim=factor)
    
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

    pdb_file = delete_hidrogens(PDB_PATH)
    # pdb_file = Proxy.proxy_for_lines(pdb_file, file_ext="pdb")

    volume = resize_volume(VOLUME_PATH, size=metadata.size, resolution=metadata.resolution)
    print(volume)
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