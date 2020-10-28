# worm-poses
 
Once unpacked it is a python list here each element has the following tuple:

[0] 'roi_mask' -> ROI without the background

[1] 'roi_full' -> ROI with full pixels

[2] 'widths' -> worm widths along the skeleton

[3] 'skels' -> skeletons coordinates

[4] 'contours' -> worm contours coordinates (first element should be the head)

[5] 'cnts_bboxes' -> bounding boxes for each worm contour in the image

[6] 'clusters_bboxes' -> bounding box of each worm cluster in the image (this should be one unless there are clusters with a very large separation).


Dataloader to load the data, and synthetize the images during training:[https://github.com/bozeklab/worm-poses/blob/master/worm_poses/flow/flow.py](https://github.com/bozeklab/worm-poses/blob/master/worm_poses/flow/flow.py)
