#!/bin/bash

#$ -P rittscher.prjc -q gpu8.q@compG004 -l gputype=p100
#$ -l gpu=1 -pe shmem 1

module use -a /mgmt/modules/eb/modules/all
module load Anaconda3/5.1.0
source activate pytorch-1.0

echo "Username: " `whoami`
echo $HOME
echo cuda_id: $CUDA_VISIBLE_DEVICES

SCRIPTPATH="$HOME/GitLab/worm-poses/scripts/train_PAF.py" 
python -W ignore $SCRIPTPATH \
--n_epochs 1000 \
--data_type 'allPAF' \
--model_name 'PAF+CPM+resnet50' \
--batch_size 48 \
--num_workers 1 \
--lr 1e-4 \
--save_frequency 100

echo "Finished at :"`date`
exit 0