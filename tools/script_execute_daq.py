#
# Excute daQ automatically
#

import os
import os.path
import argparse
from script_emv_setup import *


def execute_daq(map, pdb, workpath):
    # compute daQ
    os.chdir(TOOLS_PATH + 'software/DAQ/')
    os_command = 'python3 '
    os_command += ' daq.py '
    os_command += ' --mode=0 --gpu $CUDA_VISIBLE_DEVICES --batch_size 12288'
    os_command += ' -F %s/%s' % (workpath, map)
    os_command += ' -P %s/%s' % (workpath, pdb)
    print('--> Compute daQ', os_command)
    os.system(os_command)
    
    
def convert_daq_to_aapdb(daq, aa_pdb, workpath):
    # Save to aa.PDB file
    os_command = ' python3 ' + TOOLS_PATH + 'convert_daQvol_to_pdb.py'
    os_command += ' %s' % (daq)
    os_command += ' %s/%s' % (workpath, aa_pdb)
    print('--> Save to aa.PDB file', os_command)
    os.system(os_command)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Compute DAQ")
    parser.add_argument("-i", "--map", help="input map EMDB ID (just the numeric part, without EMD-)", required=True)
    parser.add_argument("-p", "--pdb", help="input atomic model PDB ID", required=True)
    parser.add_argument("-d", "--workdir", help="path to working directory", required=False)
    args = parser.parse_args()

    mapId = args.map
    pdbId = args.pdb
    path = args.workdir or WORK_PATH

    # Create (if not exists) working directory
    workpath = create_work_dir(path, mapId)
    print(f'-> Working dir', workpath)

    # Download EMDB map file
    inMap = download_emdb_map(mapId, workpath)
    # Can not continue without inMap file
    if not inMap:
        raise ValueError('Can not continue. No volume MAP found')
    print(f'-> Input volume MAP', workpath, inMap)

    # Download PDB model file
    inPdb = download_pdb_model(pdbId, workpath)
    # Can not continue without inPdb file
    if not inPdb:
        raise ValueError('Can not continue. No atom MODEL found')
    print(f'-> Input atom model', workpath, inPdb)

    # Delete Hidrogens
    inPdb_nH = delete_hidrogens(inPdb, pdbId, workpath)
    print(f'-> Atom model, H atoms deleted', inPdb_nH)
    inPdb = inPdb_nH

    # . . . . . . . . . . . . . . . . . . . . . . . . .

    print("-> Compute daQ")
    execute_daq(inMap, inPdb, workpath)
    
    # . . . . . . . . . . . . . . . . . . . . . . . . .

    print("-> Save to aa.PDB")
    daq = TOOLS_PATH + 'software/DAQ/Predict_Result/emd_' + mapId +'.map/daq_score_w9.pdb'  
    print(daq)
    aa_pdb = pdbId + '.daq.aa.pdb'
    convert_daq_to_aapdb(daq, aa_pdb, workpath)

    print("-> Save to JSON")
    convert_to_json(mapId, pdbId, workpath, cmd='convert_daQvol_to_json.py', method='daQ')

 