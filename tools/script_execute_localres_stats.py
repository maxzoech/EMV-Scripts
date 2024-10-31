"""
generate the local resolution statistics
"""
import os
import argparse
import csv
import glob
import json
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import mrcfile
from script_emv_setup import SOFTWARE_VERSION, WORK_PATH, STATS_PATH, get_parameters

matplotlib.use("Agg")

JSON_FILE_SUFIX = "_emv_localresolution_stats.json"
CSV_FILE_NAME = "emv_localResolution_stats.csv"
CSV_FILE_NAME2 = "emv_localResolution_consensus.csv"
RESOURCE_NAME = "EMV-statitics"
METHOD_TYPE = "Local Resolution Consensus"
UNITS_NAME = "Angstrom"
# This threshold represent the cutoff to consider whether we have to report a warning
THRESHOLD = 2

methods = [
    {"name": "MonoRes", "fileregex": "/*monores.atom*.pdb"},
    {"name": "DeepRes", "fileregex": "/*deepres.atom*.pdb"},
    {"name": "BlocRes", "fileregex": "/*blocres.atom*.pdb"},
]


def local_resolution_histrograms(emdb_id, baseFolder, sampling):
    """
    This function generate the local resolution histograms as a .png file. The methods to be considered
    are MonoRes, DeepRes, and BlocRes. For each method a distribution of resolution is computed and therefore
    a histogram (.png) is obtained, as well as a median of local resolution and an interquartile range q25, q75.
    These values are obtained per method, i.e. due to there are 3 methods we will get 3 medians, 3 25-quartiles and
    3 75-quartiles. The output of the function will summarize these 9 values as only 3, the median of medians, and
    the maximum interquartile range q25, q75
    :param emdbId: EMDB id of the volume map
    :param baseFolder: Folder where the pdbs with the information with local resolution are
    :param sampling: Sampling rate of the maps
    :return: res, q25, q75, warnings and errors. res is the median of the medians of local resolution and q25 and q75
    are greatest interquartile range it means q25 = min(q25_1, q25_2, q25_3), q75 = max(q75_1, q75_2, q75_3),
    """
    quartile25 = []
    quartile75 = []
    median_resolution = []
    warnings = []
    errors = []

    for method in methods:
        median = None
        q_25 = None
        q_75 = None
        failed = False
        try:
            fnames = glob.glob(baseFolder + method["fileregex"])
            for fname in fnames:
                median, q_25, q_75, failed = tryHistogram(
                    sampling, fname, baseFolder, emdb_id + "_emv_" + method["name"]
                )
                if not failed:
                    median_resolution.append(median)
                    quartile25.append(q_25)
                    quartile75.append(q_75)
                else:
                    errors.append(
                        "processing: Couldn't generate histogram for %s data"
                        % method["name"]
                    )
                    print(errors)
                break  # there should be only one file per method, but just in case
        except Exception as ex:
            print(ex)
        if not median or not q_25 or not q_75:
            warnings.append("processing: No data found for %s" % method["name"])

    if (np.max(median_resolution) - np.min(median_resolution)) > THRESHOLD:
        warnings.append(
            "processing: Difference between maximum and minimum is greater than Threshold:"
            + str(THRESHOLD)
        )

    if not median_resolution or not quartile25 or not quartile75:
        errors.append("processing: No data found")
        return -1, -1, -1, warnings, errors
    return (
        np.median(median_resolution),
        np.min(quartile25),
        np.max(quartile75),
        warnings,
        errors,
    )


def interquart(values, q1, q2):
    """
    This function estimates the interquartile range q1-q2 given a set of values
    :param values: Input values to determine the interquartile range
    :param q1: quartile q1
    :param q2: quartile q2
    :return: [quartile_q1(values), quartile_q2(values)]
    """
    aux = np.sort(values)
    l = len(aux)
    stdvals_mr = [aux[round(q1 * l) - 1], aux[round(q2 * l) - 1]]
    return stdvals_mr


def readpdbfile(fn, sampling):
    """
    This function reads the pdb with the local resolution values stored in it (column 56:61)
    and return it as a vector
    :param fn: folder where the data is located
    :param sampling: sampling rate of the data
    :return: Array with the data of the pdb
    """
    lines = [x.rstrip("\n") for x in open(fn, "r")]
    dataList = []
    for l in lines:
        if l.startswith("ATOM"):
            dataList.append(float(l[56:61]))

    nyquist = 2 * sampling
    dataList = np.array(dataList)
    dataList = dataList[dataList >= nyquist]
    return dataList


