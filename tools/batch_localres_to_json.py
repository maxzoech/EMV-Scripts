"""
Passing EM Validations to JSON Data Format
"""
import argparse
import getopt
import os
import re
import sys


DATA_PATH = "../data/emdbs"
METHODS = ["DeepRes", "MonoRes", "BlocRes"]


def convert_to_json(path, method):
    """
    Convert to JSON
    """
    IN_FILE_SUFIX = "." + method.lower() + ".atom.pdb"
    IN_FILE_REGEX = "[0-9][A-Za-z0-9]{3}" + IN_FILE_SUFIX
    OUT_FILE_SUFIX = "_emv_" + method.lower() + ".json"
    CONVERT_CMD = "convert_localres_to_json.py"
    print('-- Searching files:', IN_FILE_SUFIX)
    try:
        for file in os.listdir(path):
            entry_path = os.path.join(path, file)
            print("--- Reading data folder: ", entry_path)
            data_files = [f for f in os.listdir(
                entry_path) if re.match(IN_FILE_REGEX, f)]
            print("---- data files: ", data_files)

            if data_files:
                emdb_entry = entry_path.split('/')[-1]
                for data_file in data_files:
                    pdb_entry = data_file.split('.')[0]
                    json_file = emdb_entry + '_' + pdb_entry + OUT_FILE_SUFIX

                    # convert local_res to JSON
                    os_command = ' python ' + CONVERT_CMD
                    os_command += ' %s/%s%s' % (entry_path,
                                                pdb_entry, IN_FILE_SUFIX)
                    os_command += ' %s/%s_%s%s' % (entry_path,
                                                   emdb_entry, pdb_entry, OUT_FILE_SUFIX)
                    os_command += ' %s' % method
                    print('----- Command:', os_command)
                    os.system(os_command)

    except(Exception) as exc:
        print(exc)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="BATCH Convert EMV *aa.pdb to *.json")
    parser.add_argument("-p", "--path",
                        help="path to data directory", required=False)
    parser.add_argument("-m", "--method",
                        choices=['DeepRes', 'MonoRes', 'BlocRes'],
                        help="list of validation methods", required=True)
    args = parser.parse_args()
    path = args.path or DATA_PATH
    method = args.method

    print('Passing EM Validations to JSON Data Format')
    print("- Processing", path)
    convert_to_json(path, method)
