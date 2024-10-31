"""
Setup for EM Validation methods
"""
import json
import os
import os.path
import ftplib
import shutil
import gzip
import re
from io import BytesIO
import requests


EMDB_EBI_REPOSITORY = "https://ftp.ebi.ac.uk/pub/databases/emdb/structures/"
EMDB_WWPDB_REPOSITORY = "https://ftp.wwpdb.org/pub/emdb/structures/"
EMDB_RCSB_REPOSITORY = "https://ftp.rcsb.org/pub/emdb/structures/"
EMDB_EBI_JSON_REPOSITORY = "https://www.ebi.ac.uk/emdb/api/entry/"
EMDB_FTP_SERVER = "ftp.ebi.ac.uk"
EMDB_FTP_DIR = "pub/databases/emdb/structures/%s/other"
PDB_EBI_REPOSITORY = "https://www.ebi.ac.uk/pdbe/entry-files/download/"
PDB_RCSB_REPOSITORY = "https://files.rcsb.org/download/"
TOOLS_PATH = "/home/bioinfo/services/emv/tools/"
LOGS_PATH = "/home/bioinfo/services/emv/logs"
WORK_PATH = "/home/bioinfo/services/emv/data/emdbs"
STATS_PATH = "statistics"
FN_LOCAL_JSON_PARAMS = "params.json"
SOFTWARE_VERSION = "0.7.2"


def delete_file(filename, file_path):
    """
    Delete file
    """
    try:
        print("INFO:", "Deleting file", filename)
        os.remove(os.path.join(file_path, filename))
    except FileNotFoundError as ex:
        print("INFO:", ex.strerror, ex.filename)
        print("INFO:", "Seems", filename, "wasn't there to be deleted. Never mind!")


def create_work_dir(path, map_id):
    """
    Create (if not exists) a working directory
    """
    name = "emd-" + map_id
    dir_path = os.path.join(path, name)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print("INFO:", "Directory ", dir_path, "Created")
    else:
        print("WARNING:", "Directory", dir_path, "already exists")

    return dir_path


def ungzip_file(srcfile, destfile, remove=True):
    """
    Uncompress a gz file
    by default (remove=True) the gzipped file will be
    removed after
    """
    print("INFO:", "Unzipping", srcfile, "->", destfile)
    if srcfile.endswith(".gz"):
        with open(destfile, "wb") as fout, gzip.GzipFile(srcfile) as fgzip:
            shutil.copyfileobj(fgzip, fout)
    if remove and os.path.exists(srcfile):
        os.remove(srcfile)
        print("INFO:", "Removing gz file.", srcfile)
    return destfile


def download_file(url, dirpath, filename, raw=False):
    """
    Download a file

    If raw=True, use Response.raw and shutil.copyfileobj()
    with binary files in order to stream to disk directly
    from the raw socket response from the server
    without using excessive memory
    """
    fullfname = os.path.join(dirpath, filename)
    if not os.path.exists(fullfname):
        print("INFO:", "Downloading", url, fullfname)
        try:
            with requests.get(url, stream=True, timeout=120) as req:
                if req.status_code == 404:
                    print("ERROR:", "Could not download file.", req.status_code)
                    return None
                if raw:
                    with open(fullfname, "wb") as fd:
                        shutil.copyfileobj(req.raw, fd, length=8192)
                else:
                    with open(fullfname, "w", encoding="utf-8") as fd:
                        fd.write(req.text)

        except requests.exceptions.RequestException as e:
            print("ERROR:", "Could not download file.", e)
            raise SystemExit(e) from e

    else:
        print("WARNING:", "File", fullfname, "already exists.")
    return filename


