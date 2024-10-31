"""
execute deepRes automatically
"""


import os
import os.path
import argparse
import xmippLib
from script_emv_setup import (
    WORK_PATH,
    create_work_dir,
    download_emdb_map,
    download_pdb_model,
    delete_hidrogens,
    get_parameters,
    convert_to_aapdb,
    convert_to_json,
)


def createMaskDeepRes(map, pdb, sampling, size, path):
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


def resize_map(map, resolution, sampling, path):
    base = map.split(".")
    print(base[0])

    if resolution >= 2.7:
        new_sampling = 1.0
    else:
        new_sampling = 0.5

    samplingFactor = sampling / new_sampling
    fourierValue = sampling / (2 * new_sampling)

    if sampling > new_sampling:
        # map with sampling=1.0
        paramsResizeVol = " scipion3 run xmipp_image_resize"
        paramsResizeVol += " -i %s/%s" % (path, map)
        paramsResizeVol += " -o %s/resize_%s.vol" % (path, base[0])
        paramsResizeVol += " --factor %s" % samplingFactor
        os.system(paramsResizeVol)
    else:
        paramsFilterVol = " scipion3 run xmipp_transform_filter"
        paramsFilterVol += " -i %s/%s" % (path, map)
        paramsFilterVol += " -o %s/resize_%s.vol" % (path, base[0])
        paramsFilterVol += " --fourier low_pass %s" % fourierValue
        os.system(paramsFilterVol)
        paramsResizeVol = " scipion3 run xmipp_image_resize"
        paramsResizeVol += " -i %s/resize_%s.vol" % (path, base[0])
        paramsResizeVol += " -o %s/resize_%s.vol" % (path, base[0])
        paramsResizeVol += " --factor %s" % samplingFactor
        os.system(paramsResizeVol)


def transform_thr(map, path):
    base = map.split(".")
    print(base[0])

    params = "scipion3 run xmipp_transform_threshold"
    params += " -i %s/resize_%s.vol" % (path, base[0])
    params += " -o %s/resize_%s.vol" % (path, base[0])
    params += " --select below %f" % 0.15
    params += " --substitute binarize"
    os.system(params)


def execute_deepRes(map, resolution, path):
    base = map.split(".")

    if resolution >= 2.7:
        model = (
            "/home/bioinfo/services/emv/tools/xmipp/build/models/deepRes/model_w13.h5"
        )
        sampling = 1.0
    else:
        model = (
            "/home/bioinfo/services/emv/tools/xmipp/build/models/deepRes/model_w7.h5"
        )
        sampling = 0.5

    params = " scipion3 run xmipp_deepRes_resolution"
    params += " -dl %s" % model
    params += " -i %s/resize_%s.vol" % (path, base[0])
    params += " -m %s/resize_mask.vol" % path
    params += " -s %f" % sampling
    params += " -o %s/deepRes.vol" % path
    os.system(
        ". /home/bioinfo/services/tools/miniconda3/etc/profile.d/conda.sh && conda activate xmipp_DLTK_v0.3 && %s"
        % params
    )


def resize_output(size, resolution, path):
    if resolution >= 2.7:
        resize_samp = 1.0
    else:
        resize_samp = 0.5

    deepVol = path + "/deepRes.vol"
    V = xmippLib.Image(deepVol).getData()
    Zdim, Ydim, Xdim = V.shape

    factor = size / Zdim
    finalSamp = resize_samp / factor
    fourierV = resize_samp / 2 * finalSamp

    params = " scipion3 run xmipp_transform_filter"
    params += " -i %s" % deepVol
    params += " -o %s/output_deepRes.vol" % path
    params += " --fourier low_pass %f" % fourierV
    os.system(params)

    params = " scipion3 run xmipp_image_resize"
    params += " -i %s" % deepVol
    params += " -o %s/output_deepRes.vol" % path
    params += " --dim %f" % size
    os.system(params)


def resolution_to_pdb(pdbId, map, sampling, org_x, org_y, org_z, path):
    params = "scipion3 run xmipp_pdb_label_from_volume"
    params += " --pdb %s/pdb%s.ent" % (path, pdbId)
    params += " --vol %s/output_deepRes.vol" % path
    params += " --mask %s/mask.vol" % path
    params += " --sampling %f" % sampling
    params += " --origin %f %f %f" % (org_x, org_y, org_z)
    params += " -o %s/%s.deepres.atom.pdb" % (path, pdbId)
    os.system(params)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute DeepRes")
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
    resolution, sampling, size, org_x, org_y, org_z = get_parameters(
        mapId, workpath)
    print(f"-> Parameters: ")
    print(f"\tresolution = %f" % resolution)
    print(f"\tsampling = %f" % sampling)
    print(f"\tsize = %d" % size)
    print(f"\torigin = (%f,%f,%f)" % (org_x, org_y, org_z))

    # . . . . . . . . . . . . . . . . . . . . . . . . .

    print("-> Create mask")
    createMaskDeepRes(inMap, inPdb, sampling, size, workpath)

    print("-> Resize map")
    resize_map(inMap, resolution, sampling, workpath)
    mask = "mask.vol"

    print("--> Resize mask")
    resize_map(mask, resolution, sampling, workpath)

    print("-> Transform mask threshold")
    transform_thr(mask, workpath)

    print("-> Execute deepRes")
    execute_deepRes(inMap, resolution, workpath)

    print("-> Resize deepRes map")
    resize_output(size, resolution, workpath)
    deepResVol = "output_deepRes.vol"

    print("-> Pdb label from deepRes map")
    resolution_to_pdb(pdbId, deepResVol, sampling,
                      org_x, org_y, org_z, workpath)

    # . . . . . . . . . . . . . . . . . . . . . . . . .

    print("-> Average amino-acids resolution")
    print("-> Save to aa.PDB")
    convert_to_aapdb(
        pdbId, workpath, cmd="convert_deepres_to_aapdb.py", method="DeepRes"
    )

    print("-> Save to JSON")
    convert_to_json(
        mapId, pdbId, workpath, cmd="convert_localres_to_json.py", method="DeepRes"
    )
