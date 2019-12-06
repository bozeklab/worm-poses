#!/bin/bash

#$ -P rittscher.prjc -q gpu8.q -pe shmem 1 -l gpu=1

source activate pytorch-1.0

echo "Username: " `whoami`
echo $HOME
echo cuda_id: $CUDA_VISIBLE_DEVICES

SCRIPTPATH="$HOME/GitLab/worm-poses/scripts/train_detector.py" 
python -W ignore $SCRIPTPATH \
--n_epochs 1000 \
--model_name 'fasterrcnn' \
--data_type 'detection-clusters' \
--batch_size 16 \
--num_workers 2 \
--lr 1e-4 \
--save_frequency 100

echo "Finished at :"`date`
exit 0