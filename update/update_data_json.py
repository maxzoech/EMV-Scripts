import requests
import getopt
import getopt
import sys
import json
import os
import csv


WS_PDB_FITTING_URL = "https://3dbionotes.cnb.csic.es/api/mappings/PDB/EMDB/"
WS_EMDB_FITTING_URL = "https://3dbionotes.cnb.csic.es/api/mappings/EMDB/PDB/"
PATH_DATA = "data_all"
FN_NAMES = "names_covid.txt"
FN_DESCRIPTIONS = "descriptions_covid.txt"
FN_PDB_ENTRIES = "pbd_entries_covid.txt"
FN_EMDB_ENTRIES = "emdb_entries_covid.txt"
FN_COMP_MODELS = "comp_models_covid.txt"
FN_REL_PDB_ENTRIES = "rel_pbd_entries_covid.txt"
FN_REL_EMDB_ENTRIES = "rel_embd_entries_covid.txt"
FN_PDB_EMDB_MAPPINGS = "pdb_emdb_mappings_covid.csv"
FN_EMDB_PDB_MAPPINGS = "emdb_pdb_mappings_covid.csv"
FN_REL_PDB_EMDB_MAPPINGS = "rel_pdb_emdb_mappings_covid.csv"
FN_REL_EMDB_PDB_MAPPINGS = "rel_emdb_pdb_mappings_covid.csv"
FN_ALL_MAPPINGS = "all_mappings_covid.csv"


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


def getPdbMappings(entryList, inputType='pdbs'):
    if inputType == 'pdbs':
        ws_url = WS_PDB_FITTING_URL
    elif inputType == 'emdbs':
        ws_url = WS_EMDB_FITTING_URL
    mappings = []
    for entry in entryList:
        response = requests.get(ws_url + entry)
        if response.status_code == 200:
            jresp = response.json()
            if inputType == 'pdbs' and len(jresp[entry]) > 0:
                mappings.append((jresp[entry.lower()][0], entry.lower()))
            elif inputType == 'emdbs' and len(jresp[entry]) > 0:
                mappings.append((entry, jresp[entry][0]))
    print(mappings, len(mappings))
    return mappings


def readJsonFile(filename):
    if filename:
        print('Reading entries from', filename)

        descriptions = []
        names = []
        pdbs = []
        emdbs = []
        relatedPdbs = []
        relatedEmdbs = []
        compModels = []

        with open(filename) as jsonfile:
            data = json.load(jsonfile)

            proteome = data["SARS-CoV-2 Proteome"]
            # print(proteome.keys())
            protList = proteome.keys()

            for i in protList:
                if "description" in proteome[i]:
                    descriptions.append(i)

                if "names" in proteome[i]:
                    for n in proteome[i]["names"]:
                        names.append(n)

                if "PDB" in proteome[i]:
                    for n in proteome[i]["PDB"].keys():
                        pdbs.append(n)

                if "EMDB" in proteome[i]:
                    for n in proteome[i]["EMDB"].keys():
                        emdbs.append(n)

                if "Related" in proteome[i]:
                    if "SARS-CoV" in proteome[i]["Related"]:
                        if "PDB" in proteome[i]["Related"]["SARS-CoV"]:
                            for n in proteome[i]["Related"]["SARS-CoV"]["PDB"]:
                                relatedPdbs.append(n)
                        if "EMDB" in proteome[i]["Related"]["SARS-CoV"]:
                            for n in proteome[i]["Related"]["SARS-CoV"]["EMDB"]:
                                relatedEmdbs.append(n)

                    if "OtherRelated" in proteome[i]["Related"]:
                        if "PDB" in proteome[i]["Related"]["OtherRelated"]:
                            for n in proteome[i]["Related"]["OtherRelated"]["PDB"]:
                                relatedPdbs.append(n)
                        if "EMDB" in proteome[i]["Related"]["OtherRelated"]:
                            for n in proteome[i]["Related"]["OtherRelated"]["EMDB"]:
                                relatedEmdbs.append(n)

                if "CompModels" in proteome[i]:
                    if "swiss-model" in proteome[i]["CompModels"]:
                        for n in proteome[i]["CompModels"]["swiss-model"]:
                            compModels.append(n["project"]+"_"+n["model"])
                    if "BSM-Arc" in proteome[i]["CompModels"]:
                        for n in proteome[i]["CompModels"]["BSM-Arc"]:
                            compModels.append(n["model"])

                if "Interactions" in proteome[i]:
                    if "P-P-Interactions" in proteome[i]["Interactions"]:
                        if "PDB" in proteome[i]["Interactions"]["P-P-Interactions"]:
                            for n in proteome[i]["Interactions"]["P-P-Interactions"]["PDB"]:
                                pdbs.append(n)
                        if "EMDB" in proteome[i]["Interactions"]["P-P-Interactions"]:
                            for n in proteome[i]["Interactions"]["P-P-Interactions"]["EMDB"]:
                                emdbs.append(n)
                    if "Ligands" in proteome[i]["Interactions"]:
                        for k in proteome[i]["Interactions"]["Ligands"].keys():
                            for n in proteome[i]["Interactions"]["Ligands"][k]:
                                if "EMDB" == k:
                                    emdbs.append(n)
                                else:
                                    pdbs.append(n)

        # print("names", names, len(names))
        # print("descriptions", descriptions, len(descriptions))
        # print("relatedPdbs", relatedPdbs, len(relatedPdbs))
        # print("relatedEmdbs", relatedEmdbs, len(relatedEmdbs))
        # print("compModels", compModels, len(compModels))
        print("pdbs", pdbs, len(pdbs))
        # print("emdbs", emdbs, len(emdbs))

        # print("names",  len(names))
        # print("descriptions",  len(descriptions))
        # print("relatedPdbs",  len(relatedPdbs))
        # print("relatedEmdbs",  len(relatedEmdbs))
        # print("compModels",  len(compModels))
        # print("pdbs",  len(pdbs))
        # print("emdbs",  len(emdbs))

        return (names, descriptions, pdbs, emdbs, relatedPdbs, relatedEmdbs, compModels)


