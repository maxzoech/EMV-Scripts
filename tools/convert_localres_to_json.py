#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import numpy
import json
import os
import time


# Print usage in case no command line is given
if len(sys.argv) < 3:
    print('\n', 'Usage :',
          sys.argv[0], '[*.aa.pdb] [*.json] [DeepRes | MonoRes | BlocRes]')
    sys.exit(0)

input_file = sys.argv[1]
output_file = sys.argv[2]
print("- Reading", input_file)

resource = "EMV-"+sys.argv[3] + "-Scores"
print("- Converting", input_file)

emdb_entry = os.path.basename(output_file).split('_')[0].upper()
pdb_entry = os.path.basename(output_file).split('_')[1]
proc_date = time.strftime(
    '%Y-%m-%d', time.gmtime(os.path.getmtime(input_file)))

emv_data = {}
emv_data["resource"] = resource
entry_data = {
    "volume_map": emdb_entry,
    "atomic_model": pdb_entry,
    "date": proc_date}
emv_data["entry"] = entry_data
emv_data["chains"] = []


with open(input_file) as f:
    lines_data = f.readlines()

    current_chain = ""
    current_residue = 0
    # data_set = {}
    for lin in lines_data:
        if (lin.startswith('ATOM') or lin.startswith('HETATM')):

            # read fields
            residue_name = lin[17:20].strip()
            chain_id = lin[21:22].strip()
            residue_sequence_number = int(lin[22:26].strip())
            score_value = float(lin[54:60].strip())

            # get data
            if current_residue != residue_sequence_number:

                if current_residue:
                    # save current residue data
                    res_values.append(score_value)
                    mean_score = numpy.mean(res_values)
                    residue_data["scoreValue"] = ' {0:.4f}'.format(mean_score)
                    chain_data["seqData"].append(residue_data)

                # start new residue data set
                res_values = []
                residue_data = {
                    "resSeqName": residue_name,
                    "resSeqNumber": residue_sequence_number,
                }
                current_residue = residue_sequence_number
            else:
                res_values.append(score_value)

            # get chain
            if current_chain != chain_id or lin == lines_data[-1]:
                if current_chain:
                    # print(chain_id, residue_sequence_number, residue_name)
                    # save current chain
                    emv_data["chains"].append(chain_data)

                # start new chain data set
                chain_data = {}
                chain_data["name"] = chain_id
                chain_data["seqData"] = []
                current_chain = chain_id


print("-- Writing", output_file)
with open(output_file, "w+") as of:
    of.write(json.dumps(emv_data, indent=2))
