
import xmippLib
from emv_tools.ffi.scipion import xmipp_image_resize, xmipp_transform_filter

import tempfile

VOLUME_PATH = "/home/max/Documents/val-server/data/val-report-service/EMD-41510/EMD-41510_intermediateData/Runs/000727_XmippProtDeepRes/extra/deepRes_resolution_originalSize.vol"
CIF_FILE = "/home/max/Documents/val-server/data/val-report-service/EMD-41510/EMD-41510_intermediateData/8tqo.cif"

from emv_tools.metadata import download_emdb_metadata

def resize_volume(input_path: str, output_path: str, size: int, resolution: int):
    resize_samp = 1.0 if resolution >= 2.7 else 0.5 

    V = xmippLib.Image(input_path).getData()
    (z, _, _) = V.shape

    factor = size / z
    final_samp = resize_samp / factor
    fourier_V = resize_samp / 2 * final_samp

    xmipp_transform_filter(input_path, output_path, fourier=f"low_pass {fourier_V}")
    xmipp_image_resize(output_path, output_path, dim=factor)


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

    with tempfile.NamedTemporaryFile(suffix=".vol") as file:
        resize_volume(VOLUME_PATH, file.name, metadata.size, metadata.resolution)
        print(file.name)


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