def getLigands(pdbId):
    # read PDB entry
    # get ligands
    pass


def addLigands2DB(pdbId):
    ligands = getLigands(pdbId)
    # add ligands to DB
    print(ligands)


def main(argv):
    inputfile = ''
    method = ''
    try:
        opts, args = getopt.getopt(argv, 'hi:', ['ifile=', ])
    except getopt.GetoptError:
        print('update_data_json.py -i <inputfile>')
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print('update_data_json.py -i <inputfile>')
            sys.exit()
        elif opt in ('-i', '--ifile'):
            inputfile = arg

    if not inputfile:
        print('update_data_json.py -i <inputfile>')
        sys.exit(2)

    names, descriptions, pdbs, emdbs, relatedPdbs, relatedEmdbs, compModels = readJsonFile(
        filename=inputfile)

    print("All Names")
    save2file(sorted(names), filename=os.path.join(PATH_DATA, FN_NAMES))
    print(names, len(names))

    print("All Descriptions")
    save2file(sorted(descriptions), filename=os.path.join(
        PATH_DATA, FN_DESCRIPTIONS))
    print(descriptions, len(descriptions))

    print("All PDB's")
    save2file(sorted(pdbs), filename=os.path.join(PATH_DATA, FN_PDB_ENTRIES))
    print(pdbs, len(pdbs))

    print("All EMDB's")
    save2file(sorted(emdbs), filename=os.path.join(PATH_DATA, FN_EMDB_ENTRIES))
    print(emdbs, len(emdbs))

    print("All Related PDB's")
    save2file(sorted(relatedPdbs), filename=os.path.join(
        PATH_DATA, FN_REL_PDB_ENTRIES))
    print(relatedPdbs, len(relatedPdbs))

    print("All Related EMDB's")
    save2file(sorted(relatedEmdbs), filename=os.path.join(
        PATH_DATA, FN_REL_EMDB_ENTRIES))
    print(relatedEmdbs, len(relatedEmdbs))

    print("All Cumputational Models")
    save2file(sorted(compModels), filename=os.path.join(
        PATH_DATA, FN_COMP_MODELS))
    print(compModels, len(compModels))

    print()
    print("Get mappings EMDB-PDB")
    emdb_mappings = getPdbMappings(emdbs, 'emdbs')
    save2csv(emdb_mappings, filename=os.path.join(
        PATH_DATA, FN_EMDB_PDB_MAPPINGS))
    print(emdb_mappings, len(emdb_mappings))

    print("Get mappings PDB-EMDB")
    pdb_mappings = getPdbMappings(pdbs, 'pdbs')
    save2csv(pdb_mappings, filename=os.path.join(
        PATH_DATA, FN_PDB_EMDB_MAPPINGS))
    print(pdb_mappings, len(pdb_mappings))

    print("Get mappings REL EMDB-PDB")
    rel_emdb_mappings = getPdbMappings(relatedEmdbs, 'emdbs')
    save2csv(rel_emdb_mappings, filename=os.path.join(
        PATH_DATA, FN_REL_EMDB_PDB_MAPPINGS))
    print(rel_emdb_mappings, len(rel_emdb_mappings))

    print("Get mappings REL PDB-EMDB")
    rel_pdb_mappings = getPdbMappings(relatedPdbs, 'pdbs')
    save2csv(rel_pdb_mappings, filename=os.path.join(
        PATH_DATA, FN_REL_PDB_EMDB_MAPPINGS))
    print(rel_pdb_mappings, len(rel_pdb_mappings))

    print("All mappings")
    allMappings = pdb_mappings + emdb_mappings + \
        rel_pdb_mappings + rel_emdb_mappings
    allMappingsNoDups = set(allMappings)
    save2csv(allMappingsNoDups, filename=os.path.join(
        PATH_DATA, FN_ALL_MAPPINGS))


if __name__ == '__main__':
    main(sys.argv[1:])
