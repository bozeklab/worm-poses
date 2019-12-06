#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 17:05:49 2018

@author: avelinojaver
"""

import sys
from pathlib import Path 
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))
import tqdm
import torch
import matplotlib.pylab as plt
import numpy as np
import cv2


from worm_poses.trainer import _get_model
from worm_poses.flow import maps2skels

#%%
if __name__ == '__main__':
    model_path = '/Volumes/rescomp1/data/WormData/results/worm-poses/logs/manually-annotated-PAF_20190116_181119_CPMout-PAF_adam_lr0.0001_wd0.0_batch16/checkpoint.pth.tar'
    model_name = 'CPMout-PAF'
    dataset = 'manually-annotated-PAF'
    
    n_segments = 25
    n_affinity_maps = 20
    
    cuda_id = 0
    if torch.cuda.is_available():
        print("THIS IS CUDA!!!!")
        dev_str = "cuda:" + str(cuda_id)
    else:
        dev_str = 'cpu'
    device = torch.device(dev_str)
    
    
    
    model, out_size = _get_model(model_name, n_segments, n_affinity_maps)
    
    
    state = torch.load(model_path, map_location = 'cpu')
    #%%
    model.load_state_dict(state['state_dict'])
    model.eval()
    model = model.to(device)
    #%%
    root_dir = Path('/Users/avelinojaver/Downloads/BBBC010_v1_images/')
    
    for ifname, fname in enumerate(tqdm.tqdm(list(root_dir.glob('*.tif')))):
        img = cv2.imread(str(fname), -1)
        
        bot, top = img.min(), img.max()
        
        img = (img.astype(np.float32)-bot)/(top-bot)
        #img = cv2.resize(img, dsize=(0,0), fx=1.25, fy=1.25)
        
        X = img[None, None]
        X = torch.tensor(X)
        
        #X = X*255 #i trained the first model using the 0,255 instead of 0, 1.
        with torch.no_grad():
            X = X.to(device)
            outs = model(X)
            cpm_maps_r, paf_maps_r = outs[-1]
        
        
        
        cpm_map = cpm_maps_r[0]
        
        cpm_map = cpm_map.numpy()
        
        #TODO there is a bug in maps2skels if there is not enough trajectories. i need to correct it...
        skeletons_r = maps2skels(cpm_map, threshold_abs = 0.05)
       
        
        mid = 24
        
        fig, axs = plt.subplots(1,2, sharex=True, sharey=True)
        
        
        axs[0].imshow(cpm_map.max(axis=0))
        axs[1].imshow(img, cmap='gray')
        for ss in skeletons_r:
            plt.plot(ss[:, 0], ss[:, 1], '.-')
            plt.plot(ss[mid, 0], ss[mid, 1], 'o')
            
        if ifname > 0:
            break
        #%%
        