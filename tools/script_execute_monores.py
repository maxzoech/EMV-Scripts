"""
execute monores automatically
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
    download_emdb_halfmaps,
    get_parameters,
    convert_to_aapdb,
    convert_to_json,
)


def createMaskMonoRes(map, pdb, sampling, size, path):
    """Convert PDB to Map"""
    params = " scipion3 run xmipp_volume_from_pdb "
    params += " --centerPDB "
    params += " -v 0 "
    params += " --sampling %f" % sampling
    params += " --size %d" % size
    params += " -i %s/%s" % (path, pdb)
    params += " -o %s/pdbMap" % path
    os.system(params)

    """ Align pdbMap to reconstruction Map """
    params = " scipion3 run xmipp_volume_align"
    params += " --i1 %s/%s" % (path, map)
    params += " --i2 %s/pdbMap.vol" % path
    params += " --local --apply"
    params += " %s/align.vol" % path
    os.system(params)

    """create mask"""
    params = " scipion3 run xmipp_transform_threshold"
    params += " -i %s/align.vol" % path
    params += " -o %s/mask.vol" % path
    params += " --select below 0.02 --substitute binarize"
    os.system(params)

    params = " scipion3 run xmipp_transform_morphology"
    params += " -i %s/mask.vol" % path
    params += " -o %s/mask.vol" % path
    params += " --binaryOperation dilation --size 2"
    os.system(params)


def execute_monores(half1, half2, sampling, path):
    params = "scipion3 run xmipp_resolution_monogenic_signal"
    params += " --vol %s/%s:mrc" % (path, half1)
    params += " --vol2 %s/%s:mrc" % (path, half2)
    params += " --mask %s/mask.vol" % (path)
    params += " --sampling_rate %f" % sampling
    params += " --minRes 1.0 --maxRes 14.0 --threads 8"
    params += " -o %s" % (path)
    os.system(params)


def monores_to_pdb(pdbId, sampling, org_x, org_y, org_z, path):
    params = "scipion3 run xmipp_pdb_label_from_volume"
    params += " --pdb %s/pdb%s.ent" % (path, pdbId)
    params += " --vol %s/monoresResolutionMap.mrc:mrc" % path
    params += " --mask %s/mask.vol" % path
    params += " --sampling %f" % sampling
    params += " --origin %f %f %f" % (org_x, org_y, org_z)
    params += " -o %s/%s.monores.atom.pdb" % (path, pdbId)
    os.system(params)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute MonoRes")
    parser.add_argument(
        "-i",
        "--map",
        help="input map EMDB ID (just the numeric part, without EMD-)",
        required=True,
    )
    parser.add_argument("-p", "--pdb", help="input atomic model PDB ID", required=True)
    parser.add_argument(
        "-d", "--workdir", help="path to working directory", required=False
    )
    args = parser.parse_args()

    mapId = args.map
    pdbId = args.pdb
    path = args.workdir or WORK_PATH

    # Create (if not exists) working directory
    workpath = create_work_dir(path, mapId)
    print(f"-> Working dir", workpath)

    # Download EMDB map file
    inMap = download_emdb_map(mapId, workpath)
    # Can not continue without inMap file
    if not inMap:
        raise ValueError("Can not continue. No volume MAP found")
    print(f"-> Input volume MAP", workpath, inMap)

    # Download PDB model file
    inPdb = download_pdb_model(pdbId, workpath)
    # Can not continue without inPdb file
    if not inPdb:
        raise ValueError("Can not continue. No atom MODEL found")
    print(f"-> Input atom model", workpath, inPdb)

    # Delete Hidrogens
    inPdb_nH = delete_hidrogens(inPdb, pdbId, workpath)
    print(f"-> Atom model, H atoms deleted", inPdb_nH)
    inPdb = inPdb_nH

    # Download EMDB metadata
    resolution, sampling, size, org_x, org_y, org_z = get_parameters(mapId, workpath)
    print(f"-> Parameters: ")
    print(f"\tresolution = %f" % resolution)
    print(f"\tsampling = %f" % sampling)
    print(f"\tsize = %d" % size)
    print(f"\torigin = (%f,%f,%f)" % (org_x, org_y, org_z))

    print("-> Download half-maps")
    mapE = "EMD-" + mapId
    half1 = "EMD-" + mapId + "_half_1.mrc"
    half2 = "EMD-" + mapId + "_half_2.mrc"
    download_emdb_halfmaps(mapE, workpath)

    # . . . . . . . . . . . . . . . . . . . . . . . . .

    print("-> Create mapPDB and mask")
    createMaskMonoRes(inMap, inPdb, sampling, size, workpath)

    print("-> Executing monores")
    execute_monores(half1, half2, sampling, workpath)

    print("-> pdb label from monores map")
    monores_to_pdb(pdbId, sampling, org_x, org_y, org_z, workpath)

    # . . . . . . . . . . . . . . . . . . . . . . . . .

    print("-> Average amino-acids")
    print("-> Save to aa.PDB")
    convert_to_aapdb(
        pdbId, workpath, cmd="convert_deepres_to_aapdb.py", method="MonoRes"
    )

    print("-> Save in JSON format")
    convert_to_json(
        mapId, pdbId, workpath, cmd="convert_localres_to_json.py", method="MonoRes"
    )
