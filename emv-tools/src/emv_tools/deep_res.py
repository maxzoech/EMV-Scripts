
# from Bio.PDB import MMCIFParser, PDBIO

import xmippLib
from emv_tools.ffi.scipion import xmipp_image_resize, xmipp_transform_filter

VOLUME_PATH = "/home/max/Documents/val-server/data/val-report-service/EMD-41510/EMD-41510_intermediateData/Runs/000727_XmippProtDeepRes/extra/deepRes_resolution_originalSize.vol"
CIF_FILE = "/home/max/Documents/val-server/data/val-report-service/EMD-41510/EMD-41510_intermediateData/8tqo.cif"
RESIZED_VOL_PATH = "/home/max/Documents/val-server/EMV-Script-fork/emv-tools/data/resized_vol.vol"

from emv_tools.metadata import download_emdb_metadata

def resize_volume(volume_path: str, size: int, resolution: int):
    if resolution >= 2.7:
        resize_samp = 1.0
    else:
        resize_samp = 0.5

    V = xmippLib.Image(volume_path).getData()
    (z, y, x) = V.shape

    factor = size / z
    final_samp = resize_samp / factor
    fourier_V = resize_samp / 2 * final_samp

    try:
        xmipp_transform_filter(volume_path, RESIZED_VOL_PATH, fourier=f"low_pass {fourier_V}")
    except Exception as e:
        print(e)

    print("Something")


def main():
    pass

    # xmipp_image_resize(VOLUME_PATH, RESIZED_VOL_PATH, factor="2")

    # parser = MMCIFParser(QUIET=True)
    # structure = parser.get_structure("model", CIF_FILE)

    # # Save to PDB
    # io = PDBIO()
    # io.set_structure(structure)

    # print(io)

    metadata = download_emdb_metadata(41510)
    resize_volume(VOLUME_PATH, metadata.size, metadata.resolution)

    # io.save("../data/structure.pdb")
    PDB_PATH = "emv-tools/data/emd_41510/structure.pdb"

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