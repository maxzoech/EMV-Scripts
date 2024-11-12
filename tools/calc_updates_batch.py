#!/usr/local/bin/python
"""
calcUpdates batch
"""

import os
import sys
import csv
import subprocess
import argparse
from script_emv_setup import TOOLS_PATH


METHODS = [
    "mapq",
    "fscq",
    "daq",
    "deepres",
    "monores",
    "blocres",
    "statslocalres",
    "init",
]
METHOD_SCRIPTS = {
    "mapq": "queue_script_mapq.sh",
    "fscq": "queue_script_fscq.sh",
    "daq": "queue_script_daq.sh",
    "deepres": "queue_script_deepres.sh",
    "monores": "queue_script_monores.sh",
    "blocres": "queue_script_blocres.sh",
    "statslocalres": "queue_script_localres_stats.sh",
    "init": "queue_script_init.sh",
}
METHOD_INITIALS = {
    "mapq": "MQ",
    "fscq": "FQ",
    "daq": "DQ",
    "deepres": "DR",
    "monores": "MR",
    "blocres": "BR",
    "statslocalres": "LR",
    "init": "IN",
}


def submit_init_job(map_id, pdb_id):
    """
    submit the first job
    """
    method = "init"
    script_name = "queue_script_init.sh"
    print(f"->>> Downloading needed files for EMDB: {map_id} - PDB: {pdb_id}")
    cmmd = f"sbatch \
        --job-name={METHOD_INITIALS[method]}-{map_id} \
        --output=/home/bioinfo/services/emv/logs/%j_%x.out \
        --error=/home/bioinfo/services/emv/logs/%j_%x.err \
        {os.path.join(TOOLS_PATH, script_name)} {map_id} {pdb_id}"
    cmmd = " ".join(cmmd.split())
    print(f"->>> Submitting job {method.upper()} with command: {cmmd}")
    status, output_msg = subprocess.getstatusoutput(cmmd)
    if status == 0:
        print(f"->>> output_msg: {output_msg}, status: {status}")
    else:
        print(f"->>> Error submitting Job {script_name}")

    return output_msg.split()[-1]


def get_queue_cmmd_dependant(map_id, pdb_id, parent_job_id, method, script_name):
    """
    get queue command dependant
    """
    cmmd = f"sbatch \
        --job-name={METHOD_INITIALS[method]}-{map_id} \
        --dependency=afterok:{parent_job_id} \
        --output=/home/bioinfo/services/emv/logs/%j_%x.out \
        --error=/home/bioinfo/services/emv/logs/%j_%x.err \
        {os.path.join(TOOLS_PATH, script_name)} {map_id} {pdb_id}"
    return " ".join(cmmd.split())


def submit_dependant_job(map_id, pdb_id, parent_job_id, method):
    """
    submit dependant job
    """
    print(
        f"->>> Calculating {method.upper()} for EMDB: {map_id} - PDB: {pdb_id}")
    cmmd = get_queue_cmmd_dependant(
        map_id, pdb_id, parent_job_id, method, METHOD_SCRIPTS[method]
    )
    print(f"->>> Submitting job {method.upper()} with command: {cmmd}")
    status, output_msg = subprocess.getstatusoutput(cmmd)
    if status == 0:
        print(f"->>> output_msg: {output_msg}, status: {status}")
    else:
        print(f"->>> Error submitting Job: {method} {METHOD_SCRIPTS[method]}")


def read_entries_file(filename, method):
    """
    read entries file
    """
    print("->>> Reading entries from", filename)
    with open(filename, encoding="utf-8") as csvfile:
        rdr = csv.reader(csvfile, delimiter=" ", quotechar="|")
        for row in rdr:
            data = ", ".join(row)
            map_id = data.split()[0].replace("EMD-", "")
            pdb_id = data.split()[1]
            print("Sending JOBS for", map_id, pdb_id, method)
            job_id = submit_init_job(map_id, pdb_id)
            if method:
                print("-->>> Computing", method, "for", map_id, pdb_id)
                submit_dependant_job(map_id, pdb_id, job_id, method)
            else:
                # volume-map quality
                submit_dependant_job(map_id, pdb_id, job_id, "mapq")
                submit_dependant_job(map_id, pdb_id, job_id, "fscq")
                # submit_dependant_job(map_id, pdb_id, job_id, "daq")
                # local resolution
                submit_dependant_job(map_id, pdb_id, job_id, "blocres")
                submit_dependant_job(map_id, pdb_id, job_id, "monores")
                submit_dependant_job(map_id, pdb_id, job_id, "deepres")
                # db statistics
                submit_dependant_job(map_id, pdb_id, job_id, "statslocalres")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compute EM Validation methods")
    parser.add_argument(
        "-i",
        "--inputfile",
        help="input map EMDB ID (just the numeric part, without EMD-)",
        required=True,
    )
    parser.add_argument(
        "-m",
        "--method",
        help="method to compute [init, mapq, fscq, daq, deepres, monores, blocres, statslocalres]",
        required=False,
    )
    args = parser.parse_args()
    input_filename = args.inputfile
    input_method = args.method
    if input_method and input_method not in METHODS:
        print("ERROR: Method not valid.", input_method)
        sys.exit(2)

    if input_filename:
        read_entries_file(input_filename, input_method)
