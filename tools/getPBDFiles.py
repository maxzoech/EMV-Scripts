import getopt
import getopt
import sys
import urllib
import glob
import os
import requests

SCRIPT_NAME = "getPBDFiles"
DATA_PATH_DEFAULT = "../data/emdbs"
WS_PDB_FITTING_URL = "https://3dbionotes.cnb.csic.es/api/mappings/PDB/EMDB/"
WS_EMDB_FITTING_URL = "https://3dbionotes.cnb.csic.es/api/mappings/EMDB/PDB/"
URL_PDBE = "https://www.ebi.ac.uk/pdbe/entry-files/download/"
URL_RCSB = "https://files.rcsb.org/download/"


def getPdbMapping(entry):
    ws_url = WS_EMDB_FITTING_URL

    response = requests.get(ws_url + entry)
    if response.status_code == 200:
        jresp = response.json()
        mappings = jresp[entry]
        print('Found mappings', entry, mappings)
    return mappings


def downloadFile(pdbcode, datadir, file_format="pdb"):
    """
    Downloads a PDB file from the Internet and saves it in a data directory.
    :param pdbcode: The standard PDB ID e.g. '3ICB' or '3icb'
    :param datadir: The directory where the downloaded file will be saved
    :param downloadurl: The base PDB download URL, cf.
        `https://www.rcsb.org/pages/download/http#structures` for details
    :return: the full path to the downloaded PDB file or None if something went wrong
    """

    if file_format == "pdb":
        urlPath = URL_PDBE
        pdbfn = pdbcode + ".pdb"
    elif file_format == "cif":
        urlPath = URL_RCSB
        pdbfn = pdbcode + ".cif"
    elif file_format == "ent":
        urlPath = URL_PDBE
        pdbfn = "pdb" + pdbcode + ".ent"

    outfnm = os.path.join(datadir, pdbfn)
    if os.path.isfile(outfnm):
        print("Found", outfnm)
        return

    url = urlPath + pdbfn
    print('Downloading', pdbfn, url)
    try:
        urllib.request.urlretrieve(url, outfnm)
        return outfnm
    except Exception as err:
        print(str(err), file=sys.stderr)
        return None


def searchDirPath(path):
    for emdbDir in glob.glob(os.path.join(path, 'emd-*'), recursive=True):
        entry = os.path.basename(emdbDir).upper()
        print('Found', entry, emdbDir)

        mappings = getPdbMapping(entry)
        for pdbId in mappings:
            downloadFile(pdbId, emdbDir, file_format="cif")
            if not downloadFile(pdbId, emdbDir, file_format="pdb"):
                downloadFile(pdbId, emdbDir, file_format="ent")
#        break


def main(argv):
    path = ''
    try:
        opts, args = getopt.getopt(argv, 'hp:', ['path=', ])
    except getopt.GetoptError:
        print(SCRIPT_NAME, '-p <path>')
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print(SCRIPT_NAME, '-p <path>')
            sys.exit()
        elif opt in ('-p', '--path'):
            path = arg

    if not path:
        # print(SCRIPT_NAME, '-p <path>')
        # sys.exit(2)
        path = DATA_PATH_DEFAULT

    print('Searching for PDB files in', path)
    searchDirPath(path)


if __name__ == '__main__':
    main(sys.argv[1:])

