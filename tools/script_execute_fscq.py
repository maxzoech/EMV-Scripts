"""
execute FSC-Q automatically
"""

import os
import os.path
import argparse
from script_emv_setup import (
    WORK_PATH,
    create_work_dir,
    download_emdb_map,
    download_pdb_model,
    delete_hidrogens,
    get_parameters,
    download_emdb_halfmaps,
    convert_to_aapdb,
    convert_to_json,
)


def create_mask_fscq(map, pdb, sampling, size, path):
    """Convert PDB to Map"""
    params = " scipion3 run xmipp_volume_from_pdb "
    params += " --centerPDB "
    params += " -v 0 "
    params += f" --sampling {sampling}"
    params += f" --size {size}"
    params += f" -i {path}/{pdb}"
    params += f" -o {path}/pdbMap"
    os.system(params)

    # """ Align pdbMap to reconstruction Map """
    params = " scipion3 run xmipp_volume_align"
    params += f" --i1 {path}/{map}"
    params += f" --i2 {path}/pdbMap.vol"
    params += " --local --apply"
    params += f" {path}/align.vol"
    os.system(params)

    # """"convert vol to mrc"""
    params = " scipion3 run xmipp_image_convert"
    params += f" -i {path}/align.vol"
    params += f" -o {path}/align.mrc"
    params += " -t vol"
    os.system(params)
    params = " scipion3 run xmipp_image_header"
    params += f" -i {path}/align.mrc:mrc"
    params += f" -s {sampling}"
    os.system(params)

    # """create mask"""
    params = " scipion3 run xmipp_transform_threshold"
    params += f" -i {path}/align.vol"
    params += f" -o {path}/mask.vol"
    params += " --select below 0.02 --substitute binarize"
    os.system(params)

    params = " scipion3 run xmipp_transform_morphology"
    params += f" -i {path}/mask.vol"
    params += f" -o {path}/mask.vol"
    params += " --binaryOperation dilation --size 2"
    os.system(params)

    # """"convert mask vol to mrc"""
    params = " scipion3 run xmipp_image_convert"
    params += f" -i {path}/mask.vol"
    params += f" -o {path}/mask.mrc"
    params += " -t vol"
    os.system(params)
    params = " scipion3 run xmipp_image_header"
    params += f" -i {path}/mask.mrc:mrc"
    params += f" -s {sampling}"
    os.system(params)


def execute_blocres(map1, map2, sampling, resolution, cutoff, path, out):
    """
    execute_blocres
    """
    params = " /home/bioinfo/services/tools/scipion3/software/em/bsoft/bin/blocres"
    # params += " -criterio FSC -nofill -smooth -pad 1 -maxresolution 0.5  -step 1"
    params += " -nofill -smooth -pad 1 -maxresolution 0.5  -step 1"
    params += f" -sampling {sampling},{sampling},{sampling}"
    params += f" -box {int(resolution * 5)}"
    params += f" -Mask {path}/mask.mrc"
    params += f" -cutoff {cutoff}"
    params += f" {path}/{map1}"
    params += f" {path}/{map2}"
    params += f" {path}/blocres_{out}.map"
    os.system(params)


def execute_fscq(blocres1, blocres2, path):
    """
    execute_fscq
    """
    params = "scipion3 run xmipp_image_operate"
    params += f" -i {path}/{blocres1}"
    params += f" --minus {path}/{blocres2}"
    params += f" -o {path}/fscq_dif.vol"
    os.system(params)


def fscq_to_pdb(pdbId, sampling, org_x, org_y, org_z, path):
    """
    fscq_to_pdb
    """
    params = "scipion3 run xmipp_pdb_label_from_volume"
    params += f" --pdb {path}/pdb{pdbId}.ent"
    params += f" --vol {path}/fscq_dif.vol"
    params += f" --mask {path}/mask.vol"
    params += f" --sampling {sampling}"
    params += f" --origin {org_x} {org_y} {org_z}"
    params += f" -o {path}/{pdbId}.fscq.atom.pdb"
    os.system(params)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute FSC-Q")
    parser.add_argument(
        "-i",
        "--map",
        help="input map EMDB ID (just the numeric part, without EMD-)",
        required=True,
    )
    parser.add_argument(
        "-p", "--pdb", help="input atomic model PDB ID", required=True)
    parser.add_argument(
        "-d", "--workdir", help="path to working directory", required=False
    )
    args = parser.parse_args()

    mapId = args.map
    pdbId = args.pdb
    path = args.workdir or WORK_PATH

    # Create (if not exists) working directory
    workpath = create_work_dir(path, mapId)
    print(f"-> Working dir {workpath}")

    # Download EMDB map file
    inMap = download_emdb_map(mapId, workpath)
    # Can not continue without inMap file
    if not inMap:
        raise ValueError("Can not continue. No volume MAP found")
    print(f"-> Input volume MAP {workpath}, {inMap}")

    # Download PDB model file
    inPdb = download_pdb_model(pdbId, workpath)
    # Can not continue without inPdb file
    if not inPdb:
        raise ValueError("Can not continue. No atom MODEL found")
    print(f"-> Input atom model {workpath}, {inPdb}")

    # Delete Hidrogens
    inPdb_nH = delete_hidrogens(inPdb, pdbId, workpath)
    print(f"-> Atom model, H atoms deleted {inPdb_nH}")
    inPdb = inPdb_nH

    # Download EMDB metadata
    resolution, sampling, size, org_x, org_y, org_z = get_parameters(
        mapId, workpath)
    print("-> Parameters: ")
    print(f"\tresolution = {resolution}")
    print(f"\tsampling = {sampling}")
    print(f"\tsize = {size}")
    print(f"\torigin = ({org_x},{org_y},{org_z})")

    print("-> Download half-maps")
    MAP_E = "EMD-" + mapId
    HALF1 = "EMD-" + mapId + "_half_1.mrc"
    HALF2 = "EMD-" + mapId + "_half_2.mrc"
    download_emdb_halfmaps(MAP_E, workpath)

    # . . . . . . . . . . . . . . . . . . . . . . . . .

    print("-> Create mapPDB and mask")
    create_mask_fscq(inMap, inPdb, sampling, size, workpath)

    print("-> Executing blocres1")
    execute_blocres(HALF1, HALF2, sampling, resolution, 0.5, workpath, "half")

    print("-> Executing blocres2")
    MAP2 = "align.mrc"
    execute_blocres(inMap, MAP2, sampling, resolution, 0.67, workpath, "model")

    print("-> Calculating FSC-Q map (difference map)")
    BLOCRES_HALF = "blocres_half.map"
    BLOCRES_MODEL = "blocres_model.map"
    execute_fscq(BLOCRES_MODEL, BLOCRES_HALF, workpath)

    print("-> pdb label from FSC-Q map")
    fscq_to_pdb(pdbId, sampling, org_x, org_y, org_z, workpath)

    # . . . . . . . . . . . . . . . . . . . . . . . . .

    print("-> Average amino-acids")
    print("-> Save to aa.PDB")
    convert_to_aapdb(
        pdbId, workpath, cmd="convert_fscq_to_aapdb.py", method="FscQ")

    print("-> Save to JSON")
    convert_to_json(
        mapId, pdbId, workpath, cmd="convert_fscq_to_json.py", method="FscQ"
    )
