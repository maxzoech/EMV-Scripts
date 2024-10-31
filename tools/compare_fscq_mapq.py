#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import numpy
import json
from itertools import groupby
from datetime import datetime

# Print usage in case no command line is given
if len(sys.argv)<3:
    print('\nUsage : compare_fscq_mapq.py 7btf.mapq.aa.pdb 7btf.fscq.aa.pdb salida.txt')
    sys.exit(0)
    
import io
try:
    to_unicode = unicode
except NameError:
    to_unicode = str    

# Get the full pdb file and the parts of it we are going to analyse trough command line
mapqfile=sys.argv[1]
fscqfile=sys.argv[2]
outfile=sys.argv[3]
    
# Read the pdb file and save the residues we are interested at
print("Reading ", mapqfile, " to analyse:")

bool=0
count1=0
count2=0
count3=0
count4=0
count5=0
count6=0
count7=0
count8=0
count9=0

t1 = 0
t2 = 0
t3 = 0

group1 = []
group2 = []
group3 = []
group4 = []
group5 = []
group6 = []
group7 = []
group8 = []
group9 = []
group10 = []
group11 = []
group12 = []



out= open(outfile,"w+")
fscq= open(fscqfile, "r")
with open(mapqfile) as mapq:
    lines_mapq = mapq.readlines()
    lines_fscq = fscq.readlines()
    
    for lin, lin2 in zip(enumerate(lines_mapq), enumerate(lines_fscq)):
#         print (lin[1][0:6], '\n')
        if ( lin[1][0:6] == "ATOM  "  or lin[1][0:6] == "HETATM" ):
              
            resnumber = int(lin[1][22:26])
             
            if (bool==1 and resnumber == resnumber_ctl):
                resatomname = lin[1][12:16].strip()
                resname = lin[1][17:20].strip()
                chain = lin[1][21:22].strip()
                mapq = float(lin[1][54:60])
                fscq = float(lin2[1][54:60])
                 
            elif (bool==1 and resnumber != resnumber_ctl):
 
                resnumber_ctl = resnumber
                resatomname = lin[1][12:16].strip()
                resname = lin[1][17:20].strip() 
                chain = lin[1][21:22].strip()
                mapq = float(lin[1][54:60])
                fscq = float(lin2[1][54:60])
                
                if (mapq > 0.45 and fscq <=-1.0):
                    count1=count1+1
                    group1.append((resnumber, chain))
                elif (mapq > 0.45 and fscq > -1.0 and fscq < 1.5):
                    count2=count2+1
                    group2.append((resnumber, chain))
                elif (mapq > 0.45 and fscq >= 1.5):
                    count3=count3+1
                    group3.append((resnumber, chain))
                elif (mapq < 0.25 and mapq >= 0 and fscq <= -1.0):
                    count4=count4+1
                    group4.append((resnumber, chain))
                elif (mapq < 0.25 and mapq >= 0 and fscq > -1.0 and fscq < 1.5):
                    count5=count5+1
                    group5.append((resnumber, chain))
                elif (mapq < 0.25 and mapq >= 0 and fscq >= 1.5):
                    count6=count6+1  
                    group6.append((resnumber, chain))
                elif (mapq < 0 and fscq <=-1.0):
                    count7=count7+1 
                    group7.append((resnumber, chain)) 
                elif (mapq < 0  and fscq > -1.0 and fscq < 1.5):
                    count8=count8+1 
                    group8.append((resnumber, chain)) 
                elif (mapq < 0 and fscq >= 1.5):
                    count9=count9+1  
                    group9.append((resnumber, chain))
                
                #transition part
                elif (mapq >= 0.25 and mapq <= 0.45 and fscq <= -1):   
                    t1=t1+1 
                elif (mapq >= 0.25 and mapq <= 0.45 and fscq > -1.0 and fscq < 1.5):   
                    t2=t2+1 
                elif (mapq >= 0.25 and mapq <= 0.45 and fscq >= 1.5):   
                    t3=t3+1 
                                      
 
#                 print("escribo aqui ", resnumber, resname, chain, mapq, fscq)
                 
            else:
                bool=1
                resnumber_ctl = resnumber
                resatomname = lin[1][12:16].strip()
                resname = lin[1][17:20].strip()
                chain = lin[1][21:22].strip()
                mapq = float(lin[1][54:60])
                fscq = float(lin2[1][54:60])
                
                if (mapq > 0.45 and fscq <=-1.0):
                    count1=count1+1
                    group1.append((resnumber, chain))
                elif (mapq > 0.45 and fscq > -1.0 and fscq < 1.5):
                    count2=count2+1
                    group2.append((resnumber, chain))
                elif (mapq > 0.45 and fscq >= 1.5):
                    count3=count3+1
                    group3.append((resnumber, chain))
                elif (mapq <= 0.25 and mapq >= 0 and fscq <= -1.0):
                    count4=count4+1
                    group4.append((resnumber, chain))
                elif (mapq <= 0.25 and mapq >= 0 and fscq > -1.0 and fscq < 1.5):
                    count5=count5+1
                    group5.append((resnumber, chain))
                elif (mapq <= 0.25 and mapq >= 0 and fscq >= 1.5):
                    count6=count6+1 
                    group6.append((resnumber, chain)) 
                elif (mapq < 0 and fscq <=-1.0):
                    count7=count7+1 
                    group7.append((resnumber, chain)) 
                elif (mapq < 0  and fscq > -1.0 and fscq < 1.5):
                    count8=count8+1 
                    group8.append((resnumber, chain)) 
                elif (mapq < 0 and fscq >= 1.5):
                    count9=count9+1  
                    group9.append((resnumber, chain))
                    
                #transition part
                elif (mapq >= 0.25 and mapq <= 0.45 and fscq <= -1):   
                    t1=t1+1 
                elif (mapq >= 0.25 and mapq <= 0.45 and fscq > -1.0 and fscq < 1.5):   
                    t2=t2+1 
                elif (mapq >= 0.25 and mapq <= 0.45 and fscq >= 1.5):   
                    t3=t3+1 
                 
#                 print("escribo aqui ", resnumber, resname, chain, mapq, fscq)
                
print("cuadrante_1", count1)
print(group1)

print("cuadrante_2", count2)

print("cuadrante_3", count3)
print(group3)

print("cuadrante_4", count4)
for i,j in group4:
    print("%d.%s" %(i,j), end=", ")
    
print("\n cuadrante_5", count5)
print(group5)

print("cuadrante_6", count6)
for i,j in group6:
    print("%d.%s" %(i,j), end=", ")
print("\n", group6)

print("\n cuadrante_7", count7)
for i,j in group7:
    print("%d.%s" %(i,j), end=", ")
print("\n", group7)    

print("cuadrante_8", count8)
print(group8)

print("cuadrante_9", count9)
for i,j in group9:
    print("%d.%s" %(i,j), end=", ")
print("\n", group9)  

print("transition_1", t1)
print("transition_2", t2)
print("transition_3", t3)

date = datetime.now().date()
model = mapqfile.split('.')[0]
print (model)

data = {
    "emv_summary":{"method_type":"modelQuality",
                   "atomic_model" : model},
    
    "data" : {"cat_id" : 1,
              "cat_name" : "overfitting"}
    }

# Write JSON file
with io.open('data.json', 'w', encoding='utf8') as outfile:
    str_ = json.dumps(data,
                      indent=4, sort_keys=True,
                      separators=(',', ': '), ensure_ascii=False)
    outfile.write(to_unicode(str_))
                
            







