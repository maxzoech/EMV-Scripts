
#/bin/bash

SCRIPT_PATH="$HOME/services/emv/update/calcUpdates.py"
DATA_PATH="$HOME/services/emv/update/data"

echo "Computing EMV for $1"

echo "- Send all jobs to the queue"
python $SCRIPT_PATH -i $DATA_PATH/$1 -m all

### echo "- Send MapQ jobs to the queue"
### python $SCRIPT_PATH -i $DATA_PATH/$1 -m mapq

### echo "- Send DeepRes jobs to the queue"
### python $SCRIPT_PATH -i $DATA_PATH/$1 -m deepres

### echo "- Send FscQ jobs to the queue"
### python $SCRIPT_PATH -i $DATA_PATH/$1 -m fscq -n

### echo "- Send BlocRes jobs to the queue"
### python $SCRIPT_PATH -i $DATA_PATH/$1 -m blocres -n

### echo "- Send MonoRes jobs to the queue"
### python $SCRIPT_PATH -i $DATA_PATH/$1 -m monores -n
