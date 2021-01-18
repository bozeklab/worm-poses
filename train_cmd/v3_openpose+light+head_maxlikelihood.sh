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
--lr 1e-4 \
--save_frequency 500

echo "Finished at :"`date`
exit 0