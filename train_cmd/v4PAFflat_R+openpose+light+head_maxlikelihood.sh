#!/bin/bash

#$ -P rittscher.prjc -q gpu8.q -pe shmem 1 -l gpu=1


source activate pytorch-1.0

echo "Username: " `whoami`
echo $HOME
echo cuda_id: $CUDA_VISIBLE_DEVICES

SCRIPTPATH="$HOME/GitLab/worm-poses/scripts/train_PAF.py" 
python -W ignore $SCRIPTPATH \
--n_epochs 3000 \
--data_type 'v4PAFflat' \
--model_name 'openpose+light+head' \
--loss_type 'maxlikelihood' \
--batch_size 24 \
--num_workers 4 \
--lr 1e-5 \
--save_frequency 600 \
--init_model_path "$HOME/workspace/WormData/worm-poses/results/v3/v3_openpose+light+head_maxlikelihood_20200129_080810_adam_lr0.0001_wd0.0_batch24/model_best.pth.tar"


echo "Finished at :"`date`
exit 0