"""
Excute mapQ automatically
"""

import argparse
from script_emv_setup import (
    WORK_PATH,
    create_work_dir,
    download_emdb_map,
    download_pdb_model,
    download_emdb_half_maps,
    get_parameters,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute Map-Q")
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
    print("-> Working dir", workpath)

    # Download EMDB map file
    inMap = download_emdb_map(mapId, workpath)
    # Can not continue without inMap file
    if not inMap:
        raise ValueError("Can not continue. No volume MAP found")
    print("-> Input volume MAP", workpath, inMap)

    # Download EMDB metadata JSON file
    resolution, sampling, size, org_x, org_y, org_z = get_parameters(mapId, workpath)

    # Download half-maps if available
    hmap1, hmap2 = download_emdb_half_maps(mapId, workpath)

    # Download PDB model file
    inPdb = download_pdb_model(pdbId, workpath)
    # Can not continue without inPdb file
    if not inPdb:
        raise ValueError("Can not continue. No atom MODEL found")
    print("-> Input atom model", workpath, inPdb)
