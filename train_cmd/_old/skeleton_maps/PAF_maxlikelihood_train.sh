#!/bin/bash

#$ -P rittscher.prjc -q gpu8.q -pe shmem 1 -l gpu=1


source activate pytorch-1.0

echo "Username: " `whoami`
echo $HOME
echo cuda_id: $CUDA_VISIBLE_DEVICES

SCRIPTPATH="$HOME/GitLab/worm-poses/scripts/train_PAF.py" 
python -W ignore $SCRIPTPATH \
--n_epochs 1000 \
--data_type 'allPAF' \
--loss_type 'maxlikelihood' \
--batch_size 48 \
--num_workers 1 \
--lr 1e-4 \
--save_frequency 100

echo "Finished at :"`date`
exit 0