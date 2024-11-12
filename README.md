EMV-Scripts

Version 0.3.0

This GIT repo gather all scripts that run in finlay.cnb.csic.es under user bioinfo
to automatically validate new entries from EMDB+PDB.

Currently there are 6 methods implemented:
- MAPQ
- FSCQ
- DAQ
- DEEPRES
- MONORES
- LOCALRES

Every week, a new entries list from EMDB+PDB is collected and a set of jobs are 
launched through SLURM to run the corresponding scripts.

A set of commands are run throgh crontab at different times, according to:
- crontab.txt

Some of these commnands also take care of cleaning intermediate results and big files that might clutter the HD.

Every week, after all the corresponding computations have finished, basic statistics are collected
that indicate how well a particular entry is performing in relation with the rest of the database.

Results are stored under /home/bioinfo/services/emv/data/emdbs/emd-*****
The JSON files emd-<EMDB_ID>_<PDB_ID>_emv_<method>.json files are automatically and regularl retrieved from Campins (also from Rinchen-dos for dev/testing purposes). This allow to populate the corresponding WebServices (BWS) that will allow to show the _Validation and Quality_ tracks in 3DBionotes.