def download_emdb_map(map_id, workdir):
    """
    Download map file from EMDB
    """
    filename = "emd_" + map_id + ".map"
    gzfilename = "emd_" + map_id + ".map" + ".gz"
    destfile = os.path.join(workdir, filename)
    if not os.path.exists(destfile) or os.stat(destfile).st_size == 0:
        # download gziped map file
        # url = EMDB_WWPDB_REPOSITORY + 'EMD-' + map_id + '/map/' + gzfilename
        url = EMDB_EBI_REPOSITORY + "EMD-" + map_id + "/map/" + gzfilename
        # url = EMDB_RCSB_REPOSITORY + 'EMD-' + map_id + '/map/' + gzfilename
        print("INFO:", "Getting", gzfilename)
        srcfile = download_file(url, workdir, gzfilename, raw=True)
        # uncompress gziped map file
        print("INFO:", "Getting", destfile)
        if srcfile.endswith(".gz"):
            filename = ungzip_file(os.path.join(workdir, srcfile), destfile)
    else:
        print("WARNING:", "File", filename, "already exists")
    assert filename
    return filename


def download_pdb_model(pdb_id, workdir, force=False):
    """
    Download model file from PDB
    """
    filename = "pdb" + pdb_id + ".ent"
    destfile = os.path.join(workdir, filename)
    if force or not os.path.exists(destfile) or os.stat(destfile).st_size == 0:
        # download PDB model file
        # download from RCSB
        # https://files.rcsb.org/download/7BB7.pdb
        # url = PDB_RCSB_REPOSITORY + pdb_id + ".pdb"
        # download from PDBe EBI
        # https://www.ebi.ac.uk/pdbe/entry-files/download/pdb9bp9.ent
        url = PDB_EBI_REPOSITORY + "pdb" + pdb_id + ".ent"
        print("INFO:", "Getting", filename, url)
        filename = download_file(url, workdir, filename)
    else:
        print("WARNING:", "File", filename, "already exists")
    assert filename
    return filename


def delete_hidrogens(in_pdb_filename, pdb_id, workdir):
    """
    Remove Hydrogen atoms from PDB model file
    """
    filename = "pdb" + pdb_id + "_nH.ent"
    if not os.path.exists(os.path.join(workdir, filename)):
        print(
            "INFO:",
            "Removing H atoms from model file",
            workdir,
            in_pdb_filename,
            "to",
            filename,
        )
        cmd = ' grep -vrh "       H" '  # select only lines with no H atom
        cmd += f"{workdir}/{in_pdb_filename}"
        cmd += f" >> {workdir}/{filename}"
        print("delete_hidrogens CMD", cmd)
        os.system(cmd)
    else:
        print("WARNING:", "File", filename, "already exists")
    return filename


def get_emdb_metadata(map_id, work_dir):
    """
    Get required parameters from EMDB JSON file
    """
    entry = "EMD-" + map_id
    json_map_file = f"EMD-{map_id}.json"
    params = {}

    # check parameters json
    url = EMDB_EBI_JSON_REPOSITORY + entry
    print(f"INFO: Getting required parameters from {url}")
    filename = download_file(url, work_dir, json_map_file)
    with open(os.path.join(work_dir, filename), encoding="utf-8") as json_file:
        data = json.load(json_file)
        params["resolution"] = float(
            data["structure_determination_list"]["structure_determination"][0][
                "image_processing"
            ][0]["final_reconstruction"]["resolution"]["valueOf_"]
        )
        params["sampling"] = float(data["map"]["pixel_spacing"]["y"]["valueOf_"])
        params["size"] = int(data["map"]["dimensions"]["col"])
        params["org_x"] = -(float(data["map"]["origin"]["col"]))
        params["org_y"] = -(float(data["map"]["origin"]["sec"]))
        params["org_z"] = -(float(data["map"]["origin"]["row"]))
    return params


def get_parameters(map_id, workdir):
    """
    Read required parameters from local JSON file
    or from a JSON file from EMDB repo if nor available
    """
    filename = os.path.join(workdir, FN_LOCAL_JSON_PARAMS)
    params = {}
    if not os.path.exists(filename):
        # download from EMDB repo
        params = get_emdb_metadata(map_id, workdir)
        if params:
            # save params to local JSON file
            print(
                "INFO:",
                "Saving params to local JSON file",
                workdir,
                FN_LOCAL_JSON_PARAMS,
            )
            with open(
                os.path.join(workdir, FN_LOCAL_JSON_PARAMS), "w", encoding="utf-8"
            ) as outfile:
                json.dump(params, outfile)
    else:
        print(
            "INFO:",
            "Reading required parameters from local JSON file",
            workdir,
            FN_LOCAL_JSON_PARAMS,
        )
        with open(filename, encoding="utf-8") as infile:
            params = json.load(infile)
    return (
        params["resolution"],
        params["sampling"],
        params["size"],
        params["org_x"],
        params["org_y"],
        params["org_z"],
    )