def tryHistogram(sampling, fn, path, title):
    """
    This function takes the folder where the data of local resolution are stored as pdb and represent the
    local resolution histogram if it is possible
    :param sampling: sampling rate of the dataset
    :param fn: folder where data are located (pdb)
    :param path: path where the histogram will be stored
    :param title: title of the histogram and of the output filename
    :return: res, q25, q75, itFailed (res - median of local resolution), (q25 - quartile25), (q75 - quartile75),
    (itFailed - boolean that express if the method failed or not)
    """
    dataList = []
    median_data = []
    quartile_25 = []
    quartile_75 = []
    itFailed = False

    try:
        dataList = readpdbfile(fn, sampling)
        plt.figure()
        plt.hist(dataList)
        # headfn, tailfn = path.split(method)
        plt.title(title)
        fnOut = os.path.join(path, title.lower() + ".png")
        # print(fnOut)
        plt.savefig(fnOut)

        median_data = np.median(dataList)
        sortedData = np.sort(dataList)
        quartile_25 = sortedData[round(0.25 * len(sortedData))]
        quartile_75 = sortedData[round(0.75 * len(sortedData))]
        # plt.legend('m-' + str(float(median_data)) + '   IQ-' + str(quartile_25) + '-' + str(quartile_75))
    except:
        ME = title + "not found"
        itFailed = True

    return median_data, quartile_25, quartile_75, itFailed


def checkHalfMaps(fnHalf1, fnHalf2):
    hasError = False
    with mrcfile.open(fnHalf1) as mrc:
        half1 = mrc.data
    with mrcfile.open(fnHalf2) as mrc:
        half2 = mrc.data
    diff_h1h2 = np.mean(half1 - half2)
    if abs(diff_h1h2) < 1e-38:
        hasError = True
    return hasError


def saveEntryJSONStats(
    filename, emdbId, sampling, res, q25, q75, warnings={}, errors={}
):
    """
    Save the results of the analysis in a json file
    """
    executionDate = time.strftime("%Y-%m-%d")
    jStats = {
        "resource": RESOURCE_NAME,
        "method_type": METHOD_TYPE,
        "software_version": SOFTWARE_VERSION,
    }
    jEntry = {"date": executionDate, "volume_map": emdbId}
    jStats["entry"] = jEntry
    jData = {
        "sampling": sampling,
        "threshold": THRESHOLD,
        "unit": UNITS_NAME,
        "metrics": [
            {"resolutionMedian": res},
            {"quartile25": q25},
            {"quartile75": q75},
        ],
    }
    jStats["data"] = jData
    jStats["warnings"] = warnings
    jStats["errors"] = errors

    with open(filename, "w") as outfile:
        json.dump(jStats, outfile, indent=4)


def updateGlobalCSVStats(filename, emdbId, res, q25, q75):
    """
    Update the global csv file with the new data
    """
    newrow = [emdbId, str(res), str(q25), str(q75)]
    with open(filename, "a") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(newrow)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute Local Resolution Statistics")
    parser.add_argument(
        "-i",
        "--map",
        help="input map EMDB ID (just the numeric part, without EMD-)",
        required=True,
    )
    parser.add_argument(
        "-d", "--workdir", help="path to working directory", required=False
    )
    args = parser.parse_args()

    emdbIdNumber = args.map
    emdbId = "emd-" + emdbIdNumber
    path = args.workdir or WORK_PATH
    workPath = os.path.join(path, emdbId)
    resolution, sampling, size, org_x, org_y, org_z = get_parameters(
        emdbIdNumber, workPath
    )

    print("-> Compute local resolution statistics for map %s" % emdbIdNumber)
    res, q25, q75, warnings, errors = local_resolution_histrograms(
        emdbId, workPath, sampling
    )
    print(res, q25, q75, warnings, errors)

    jsonFile = os.path.join(workPath, emdbId + JSON_FILE_SUFIX)
    print("-> Save resolution statistics (JSON) %s:" % jsonFile)
    saveEntryJSONStats(jsonFile, emdbId, sampling, res, q25, q75, warnings, errors)

    # emv_localResolution_stats.csv
    csvFile = os.path.join(WORK_PATH, STATS_PATH, CSV_FILE_NAME)
    print("-> Save global statistics (CSV) %s" % csvFile)
    updateGlobalCSVStats(csvFile, emdbId, res, q25, q75)
    # emv_localResolution_cons.csv
    csvFile = os.path.join(WORK_PATH, STATS_PATH, CSV_FILE_NAME2)
    print("-> Save global statistics (CSV) %s" % csvFile)
    updateGlobalCSVStats(csvFile, emdbId, res, q25, q75)
