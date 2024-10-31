"""
Passing EM Validations to JSON Data Format
"""
import getopt
import os
import re
import sys


DATA_PATH = "../data/emdbs"
MAPQ_FILE_REGEX = "[0-9][A-Za-z0-9]{3}.fscq.atom.pdb"


def read_em_validations(path):
    """
    Read EM Validations
    """
    print('-- Reading EM Validations from', path)

    try:
        for file in os.listdir(path):
            entry_path = os.path.join(path, file)
            print("--- Reading data folder: ", entry_path)
            data_files = [f for f in os.listdir(
                entry_path) if re.match(MAPQ_FILE_REGEX, f)]
            print("---- data-files: ", data_files)

            if data_files:
                emdb_entry = entry_path.split('/')[-1]
                for data_file in data_files:
                    pdb_entry = data_file.split('.')[0]
                    json_file = emdb_entry + '_' + pdb_entry + '_emv_fscq.json'

                    # convert FscQ to JSON
                    os_command = ' python convert_fscq_to_json.py'
                    os_command += ' %s/%s.fscq.atom.pdb' % (entry_path, pdb_entry)
                    os_command += ' %s/%s' % (entry_path, json_file)
                    print('----- Command:', os_command)
                    os.system(os_command)

    except(Exception) as exc:
        print(exc)


def main(argv):
    path = ''
    try:
        opts, args = getopt.getopt(argv, 'hp:', ['path=', ])
    except getopt.GetoptError:
        print(__name__, ' -p <path>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(__name__, ' -p <path>')
            sys.exit()
        elif opt in ('-p', '--path'):
            path = arg

    if not path:
        path = DATA_PATH

    print('Passing EM Validations to JSON Data Format')
    print("- Processing", path)
    read_em_validations(path)


if __name__ == '__main__':
    main(sys.argv[1:])
