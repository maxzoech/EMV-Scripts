from requests.adapters import HTTPAdapter
import getopt
import sys
import os
import csv
import requests

WS_URL_EMDB2PDB = "http://3dbionotes.cnb.csic.es/api/mappings/EMDB/PDB/"
PATH_DATA = "data"
FN_EMDB_PDB_ENTRIES = "emdb2pdb_mappings.csv"


def save2csv(list, filename, delimiter='\t'):
    if list:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=delimiter)
            writer.writerows(list)


def getPdbMappings(entryList):
    emdbEntries = []
    ws_adapter = HTTPAdapter(max_retries=3)
    session = requests.Session()
    session.mount(WS_URL_EMDB2PDB, ws_adapter)


    for entry in entryList:
        entry = entry.upper()
        # response = requests.get(WS_URL_EMDB2PDB + entry, timeout=(12, 15))
        response = session.get(WS_URL_EMDB2PDB + entry)
        print(entry, WS_URL_EMDB2PDB + entry, response.status_code)
        if response.status_code == 200:
            jresp = response.json()
            emdbEntries.append((entry, jresp[entry][0]))
    return emdbEntries


def readEmdbIdsFromFile(filename):
    with open(filename, 'r') as filehandle:
        emdb_list = filehandle.readlines()
    return emdb_list


def main(argv):
    emdbfilename = ''
    try:
        opts, args = getopt.getopt(argv, 'hf:', ['filename='])
    except getopt.GetoptError:
        print('getEmdb2PdbMappings.py -f <filename>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('getEmdb2PdbMappings.py -f <filename>')
            sys.exit()
        elif opt in ('-f', '--filename'):
            emdbfilename = arg

    print("Get mappings EMDB-PDB",  emdbfilename)

    em_entries = readEmdbIdsFromFile(emdbfilename)
    mappings = getPdbMappings(em_entries)
    print(mappings)
    save2csv(mappings, filename=os.path.join(
        PATH_DATA, FN_EMDB_PDB_ENTRIES))


if __name__ == '__main__':
    main(sys.argv[1:])
