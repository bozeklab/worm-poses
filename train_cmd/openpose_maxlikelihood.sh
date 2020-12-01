#!/bin/bash

#$ -P rittscher.prjc -q gpu8.q -pe shmem 1 -l gpu=1


#source activate pytorch-1.0

echo "Username: " `whoami`
echo $HOME
echo cuda_id: $CUDA_VISIBLE_DEVICES

SCRIPTPATH="start_worm-poses.py"
python -W ignore $SCRIPTPATH

echo "Finished at :"`date`
exit 0