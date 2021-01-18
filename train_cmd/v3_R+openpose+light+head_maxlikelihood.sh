#!/bin/bash

echo "Username: " `whoami`
echo $HOME
echo cuda_id: $CUDA_VISIBLE_DEVICES

SCRIPTPATH="../scripts/train_PAF.py"
python -W ignore $SCRIPTPATH \
--n_epochs 3000 \
--data_type 'v3' \
--model_name 'openpose+light+head' \
--loss_type 'maxlikelihood' \
--batch_size 24 \
--num_workers 4 \
--lr 1e-5 \
--save_frequency 500 \
--init_model_path "$HOME/workspace/WormData/worm-poses/results/v2/v2_openpose+light+head_maxlikelihood_20191219_144819_adam_lr0.0001_wd0.0_batch32/model_best.pth.tar"


echo "Finished at :"`date`
exit 0