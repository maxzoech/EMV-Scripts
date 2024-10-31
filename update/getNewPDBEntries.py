import getopt
import sys
import os
import csv
import requests
from datetime import datetime, timedelta
from rcsbsearch import rcsb_attributes as attrs, TextQuery

WS_URL = "https://3dbionotes.cnb.csic.es/api/mappings/PDB/EMDB/"
DAYS_INTERVAL = 7
PATH_DATA = "/home/bioinfo/services/emv/update/data"
FN_PDB_ENTRIES = "_new-all_entries_noem.txt"
FN_EM_ENTRIES = "_new-all_entries_em.txt"
FN_EMDB_PDB_ENTRIES = "_new-all_entries_mappings.csv"


def getNewPDBEntries(d1, interval, withEM=False):

    iso1 = d1.replace(microsecond=0).isoformat()

    d0 = d1 - timedelta(days=interval)
    iso0 = d0.replace(microsecond=0).isoformat()

    q2 = attrs.rcsb_accession_info.initial_release_date >= str(iso0+'Z')
    q3 = attrs.rcsb_accession_info.initial_release_date <= str(iso1+'Z')
    q4 = attrs.rcsb_entry_info.experimental_method != "EM"
    q5 = attrs.rcsb_entry_info.experimental_method == "EM"
    query = q2 & q3
    if withEM:
        query = query & q5
    else:
        query = query & q4

    return list(query())


def save2file(list, filename):
    if list:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as filehandle:
            filehandle.writelines("%s\n" % entry for entry in list)


def save2csv(list, filename, delimiter='\t'):
    if list:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=delimiter)
            writer.writerows(list)


def getPdbMappings(entryList):
    emdbEntries = []
    for entry in entryList:
        response = requests.get(WS_URL + entry)
        if response.status_code == 200:
            jresp = response.json()
            emdbEntries.append((jresp[entry.lower()][0], entry.lower()))
    return emdbEntries


def getEMDBMappings(entryList):
    # https://www.ebi.ac.uk/pdbe/api/pdb/entry/summary/7x7n
    url = 'https://www.ebi.ac.uk/pdbe/api/pdb/entry/summary/'
    emdbEntries = []
    for entry in entryList:
        response = requests.get(url + entry)
        if response.status_code == 200:
            jresp = response.json()
            if jresp[entry.lower()][0]['related_structures']:
                resource = jresp[entry.lower(
                )][0]['related_structures'][0]['resource']
                accession = jresp[entry.lower(
                )][0]['related_structures'][0]['accession']
                relationship = jresp[entry.lower(
                )][0]['related_structures'][0]['relationship']
                if resource == 'EMDB':
                    emdbEntries.append((accession, entry.lower()))
    return emdbEntries


def main(argv):
    endDate = ''
    interval = ''
    try:
        opts, args = getopt.getopt(argv, 'hd:i:', ['endDate=', 'interval='])
    except getopt.GetoptError:
        print('getCovidEntries.py -d <endDate> -i <interval>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('getCovidEntries.py -d <endDate> -i <interval>')
            sys.exit()
        elif opt in ('-d', '--endDate'):
            endDate = datetime.strptime(arg, '%d/%m/%Y')
        elif opt in ('-i', '--interval'):
            interval = int(arg)

    if not endDate:
        endDate = datetime.today()
    if not interval:
        interval = DAYS_INTERVAL

    print('Get latest Non EM-PDB Entries:', endDate, interval)
    noem_entries = getNewPDBEntries(endDate, interval, withEM=False)
    print("-> Found", len(noem_entries), noem_entries)
    save2file(sorted(noem_entries), filename=os.path.join(
        PATH_DATA, endDate.date().isoformat() + FN_PDB_ENTRIES))

    print("Get latest EM-PDB Entries",  endDate, interval)
    em_entries = getNewPDBEntries(endDate, interval, withEM=True)
    print("-> Found", len(em_entries), em_entries)
    save2file(sorted(em_entries), filename=os.path.join(
        PATH_DATA, endDate.date().isoformat() + FN_EM_ENTRIES))

    print("Get latest mappings EM-PDB",  endDate, interval)
    # mappings = getPdbMappings(em_entries)
    mappings = getEMDBMappings(em_entries)
    print("->", mappings)
    save2csv(mappings, filename=os.path.join(
        PATH_DATA, endDate.date().isoformat() + FN_EMDB_PDB_ENTRIES))

    # save latest without date
    save2file(sorted(noem_entries), filename=os.path.join(
        PATH_DATA, "new-all_entries_noem.txt"))
    save2file(sorted(em_entries), filename=os.path.join(
        PATH_DATA, "new-all_entries_em.txt"))
    save2csv(mappings, filename=os.path.join(
        PATH_DATA, "new-all_entries_mappings.csv"))


if __name__ == '__main__':
    main(sys.argv[1:])
