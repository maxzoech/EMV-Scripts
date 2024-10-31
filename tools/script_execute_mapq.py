"""
Excute mapQ automatically
"""
import os
import os.path
import time
import argparse
from script_emv_setup import (
    TOOLS_PATH,
    WORK_PATH,
    create_work_dir,
    download_emdb_map,
    download_pdb_model,
    delete_hidrogens,
    convert_to_json,
)


def execute_mapq(map_filename, pdb, dir_path):
    """compute MapQ"""
    os_command = f"python3 {TOOLS_PATH}mapq_chimera/mapq_cmd.py \
        /home/bioinfo/.local/UCSF-Chimera64-1.14/ {dir_path}/{map_filename} {dir_path}/{pdb} np=8"
    print("--> Map-Q command:", os_command)
    os.system(os_command)


def convert_mapq_to_aapdb(mapq, aa_pdb, dir_path):
    """Save to aa.PDB file"""
    os_command = f"python3 {TOOLS_PATH}convert_mapQvol_to_pdb.py \
        {dir_path}/{mapq} {dir_path}/{aa_pdb}"
    os.system(os_command)


def waitfor(file_path):
    """wait for file"""
    print(f"--> Waiting for file {file_path}")

    while not os.path.exists(file_path):
        time.sleep(10000)
        print("---> Still waiting")

    print(f"--> Found file {file_path}")
    print("--> We can proceed")


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
    print(f"-> Working dir {workpath}")

    # Download EMDB map file
    inMap = download_emdb_map(mapId, workpath)
    # Can not continue without inMap file
    if not inMap:
        raise ValueError("Can not continue. No volume MAP found")
    print(f"-> Input volume MAP {workpath} {inMap}")

    # Download PDB model file
    inPdb = download_pdb_model(pdbId, workpath)
    # Can not continue without inPdb file
    if not inPdb:
        raise ValueError("Can not continue. No atom MODEL found")
    print(f"-> Input atom model {workpath}, {inPdb}")

    # wait for input files
    inPdb_path = os.path.join(workpath, inPdb)
    waitfor(inPdb_path)

    # Delete Hidrogens
    inPdb_nH = delete_hidrogens(inPdb, pdbId, workpath)
    print(f"-> Atom model, H atoms deleted {inPdb_nH}")
    inPdb = inPdb_nH

    # . . . . . . . . . . . . . . . . . . . . . . . . .

    # wait for input files
    inPdb_path = os.path.join(workpath, inPdb)
    waitfor(inPdb_path)

    print("-> Compute mapQ")
    execute_mapq(inMap, inPdb, workpath)

    # . . . . . . . . . . . . . . . . . . . . . . . . .

    print("-> Save to aa.PDB")
    # pdb7uqi_nH__Q__emd_26695.pdb
    mapq_filename = "pdb" + pdbId + "_nH__Q__emd_" + mapId + ".pdb"
    aa_pdb_filename = pdbId + ".mapq.aa.pdb"
    convert_mapq_to_aapdb(mapq_filename, aa_pdb_filename, workpath)

    print("-> Save to JSON")
    convert_to_json(
        mapId, pdbId, workpath, cmd="convert_mapQvol_to_json.py", method="mapQ"
    )
