import getopt
import sys
import os
import csv

DATA_PATH = 'data'
TOOLS_PATH = '/home/bioinfo/services/emv/tools'
METHODS = ['mapq', 'fscq', 'daq', 'deepres', 'monores', 'blocres', 'statslocalres', 'init']
METHOD_SCRIPTS = {'mapq': 'queue_script_mapq.sh',
                  'fscq': 'queue_script_fscq.sh',
                  'daq': 'queue_script_daq.sh',
                  'deepres': 'queue_script_deepRes.sh',
                  'monores': 'queue_script_monores.sh',
                  'blocres': 'queue_script_blocres.sh',
                  'statslocalres': 'queue_script_localres_stats.sh',
                  'init':'queue_script_init.sh',
                  }
METHOD_INITIALS = {'mapq': 'MQ', 'fscq': 'FQ', 'daq': 'DQ',
                   'deepres': 'DR', 'monores': 'MR', 'blocres': 'BR', 
                   'statslocalres': 'LR',
                   'init': 'IN'
                   }


def known_entry(mapId, path):
    bMatch = False
    for dirpath, dirnames, filenames in os.walk(path):
        for dName in dirnames:
            if mapId in dName:
                bMatch = True
                # print('--->>> FOUND', mapId, dName)
                break
    return bMatch


def read_entries_file(filename, method='init', new_only=False):
    """
    read Entries File
    """
    print('->>> Reading entries from', filename)
    with open(filename, encoding="utf-8") as csvfile:
        rdr = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in rdr:
            data = ', '.join(row)
            mapId = data.split()[0].replace('EMD-', '')
            pdbId = data.split()[1]
            # print('-->>> Got', mapId, pdbId)
            if new_only and known_entry(mapId, DATA_PATH):
                print('-->>> Skip already processed entry', mapId, pdbId)
                continue
            sendCalc2Queue2(mapId, pdbId, method)


def getQueueCmd(mapId, pdbId, method, scriptName):
    cmd = 'sbatch' + ' ' + '--job-name=' + METHOD_INITIALS[method] + '-' + mapId + \
        ' ' + os.path.join(TOOLS_PATH, scriptName) + \
        ' ' + mapId + ' ' + pdbId
    return cmd


def sendCalc2Queue2(mapId, pdbId, method):
    print('->>> Calculating EMV for', mapId, pdbId)
    script = METHOD_SCRIPTS[method]
    cmd = getQueueCmd(mapId, pdbId, method, script)
    print('->>> Sending command', cmd)
    result = os.system(cmd)
    if result > 0:
        print('->>> with result: %d' % result)


def main(argv):
    inputfile = ''
    method = ''
    newEntriesOnly = False
    scriptname = os.path.basename(sys.argv[0])
    try:
        opts, args = getopt.getopt(
            argv, 'hi:m:n', ['ifile=', 'method=', 'newOnly'])
    except getopt.GetoptError:
        print(scriptname, '-i <inputfile> -m <method>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(scriptname, '-i <inputfile> -m <method>')
            sys.exit()
        elif opt in ('-n', '--newOnly'):
            newEntriesOnly = True
        elif opt in ('-i', '--ifile'):
            inputfile = arg
        elif opt in ('-m', '--method'):
            method = arg
            if method not in METHODS:
                print('Supported methods:',  METHODS)
                sys.exit()

    if not method:
        method = 'init'
    if inputfile:
        read_entries_file(filename=inputfile, method=method,
                        new_only=newEntriesOnly)


if __name__ == '__main__':
    main(sys.argv[1:])
