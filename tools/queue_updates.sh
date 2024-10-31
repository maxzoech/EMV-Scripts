#/bin/bash

SCRIPT_PATH="$HOME/services/emv/tools/calcUpdates.py"
UPDATE_DATA_PATH="$HOME/services/emv/update/data"
PYTHON3_PATH="/usr/bin/python3"
METHODS=("mapq" "fscq" "daq" "blocres" "monores" "deepres" "statslocalres" "init")
USAGE_MSG="Usage: queue_updates.sh <input_file> <method1> <method2> <method3> ... [${METHODS[@]}]" 

if [[ $1 == "" ]]; then
    echo "Error1: no input file specified."
    echo $USAGE_MSG
    exit 1
elif [[ $2 == "" ]]; then
    echo "Error2: no method specified."
    echo $USAGE_MSG
    exit 2
fi

inputFile=$1
echo "- Read entries from $UPDATE_DATA_PATH/$inputFile"
shift
for method in "$@"; do
    if [[ " ${METHODS[*]} " =~ " $method " ]]; then
        echo "- Send $method jobs to the queue"
        $PYTHON3_PATH $SCRIPT_PATH -i $UPDATE_DATA_PATH/$inputFile -m $method
    else
        echo "unrecognised method $method"
    fi
    echo
done
