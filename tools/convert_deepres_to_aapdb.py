#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import numpy
from itertools import groupby

# Print usage in case no command line is given
if len(sys.argv)<2:
    print('\nUsage : analyse_localres_pdb.py input_pdb-local-resolu.pdb output_file')
    sys.exit(0)

# Get the full pdb file and the parts of it we are going to analyse trough command line
pdbfile=sys.argv[1]
outfile=sys.argv[2]
    
# Read the pdb file and save the residues we are interested at
print("Reading ", pdbfile, " to analyse:")

bool=0
out= open(outfile,"w+")
with open(pdbfile) as f:
		
	lines_data = f.readlines()
	for j,lin in enumerate(lines_data):

		if ( lin.startswith('ATOM') or lin.startswith('HETATM') ):
			resnumber = int(lin[22:26])

			if (bool==1 and resnumber == resnumber_ctl):
#				print('\n resnumber= ',resnumber)
#				print('\n resnumber_ctl= ',resnumber_ctl)
				resatomname = lin[12:16].strip()
				resname = lin[17:20].strip()
				localres = float(lin[54:60])
				current_frag.append((resname,resnumber,resatomname,localres))
				lines_aa.append(lin)
#				print('\n SHERLOCK current_frag',current_frag)

			elif (bool==1 and resnumber != resnumber_ctl):
				list_amino = [ele[3] for ele in current_frag if ele[3]>0.2]
				print('\n AMINO list_amino',list_amino)

				if len(list_amino) > 0:
					mean = numpy.mean(list_amino)
				else:
					mean=0.00
#				print('\n LR mean',mean)

				for ele in lines_aa:
					modif = ele.replace(ele[55:60], ' {0:.2f}'.format(mean))
					print(modif)
					out.write(modif)

				current_frag = []
				lines_aa = []
				resnumber_ctl = resnumber
				resatomname = lin[12:16].strip()
				resname = lin[17:20].strip() 
				localres = float(lin[54:60])

				current_frag.append((resname,resnumber,resatomname,localres))
				lines_aa.append(lin)			

			else:
				bool=1
				current_frag = []
				lines_aa = []
				resnumber_ctl = resnumber
				resatomname = lin[12:16].strip()
				resname = lin[17:20].strip() 
				localres = float(lin[54:60])

				current_frag.append((resname,resnumber,resatomname,localres))
				lines_aa.append(lin)

     #print ('\nSHERLOCK ',resname,resnumber,resatomname,localres)

  #print('\n SHERLOCK current_frag',current_frag)
  #print('\n SHERLOCK len(current_frag)',len(current_frag))





