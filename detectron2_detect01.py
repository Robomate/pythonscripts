
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Purpose: Inference DETECTRON2
Date: 12/2022
Version: V01
Author: MAKO
Description:
    use DETECTRON2 for
    MODELTYPE = "OD" # object detection
    MODELTYPE = "IS" # instance segmentation
    MODELTYPE = "KP" # keypoint detection
    MODELTYPE = "LVIS" # LVIS segmentation
    MODELTYPE = "PS" # panoptic segmentation 

Dependencies:
    cd detectron2; conda activate detectron2
    python detect04.py

Links:
https://github.com/facebookresearch/detectron2/blob/main/MODEL_ZOO.md # check Inference times
"""
import cv2
import torch
import time
import glob
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
from detectron2.utils.visualizer import Visualizer, ColorMode
from detectron2 import model_zoo

# choose model type
MODELTYPE = "OD" # object detection
# MODELTYPE = "IS" # instance segmentation
MODELTYPE = "KP" # keypoint detection
# MODELTYPE = "LVIS" # LVIS segmentation
# MODELTYPE = "PS" # panoptic segmentation

# choose input source
source = "VIDEOSTREAM"
# source = "IMAGESTREAM"
# source = "IMAGESINGLE"


# data paths
scalefactor = 1.0
videopath = 0 # webcam
# scalefactor = 0.7
# videopath = "C:\\Users\\x\\Pictures\\Video Projects\\20211216_160453.mp4" # video: 1920x1080
videopath = "C:\\Users\\x\\Pictures\\Video Projects\\backfull.mp4" # video: 700x700

dir_name = "levelcrossing_20220531_1"
dir_name = "roadworks_20220602_1"
path_02 = "C:\\Users\\x\\Pictures\\Video Projects\\" + dir_name + "/data/images/"
imagepath = "parkinglot2.jpg" # image
# !wget http://images.cocodataset.org/val2017/000000439715.jpg -O input.jpg

def InitModel():
    """
    inputs:
    returns:

    """
    # Create config
    cfg = get_cfg()
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
    if MODELTYPE == "OD": # object detection
        pathtoyaml = "COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"
    elif MODELTYPE == "IS": # instance segmentation
        pathtoyaml = "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"
    elif MODELTYPE == "KP": # keypoint detection
        pathtoyaml = "COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml"
    elif MODELTYPE == "LVIS": # LVIS segmentation
        pathtoyaml = "LVISv0.5-InstanceSegmentation/mask_rcnn_X_101_32x8d_FPN_1x.yaml"
    elif MODELTYPE == "PS": # panoptic segmentation
        pathtoyaml = "COCO-PanopticSegmentation/panoptic_fpn_R_50_3x.yaml"

    cfg.merge_from_file(model_zoo.get_config_file(pathtoyaml))
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(pathtoyaml)
    if torch.cuda.is_available():
        cfg.MODEL.DEVICE = "cuda" # or "cuda"
        print("Model running on Cuda" )
    else:
        cfg.MODEL.DEVICE = "cpu" # or "cuda"
        print("Model running on CPU" )

    return cfg

def cv2GetVideo(config, videopath, scalefac):
    """
    inputs:
    returns:

    """
    cap = cv2.VideoCapture(videopath)
    if not cap.isOpened():
        print("Error, Cannot open video.")

    while(cap.isOpened()):
        ts = time.time()
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        else:
            vis = DoPrediction(config, frame, scalefac)
            te = time.time()
            td = 1.0 /(te-ts)
            print("FPS: %.2f" % td)
            cv2.imshow('', vis.get_image()[:, :, ::-1])
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()

def DoPrediction(config, image, scalefac):
    """
    inputs:
    returns:

    """
    # Create predictor
    predictor = DefaultPredictor(config)
    # Make prediction
    if MODELTYPE == "PS": # panoptic segmentation
        outputs, seginfo = predictor(image)["panoptic_seg"]
        viz = Visualizer(image[:, :, ::-1], MetadataCatalog.get(config.DATASETS.TRAIN[0]), scale=scalefac)
        v = viz.draw_panoptic_seg_predictions(outputs.to("cpu"),seginfo)

    else:
        outputs = predictor(image)
        viz = Visualizer(image[:, :, ::-1], MetadataCatalog.get(config.DATASETS.TRAIN[0]), scale=scalefac)
        v = viz.draw_instance_predictions(outputs["instances"].to("cpu"))

    return v


if __name__ == "__main__":
    cfg0 = InitModel() # Init the Model
    if source == "VIDEOSTREAM": # eval video
        cv2GetVideo(cfg0, videopath, scalefactor)
    elif source == "IMAGESTREAM": # eval video
        # read in all filenames
        file_list = []
        for file_name in sorted(glob.glob(path_02 +'*.jpg')):  
            file_list.append(file_name)
        # print(file_list)

        for im in file_list:
            ts = time.time()
            im = cv2.imread(im)
            vis = DoPrediction(cfg0, im, 1.0)
            te = time.time()
            td = 1.0 /(te-ts)
            print("FPS: %.2f" % td)
            cv2.imshow('',vis.get_image()[:, :, ::-1])
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    else: # eval image
        im = cv2.imread(imagepath)
        vis = DoPrediction(cfg0, im, 1.0)
        cv2.imshow('',vis.get_image()[:, :, ::-1])
        cv2.waitKey(0)




