#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 12:07:03 2019

@author: avelinojaver
"""

import sys
from pathlib import Path 
__root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(__root_dir))

import random
import numpy as np
import tables
import torch
import tqdm
import time
import pandas as pd

import multiprocessing as mp
mp.set_start_method('spawn', force = True)

from worm_poses.utils import get_device
from worm_poses.models import PoseDetector

def _prepare_batch(batch, device):
    frames, X = map(np.array, zip(*batch))
    X = X.astype(np.float32)/255.
    X = torch.from_numpy(X).unsqueeze(1)
    #X = X.to(device)
    return frames, X
    
    
def read_images_proc(mask_file, batch_size, queue, device):
    bn = Path(mask_file).stem
    with tables.File(mask_file, 'r') as fid:
        masks = fid.get_node('/mask')
        tot, img_h, img_w = masks.shape
        
        batch = []
        for frame_number in tqdm.trange(tot, desc = bn):
            img = masks[frame_number]
            if not img.any():
                continue
            
            batch.append((frame_number, img))
            if len(batch) >= batch_size:
                queue.put(_prepare_batch(batch, device))
                batch = []
                 
    if len(batch):
        queue.put(_prepare_batch(batch, device))
    queue.put(None)
    
    while not queue.empty():
        #wait until the consumer empty the queue before destroying the process.
        time.sleep(1)


def read_images_batch_proc(mask_file, batch_size, queue, device):
    bn = Path(mask_file).stem
    with tables.File(mask_file, 'r') as fid:
        masks = fid.get_node('/mask')
        tot, img_h, img_w = masks.shape
        
        
        for frame_number in tqdm.trange(0, tot, batch_size, desc = bn):
            X = masks[frame_number:frame_number + batch_size]
            X = X.astype(np.float32)/255.
            X = torch.from_numpy(X).unsqueeze(1)
            frames = list(range(frame_number, frame_number + X.shape[0]))
            queue.put((frames, X))
            
    queue.put(None)
    
    while not queue.empty():
        #wait until the consumer empty the queue before destroying the process.
        time.sleep(1)

# def process_images_proc(model, queue_images, queue_results, device):
#     with torch.no_grad():
#         while True:
#             dat = queue_images.get(timeout = 60)
#             if dat is None:
#                 queue_results.put(None)
#                 break
#             frames, X = dat
#             X = X.to(device)
#             predictions = model(X)
#             predictions = [{k : v.cpu().numpy() for k,v in p.items()} for p in predictions]
#             queue_results.put((frames, predictions))
    
#     queue_results.put(None)
#     while not queue_results.empty():
#         #wait until the consumer empty the queue before destroying the process.
#         time.sleep(1)


def _init_reader(mask_file, batch_size, device, images_queue_size):
    queue_images = mp.Queue(images_queue_size)
    
    reader_p = mp.Process(#target = read_images_proc, 
                          target = read_images_batch_proc, 
                          args= (mask_file, batch_size, queue_images, device)
                          )
    reader_p.daemon = True
    reader_p.start()        # Launch reader_proc() as a separate python process
    return reader_p, queue_images
    
@torch.no_grad()
def _process_from_reader(
                queue_images,
                  save_name, 
                  model, 
                  device
                  ):
    
    
    
    edges = []
    points = []
    current_poind_id = 0
    while True:
        dat = queue_images.get(timeout = 60)
        if dat is None:
            break
        frames, X = dat
        X = X.to(device)
        predictions = model(X)
        predictions = [{k : v.cpu().numpy() for k,v in p.items()} for p in predictions]
        
        for frame, prediction in zip(frames, predictions):
            
            seg_id, skel_x, skel_y = prediction['skeletons'].T
            nms_score = prediction['scores_abs'].T
            edge_p1, edge_p2 = prediction['edges_indices']
            edge_cost_PAF, edge_cost_R = prediction['edges_costs']
            
            
            N = len(seg_id)
            t_p = np.full(N, frame)
            p_ids = range(current_poind_id, current_poind_id + N)
            points += list(zip(p_ids, t_p, seg_id, skel_x, skel_y, nms_score))
            
            t_e = np.full(len(edge_p1), frame)
            edge_p1 += current_poind_id
            edge_p2 += current_poind_id
            edges += list(zip(t_e, edge_p1, edge_p2, edge_cost_PAF, edge_cost_R))
            
            current_poind_id += N
            
    
    points_df = pd.DataFrame(points, columns = ['point_id', 'frame_number', 'segment_id', 'x', 'y', 'score'])
    edges_df = pd.DataFrame(edges, columns = ['frame_number', 'point1', 'point2', 'cost_PAF', 'cost_R'])
    
    points_rec = points_df.to_records(index = False)
    edges_rec = edges_df.to_records(index = False)
    
    
    TABLE_FILTERS = tables.Filters(
                        complevel=5,
                        complib='zlib',
                        shuffle=True,
                        fletcher32=True)
    
    with tables.File(save_name, 'w') as fid:
        fid.create_table('/', 'points', obj = points_rec, filters = TABLE_FILTERS)
        fid.create_table('/', 'edges', obj = edges_rec, filters = TABLE_FILTERS)



def _process_file(mask_file, save_name, model, device, batch_size, images_queue_size = 4):
    reader_p, queue_images = _init_reader(mask_file, batch_size, device, images_queue_size)
    try:
        _process_from_reader(queue_images, save_name, model, device)
    except Exception as e:
        reader_p.terminate()
        raise e
    

def get_model_arguments(basename):
    model_name = basename.split('_')[1]
    
    if 'openpose+light+fullsym' in bn:
        model_args = dict(
            n_segments = 15,
            n_affinity_maps = 14,
            features_type = 'vgg11',
            n_stages = 4,
            )
        
    elif '+light' in model_name:
        model_args = dict(
            n_segments = 8,
            n_affinity_maps = 8,
            features_type = 'vgg11',
            n_stages = 4,
        )
        
        
        
    else:
        model_args = dict(
            n_segments = 8,
            n_affinity_maps = 8,
            features_type = 'vgg19',
            n_stages = 6,
        )
        
    model_args['use_head_loss'] = '+head' in model_name
    return model_args


if __name__ == '__main__':
    #bn = 'v2_openpose+light_maxlikelihood_20191211_150642_adam_lr0.0001_wd0.0_batch32'
    #bn = 'v2_openpose+head_maxlikelihood_20191219_150412_adam_lr0.0001_wd0.0_batch20'
    bn = 'v2_openpose+light+head_maxlikelihood_20191219_144819_adam_lr0.0001_wd0.0_batch32'
    #bn = 'v2_openpose+light+fullsym_maxlikelihood_20191229_223132_adam_lr0.0001_wd0.0_batch22'
    
    set_type = bn.partition('_')[0]
    model_path = Path.home() / 'workspace/WormData/worm-poses/results' / set_type  / bn / 'model_best.pth.tar'
    
    #save_dir_root = Path.home() / 'workspace/WormData/worm-poses/processed'
    #save_dir = save_dir_root / bn
    #save_dir.mkdir(exist_ok = True, parents = True)
    
    
    cuda_id = 0
    device = get_device(cuda_id)
    batch_size = 5#3
    
    images_queue_size = 2
    results_queue_size = 4
    
    model_args = get_model_arguments(bn)
    #%%
    model = PoseDetector(**model_args)
    
    state = torch.load(model_path, map_location = 'cpu')
    model.load_state_dict(state['state_dict'])
    model.eval()
    model = model.to(device)
    
    #%%
    #root_dir = Path.home() / 'workspace/WormData/screenings/mating_videos/wildMating/'
    root_dir = Path.home() / 'workspace/WormData/screenings/mating_videos/Mating_Assay/'
    #root_dir = Path.home() / 'workspace/WormData/screenings/Pratheeban/'
    #root_dir = Path.home() / 'workspace/WormData/screenings/Serena_WT_Screening/'
    #root_dir = Path.home() / 'workspace/WormData/screenings/pesticides_adam/Syngenta/'
    
    
    mask_dir = root_dir / 'MaskedVideos'
    save_root_dir = root_dir / f'ResultsNN_{bn}'
    
    mask_files = list(mask_dir.rglob('*.hdf5'))
    random.shuffle(mask_files)
    
    unprocessed_files = []
    for mask_file in mask_files:
        bn = mask_file.stem
        save_dir = Path(str(mask_file.parent).replace(str(mask_dir), str(save_root_dir)))
        save_dir.mkdir(exist_ok = True, parents = True)
        save_name = save_dir / (mask_file.stem + '_unlinked-skels.hdf5') 
        
        #_process_file(mask_file, save_name, model, device, batch_size)
        if save_name.exists():
            continue
        try:
            _process_file(mask_file, save_name, model, device, batch_size)
        except Exception as e:
            unprocessed_files.append((mask_file, str(e)))
            
    #I couldn't process the following files
    for fname, e in unprocessed_files:
        print(fname)
        print(e)
    
        
    