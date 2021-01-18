#!/bin/bash

echo "Username: " `whoami`
echo $HOME
echo cuda_id: $CUDA_VISIBLE_DEVICES

SCRIPTPATH="$HOME/GitLab/worm-poses/scripts/train_PAF.py" 
python -W ignore $SCRIPTPATH \
--n_epochs 1000 \
--data_type 'v2+halfboxes' \
--model_name 'keypointrcnn+resnet18' \
--loss_type 'maxlikelihood' \
--batch_size 28 \
--roi_size 256 \
--num_workers 4 \
--lr 1e-4 \
--save_frequency 200

echo "Finished at :"`date`
exit 0