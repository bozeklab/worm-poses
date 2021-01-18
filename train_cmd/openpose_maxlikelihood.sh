#!/bin/bash

echo "Username: " `whoami`
echo $HOME
echo cuda_id: $CUDA_VISIBLE_DEVICES

#SCRIPTPATH="start_worm-poses.py"
SCRIPTPATH="../scripts/train_PAF.py"
python -W ignore $SCRIPTPATH

echo "Finished at :"`date`
exit 0