def download_emdb_halfmaps(emdb_id, path):
    """
    Download half-maps files from EMDB
    """
    outname = os.path.join(path, emdb_id)
    # emd_33222_half_map_1.map.gz
    # EMD-33222_half_1.mrc
    # half1 = emdb_id + "_half_1.mrc"
    # half2 = emdb_id + "_half_2.mrc"
    # halfmap1file = os.path.join(path, half1)
    # halfmap2file = os.path.join(path, half2)

    if not os.path.exists(os.path.join(path, emdb_id + "_half_1.mrc")):
        try:
            ftp = ftplib.FTP(EMDB_FTP_SERVER)
            ftp.login()
            ftp.cwd(EMDB_FTP_DIR % emdb_id)
            fnames = ftp.nlst()
            half_names_in_server = [None, None]

            for fname in fnames:
                match_objs = re.match(".*half[-_\\.]*(map_?)*([12])", fname)
                if match_objs:
                    half_names_in_server[int(match_objs.group(2)) - 1] = fname

            if None in half_names_in_server:
                raise ValueError("Error, half map not available")

            print("--> Downloading", half_names_in_server)
            tmp_halfs = []
            for num_halfs in range(1, 3):
                try:
                    tmp_half_name = f"{outname}_half_{num_halfs}.mrc"
                    tmp_halfs.append(tmp_half_name)

                    with BytesIO() as flo:
                        ftp.retrbinary(
                            "RETR " + half_names_in_server[num_halfs - 1], flo.write
                        )
                        flo.seek(0)

                        with open(tmp_half_name, "wb") as fout, gzip.GzipFile(
                            fileobj=flo
                        ) as fgzip:
                            shutil.copyfileobj(fgzip, fout)

                except ftplib.all_errors as e:
                    print(e)
                    delete_file(tmp_half_name, path)
                    msg = f"Error downloading half-maps for emdb_id: {emdb_id} to: {outname}"
                    raise ValueError(msg) from e

        except ftplib.all_errors as e:
            print(e)
            msg = f"Error downloading half-maps for emdb_id: {emdb_id} to: outname"
            raise ValueError(msg) from e
    else:
        print(
            "WARNING:",
            "File",
            os.path.join(path, emdb_id + "_half_1.mrc"),
            "already exists",
        )
    return outname


def download_emdb_half_maps(map_id, work_dir):
    """
    download_emdb_half_maps if available
    """
    hmap1 = ""
    hmap2 = ""
    json_map_file = f"EMD-{map_id}.json"

    with open(os.path.join(work_dir, json_map_file), encoding="utf-8") as json_file:
        data = json.load(json_file)
        hmaps = data["interpretation"]["half_map_list"]["half_map"]
        hmap1 = hmaps[0]["file"]
        hmap2 = hmaps[1]["file"]

    return hmap1, hmap2


def convert_to_aapdb(pdb_id, path, cmd, method):
    """
    convert to aa-PDB
    """
    os_command = f"python3 {TOOLS_PATH}{cmd} \
        {path}/{pdb_id}.{method.lower()}.atom.pdb \
        {path}/{pdb_id}.{method.lower()}.aa.pdb"

    print("--> Save to aa.PDB file", os_command)
    os.system(os_command)


def convert_to_json(map_id, pdb_id, path, cmd, method):
    """
    convert aa.pdb to JSON
    """
    os_command = f"python3 {TOOLS_PATH}{cmd} \
        {path}/{pdb_id}.{method.lower()}.aa.pdb \
        {path}/emd-{map_id}_{pdb_id}_emv_{method.lower()}.json {method}"

    print("--> Convert aa.pdb to JSON", os_command)
    os.system(os_command)
