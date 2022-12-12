#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Purpose: 
Date: 03/2022
Version: V01
Author: MAKO
Description:
    Test Data: PCW
    97 Lidar Frames for 14 sec (7HZ)
Dependencies:

Links:
still missing msgs for gps:
vehicle_gps_position
sensor_gps

For Tracking:
KALMAN
https://github.com/rlabbe/filterpy

MPC
http://grauonline.de/wordpress/?page_id=3244
https://dynamics-and-control.readthedocs.io/en/latest/2_Control/7_Multivariable_control/Simple%20MPC.html

"""
import os
import sys
import numpy as np
import glob
import pandas as pd
import open3d as o3d
import math
from matplotlib import colors
from matplotlib import cm
from datetime import datetime

import db_landmark_features_01 as lmfeat
# import pcdrosbag2_2022_05_03_2 as pcddb
np.set_printoptions(suppress=True)

# globals
# path_01 = "/home/sam/Schreibtisch/D4S/pcwtest_03052022/pcwtest_03052022_csvfiles/logging_rosbags134mb2/" # Linux Lenovo
# name_01 = "pcdrosbag2_2022_05_03-14_13_20_01"

# path_01 = "/home/sam/Schreibtisch/D4S/office_test_24052022_1/data/pcd/"
# dir_name = "bahngang_test_30052022_1"
# dir_name = "bahngang_test_01062022_12"
# dir_name = "parkplatz_test_31052022_4"
# dir_name = "strommast_test_01062022_5"
dir_name = "levelcrossing_20220531_1"


path_01 = "/home/sam/Schreibtisch/D4S/" + dir_name + "/data/pcd/"
path_02 = "/home/sam/Schreibtisch/D4S/" + dir_name + "/data/eval/"
# name_01 = "frame"
name_02 = "double_eval"

extension_01 = ".pcd" # file extension
extension_02 = ".csv" # file extension

# set options:
# perform calibration
ENABLE_CALIBRATION = False
# ENABLE_CALIBRATION = True

# one time clustering
SINGLE_CLUSTERING = False
# SINGLE_CLUSTERING = True

# 2 times clustering
DOUBLE_CLUSTERING = False
DOUBLE_CLUSTERING = True

# export evaluation stats
EXPORT_EVAL = False
EXPORT_EVAL = True

# intensity/distance profiles
####################################################################

# # Reflex foil 1,2x2,0m: 200m siepark measurement
# intensity_thres_list = [200,170,150,100] # intensity reflection [0-255]
# distances_thres_list = [1,40,80,100,1000] # in meter


# Reflex foil 1,2x2,0m: 200m siepark measurement
intensity_thres_list = [150,120,100,100] # intensity reflection [0-255]
distances_thres_list = [1,10,20,100,1000] # in meter


# single  threshold 
single_threshold = 150 # (for calibration)
# intensity_thres_list = [single_threshold,] # intensity reflection [0-255]
# distances_thres_list = [1,single_threshold,] # in meter

# cluster step 1
MINDIST1 = 0.8 # min distance of cluster: in meter
MINPNTS1 = 4 # minimum number of pnts per cluster

# cluster step 2
MINDIST2 = 0.3 # min distance of cluster: in meter
MINPNTS2 = 6 # minimum number of pnts per cluster

# Reflex foil 1,2x2,0m: 200m siepark measurement
####################################################################

# intensity features 
# intensity_thres_list = [200,170,150,100] # intensity reflection [0-255]
# distances_thres_list = [5,40,80,100,1000] # in meter

# # statistical features
# STDEVX_MIN = 0.00 # landmark width 
# STDEVY_MIN = 0.00 # landmark width 
# STDEVZ_MIN = 0.2 # landmark height: 1.20m
# STDEVX_MAX = 0.50 # landmark width: 0.40m
# STDEVY_MAX = 0.50 # landmark width: 0.40m
# STDEVZ_MAX = 1.3 # landmark height: 1.20m

# # geometric features
# MINMAXX_MIN = 0.00 # landmark width 
# MINMAXY_MIN = 0.00 # landmark width 
# MINMAXZ_MIN = 0.43 # landmark third of the height: 1.20m
# MINMAXX_MAX = 0.50 # landmark width: 0.40m
# MINMAXY_MAX = 0.50 # landmark width: 0.40m
# MINMAXZ_MAX = 1.3 # landmark height: 1.20m


# compute automated feature properties in meters)
####################################################################

# set featurelist:
# featurelist = lmfeat.feature_list_01 # single small cube 0,3x0,3m (wxh)
# featurelist = lmfeat.feature_list_02 # big cube standing 0,3x0,6m (wxh)
# featurelist = lmfeat.feature_list_03 # big cube lying 0,6x0,3m (wxh)
# featurelist = lmfeat.feature_list_04 # pyramid even, bottom: big cube lying, top: small cube
featurelist = lmfeat.feature_list_05 # double sign lying

# statistical features
stdev_factor = 0.8 # scale factor
STDEVX_MIN = round(featurelist[0] - featurelist[0] * stdev_factor, 2) # landmark width 
STDEVY_MIN = round(featurelist[1] - featurelist[1] * stdev_factor, 2) # landmark width 
STDEVZ_MIN = round(featurelist[2] - featurelist[2] * stdev_factor, 2) # landmark height
STDEVX_MAX = round(featurelist[0] + featurelist[0] * stdev_factor, 2) # landmark width
STDEVY_MAX = round(featurelist[1] + featurelist[1] * stdev_factor, 2) # landmark width
STDEVZ_MAX = round(featurelist[2] + featurelist[2] * stdev_factor, 2) # landmark height

# geometric features
minmax_factor = 0.8 # scale factor
MINMAXX_MIN = round(featurelist[3] - featurelist[3] * minmax_factor, 2) # landmark width 
MINMAXY_MIN = round(featurelist[4] - featurelist[4] * minmax_factor, 2) # landmark width 
MINMAXZ_MIN = round(featurelist[5] - featurelist[5] * minmax_factor, 2) # landmark height
MINMAXX_MAX = round(featurelist[3] + featurelist[3] * minmax_factor, 2) # landmark width
MINMAXY_MAX = round(featurelist[4] + featurelist[4] * minmax_factor, 2) # landmark width
MINMAXZ_MAX = round(featurelist[5] + featurelist[5] * minmax_factor, 2) # landmark height


def get_colormap_tableau20():
    """
    Get the Tableau20 colormap.
    
    Returns:
        color : rgb tuple, normalized to [0, 1] range
    """
    tableau20 = [(31, 119, 180), (14, 199, 232), (255, 127, 14), (255, 187, 120),
                 (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                 (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                 (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                 (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

    # Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
    for i in range(len(tableau20)):
        r, g, b = tableau20[i]
        tableau20[i] = (r / 255., g / 255., b / 255.)

    return tableau20

def Euler_ZYX_deg_4x4(
    rotx_deg, # float, rotation angle, roll [degrees] 
    roty_deg, # float, rotation angle, pitch [degrees]
    rotz_deg, # float, rotation angle, yaw [degrees]  
    print_data, # bool, print out data
    ):
    """ 
    For 4x4 Homogeneous Transformation Matrix:
    Apply Euler Rotation by Tait-Bryan Angles Convention: ZYX
    as used in mobile robotics and the aerospace industry.

    inputs: 
        rotx_deg, # float, rotation angle, roll [degrees] 
        roty_deg, # float, rotation angle, pitch [degrees]
        rotz_deg, # float, rotation angle, yaw [degrees] 
        print_data, bool, print out data 
    outputs:
        RZYX44, np.array, 4x4 Homgeneous Rotation Matrix [radians]
    dependencies:
        numpy
    """
    # convert degrees to radians
    roll= np.deg2rad(rotx_deg)
    pitch= np.deg2rad(roty_deg)
    yaw = np.deg2rad(rotz_deg)

    R44X = np.zeros ((4,4))
    R44X[0,0] = 1
    R44X[3,3] = 1
    R44X[1, 1:3] = [np.cos(roll), -np.sin(roll)]
    R44X[2, 1:3] = [np.sin(roll),  np.cos(roll)]
    
    R44Y = np.zeros ((4,4))
    R44Y[1,1] = 1
    R44Y[3,3] = 1
    R44Y[0, 0:3] = [ np.cos(pitch),0, np.sin(pitch)]
    R44Y[2, 0:3] = [-np.sin(pitch),0, np.cos(pitch)]
    
    R44Z = np.zeros ((4,4))
    R44Z[2,2] = 1
    R44Z[3,3] = 1
    R44Z[0, 0:2] = [np.cos(yaw), -np.sin(yaw)]
    R44Z[1, 0:2] = [np.sin(yaw),  np.cos(yaw)]
    
    RZYX44 = R44Z@R44Y@R44X

    if print_data:
        print ('rx, roll\n',R44X)
        print ('ry, pitch\n',R44Y)
        print ('rz, yaw\n',R44Z)
        print("RZYX44")
        print(RZYX44)

    return RZYX44

def azimuthAngle(x1, y1, x2, y2):
    '''
    https://developpaper.com/example-of-python-calculating-azimuth-angle-based-on-the-coordinates-of-two-points/
    '''
    angle = 0.0;
    dx = x2 - x1
    dy = y2 - y1
    if x2 == x1:
        angle = math.pi / 2.0
        if y2 == y1 :
            angle = 0.0
        elif y2 < y1 :
            angle = 3.0 * math.pi / 2.0
    elif x2 > x1 and y2 > y1:
        angle = math.atan(dx / dy)
    elif x2 > x1 and y2 < y1 :
        angle = math.pi / 2 + math.atan(-dy / dx)
    elif x2 < x1 and y2 < y1 :
        angle = math.pi + math.atan(dx / dy)
    elif x2 < x1 and y2 > y1 :
        angle = 3.0 * math.pi / 2.0 + math.atan(dy / -dx)
    return (angle * 180 / math.pi)

def set_open3d_viewpoint(
    vis, # object, o3d.visualization.Visualizer()
    rotx_deg, # float, rotation angle, roll [degrees] 
    roty_deg, # float, rotation angle, pitch [degrees]
    rotz_deg, # float, rotation angle, yaw [degrees] 
    transx, # float, tanslation x axis [meter]
    transy, # float, tanslation y axis [meter]
    transz, # float, tanslation z axis [meter]
    print_data, # bool, print out data
    ):
    """ 
    Todo!! : add camera intrinsics
    Set Viewpoint of open3d Window

    inputs: 
        vis, # object, o3d.visualization.Visualizer()
        rotx_deg, # float, rotation angle, roll [degrees] 
        roty_deg, # float, rotation angle, pitch [degrees]
        rotz_deg, # float, rotation angle, yaw [degrees] 
        transx, # float, tanslation x axis [meter]
        transy, # float, tanslation y axis [meter]
        transz, # float, tanslation z axis [meter]
        print_data, # bool, print out data
    outputs:
        params_new, object, new camera parameter
        params_old, object, old camera parameter
    dependencies:
        Euler_ZYX_deg_4x4()
        numpy
        open3d  
    """
    # get/set camera matrices
    ctr = vis.get_view_control()
    params_old = ctr.convert_to_pinhole_camera_parameters() # get old camera parameter

    # camera extrinsics
    ###################################
    extrinsic_old = params_old.extrinsic
    extrinsic_new = params_old.extrinsic.copy()

    # set viewpoint: rotation, add new rotation to existing rotation
    RZYX = Euler_ZYX_deg_4x4(
        rotx_deg, # rotation angle in degrees, roll 
        roty_deg, # rotation angle in degrees, pitch
        rotz_deg, # rotation angle in degrees, yaw 
        print_data, # optional: print out data
        )
    RZYX2 = extrinsic_new@RZYX
    extrinsic_new[0][0:3] = RZYX2[0][0:3]
    extrinsic_new[1][0:3] = RZYX2[1][0:3]
    extrinsic_new[2][0:3] = RZYX2[2][0:3]

    # set viewpoint: translation
    extrinsic_new[0][3] = transx
    extrinsic_new[1][3] = transy 
    extrinsic_new[2][3] = transz
    
    # camera intrinsics
    ###################################
    intrinsic_old = params_old.intrinsic.intrinsic_matrix.copy()
    intrinsic_new = intrinsic_old

    # set new camera matrices
    params_new = o3d.camera.PinholeCameraParameters() # set new camera parameter
    params_new.extrinsic = extrinsic_new
    params_new.intrinsic = o3d.camera.PinholeCameraIntrinsic()
    params_new.intrinsic.intrinsic_matrix = intrinsic_new 

    if print_data:
        print("extrinsic old:")
        print(extrinsic_old)
        print("extrinsic new:")
        print(extrinsic_new)
        print("intrinsic old:")
        print(intrinsic_old)
        print("intrinsic new:")
        print(intrinsic_new)

    return params_new, params_old



def main(args=None):

    try:
        tableau20 = get_colormap_tableau20()
        # print(tableau20)
        colors2 = tableau20

        # read in all filenames
        file_list = []
        for file_name in sorted(glob.glob(path_01 +'*.csv')):  
            file_list.append(file_name)
        print(file_list)

        # single file for init visualizer
        ##########################################################
        # file_name = path_01 + name_01 + extension_02
        glued_data = pd.DataFrame()
        file_name = file_list[40]
        print(file_name)
        print()
        x = pd.read_csv(file_name, low_memory=False, sep=";")
        x = x.apply(pd.to_numeric, errors='coerce')
        glued_data = pd.concat([glued_data,x],axis=0)
        # print(glued_data)
        pcd_array_01 = np.transpose(np.asarray(glued_data))
        # pcd_array_02 = np.transpose(pcd_array_01[1:4]).astype(float)
        pcd_array_02 = np.transpose(pcd_array_01[1:4])
        # pcd_array_03 = np.transpose(pcd_array_01[4])
        pcd_array_03 = pcd_array_01[4]
        # = np.transpose(pcd_array_01)
        print(pcd_array_02[-1])

        # numpy to new pointcloud
        pcd01 = o3d.geometry.PointCloud()
        pcd01.points = o3d.utility.Vector3dVector(pcd_array_02)

        # colors
        colors2 = [(0.6, 0.6, 0.6) for i in range(len(pcd_array_03))]
        # cnt_2 = 0
        # for idx0 in range(len(pcd_array_03)):
        #     colors2[idx0] = tableau20[cnt_2]
        #     cnt_2 += 1
        #     if cnt_2 == len(tableau20):
        #         cnt_2 = 0
        for idx0 in range(len(pcd_array_03)):
            if pcd_array_03[idx0]> single_threshold:
                colors2[idx0] = tableau20[6]
            else:
                colors2[idx0] = tableau20[0]

        # colors2 = [(0.6, 0.6, 0.6) for i in range(len(pcd_array_03))]
        pcd01.colors = o3d.utility.Vector3dVector(colors2)
        # pcd01.colors = o3d.utility.Vector3dVector(np.array([[8.0,7.0,6.0],[5.0,4.0,3.0]]))
        # pcd01.colors = o3d.utility.Vector3dVector(img[img_mask, :].astype(float) / 255.0)

        # This is for visualization of the received point cloud.
        ##########################################################
        vis = o3d.visualization.Visualizer()
        vis.create_window()
        vis.add_geometry(pcd01)

                # create custom viewpoints by camera extrinsics
        #####################################################################################
        params_topview, __  = set_open3d_viewpoint(
        vis, # vis, # object, o3d.visualization.Visualizer()
        0, # rotx_deg, # float, rotation angle, roll [degrees] 
        0, # roty_deg, # float, rotation angle, pitch [degrees]
        0, # rotz_deg, # float, rotation angle, yaw [degrees] 
        -50, # transx, # float, tanslation x axis [meter]
        0, # transy, # float, tanslation y axis [meter]
        100, # transz, # float, tanslation z axis [meter]
        True, # print_data, # bool, print out data
        )

        params_profileview, __  = set_open3d_viewpoint(
        vis, # vis, # object, o3d.visualization.Visualizer()
        -90, # rotx_deg, # float, rotation angle, roll [degrees] 
        0, # roty_deg, # float, rotation angle, pitch [degrees]
        0, # rotz_deg, # float, rotation angle, yaw [degrees] 
        -50, # transx, # float, tanslation x axis [meter]
        10, # transy, # float, tanslation y axis [meter]
        60, # transz, # float, tanslation z axis [meter]
        True, # print_data, # bool, print out data
        )
        
        params_profileview2, __  = set_open3d_viewpoint(
        vis, # vis, # object, o3d.visualization.Visualizer()
        -40, # rotx_deg, # float, rotation angle, roll [degrees] 
        70, # roty_deg, # float, rotation angle, pitch [degrees]
        50, # rotz_deg, # float, rotation angle, yaw [degrees] 
        0, # transx, # float, tanslation x axis [meter]
        5, # transy, # float, tanslation y axis [meter]
        25, # transz, # float, tanslation z axis [meter]
        True, # print_data, # bool, print out data
        )
        
        params_panoramaview, __  = set_open3d_viewpoint(
        vis, # vis, # object, o3d.visualization.Visualizer()
        -10, # rotx_deg, # float, rotation angle, roll [degrees] 
        40, # roty_deg, # float, rotation angle, pitch [degrees]
        70, # rotz_deg, # float, rotation angle, yaw [degrees] 
        -20, # transx, # float, tanslation x axis [meter]
        30, # transy, # float, tanslation y axis [meter]
        30, # transz, # float, tanslation z axis [meter]
        True, # print_data, # bool, print out data
        )
        
        # set viewpoints here:

        # calibration viewpoints
        # params_calibration = params_profileview
        params_calibration = params_profileview2
        # params_calibration = params_panoramaview
        # params_calibration = params_topview

        # live viewpoints
        # params_liveview = params_profileview
        params_liveview = params_profileview2
        # params_liveview = params_panoramaview
        # params_liveview = params_topview

        # optional: calibration
        ##########################################################
        if ENABLE_CALIBRATION:
            ctr = vis.get_view_control()
            ctr.convert_from_pinhole_camera_parameters(params_calibration, allow_arbitrary=True)
            vis.poll_events()
            vis.update_renderer()
            vis.run()

        # first and last csv files in dir
        #########################################################
        file_list2 = []
        file_list2.append(file_list[0])
        file_list2.append(file_list[-1])
        print(file_list2)
        print()

        cnt = 0

        # for eval all candidates
        total_lm_list = []
        total_lm_pnts_median = []
        total_lm_idx_list = []
        total_lm_int_list = []
        # final landmark cluster
        lm_cluster_list = []
        lm_cluster_mean_list = []
        lm_cluster_median_list = []
        lm_cluster_idx_list = []

        # for eval double clustering
        final_frame_list = []
        final_pnt_list = []
        final_dist_list = []
        final_num_pnt_list = []
        final_num_pntc1_list = []
        final_num_pntc2_list = []
        final_acc_list = []
        candidate_list = []
        final_pnt_azimuth_list = []
        final_pnt_elevation_list = []

        # for file_name in file_list2: 
        for file_name in file_list: 
            # import data
            ################################################################
            glued_data = pd.DataFrame()
            x = pd.read_csv(file_name, low_memory=False, sep=";")
            x = x.apply(pd.to_numeric, errors='coerce')
            glued_data = pd.concat([glued_data,x],axis=0)
            cnt += 1
            print(cnt, file_name)
            # print(glued_data)

            # convert to open3d
            ################################################################
            pcd_array_01 = np.transpose(np.asarray(glued_data))
            pcd_array_02 = np.transpose(pcd_array_01[1:4])
            pcd_array_04 = np.transpose(pcd_array_01[1:3])
            # pcd_array_03 = np.transpose(pcd_array_01[4])
            pcd_array_03 = pcd_array_01[4]
            # = np.transpose(pcd_array_01)

            # numpy to new pointcloud
            vis.remove_geometry(pcd01)  
            pcd01 = o3d.geometry.PointCloud()
            pcd01.points = o3d.utility.Vector3dVector(pcd_array_02)

            # optional: assign uniform color to PCD
            colors2 = [(0.6, 0.6, 0.6) for i in range(len(pcd_array_03))]
            # pcd01.colors = colors2
            for idx0 in range(len(pcd_array_03)):
                colors2[idx0] = tableau20[1]



            if SINGLE_CLUSTERING:
                # appply intensity distance profile
                ###################################################################
                intensity = pcd_array_03
                xyaxis = pcd_array_04
                xyzaxis = pcd_array_02
                dist_list = [] # distance in polar coordinates (x,y)
                xyz_list = [] # coordinates (x,y,z)
                int_list = [] # intensity
                idx_list = [] # global indices for coloring pcd
                nums_list = [] # number of elements
                labels_list = [] # cluster labels
                ego_pos_list = [] # number of elements

                for idx6 in range(len(intensity_thres_list)):
                    # get temporarily values from intensity threshold
                    intensity_idx = np.where(intensity > intensity_thres_list[idx6])[0].tolist()
                    xyaxistmp = xyaxis[intensity_idx] 
                    xyzaxistmp = xyzaxis[intensity_idx]
                    intensitytmp = intensity[intensity_idx]
                
                    # check distance thresholds:
                    distances_polar = np.linalg.norm(xyaxistmp,axis=1)
                    # distances_spherical = np.linalg.norm(xyzaxistmp,axis=1)
                    # distances = distances_spherical
                    distances = distances_polar
                    # print("intensity_thres", intensity_thres_list[idx])
                    # print(distances_polar)
                    distances_idx = np.where(np.logical_and(distances > distances_thres_list[idx6], distances < distances_thres_list[idx6+1]))[0].tolist()
                    distances_polar_filtered = distances[distances_idx]
                    xyz_filtered = xyzaxistmp[distances_idx]
                    intensity_filtered = intensitytmp[distances_idx]
                    idx_filtered = np.asarray(intensity_idx)[distances_idx]

                    # distances_median = np.median(distances)
                    # dist_list.append(distances_median) 
                    if len(distances_polar_filtered) > 0:
                        dist_list.append(distances_polar_filtered) 
                        xyz_list.append(xyz_filtered) 
                        int_list.append(intensity_filtered) 
                        nums_list.append(len(distances_polar_filtered))
                        idx_list.append(idx_filtered)  
                    else: 
                        nums_list.append(len(distances_polar_filtered)) 
                        

                    # labels_list.append(labels)

                    # debugging: all lm candidates
                    # print(intensity_idx)
                    # print(intensitytmp)
                    # print(xyaxistmp)
                    # print(xyzaxistmp)
                    # print(distances_polar_filtered)
                    # print(xyz_filtered)
                    # print(intensity_filtered)
                    # print()
                    # print(distances_median)
                    # distances_mean = np.mean(distances)
                    # intensity_val = distances[intensity_val]

                print()
                print("dist_polar_list")
                print("distances_thres_list", distances_thres_list)
                print("intensity_thres_list", intensity_thres_list)
                # print(dist_list)
                # print(xyz_list)
                # print(idx_list)
                print(nums_list)

                # dist_array = np.concatenate(dist_list, axis=0)
                xyz_array = np.concatenate(xyz_list, axis=0)
                idx_array = np.concatenate(idx_list, axis=0)
                # print(dist_array)
                print(xyz_array)
                # print(ego_pos_list)
                print()
                # max_idx = np.argmax(nums_list)
                # max_pnt = np.max(nums_list)


                # apply clustering (-1 are outliers!!)
                ###############################################################
                pcd_array_04 = xyz_array
                # print(pcd_array_04.shape)
                pcd02 = o3d.geometry.PointCloud()
                pcd02.points = o3d.utility.Vector3dVector(pcd_array_04)
                labels = np.array(pcd02.cluster_dbscan(
                eps=1.55, 
                min_points=2,
                ))

                # debugging
                print(labels)

                # apply statistical and geometric features
                ###############################################################
                labels_max = np.max(labels)
                lm_color_cluster_idx = -2 # init idx landmark cluster
                for idx_4 in range(labels_max+1):
                    cluster_pnts_idx = np.where(labels== idx_4)[0].tolist() # get indices
                    # extract pnts
                    pcd_array_05 = pcd_array_04[cluster_pnts_idx]
                    # apply statistics to extrated pnts
                    pcd_array_mean = np.mean(pcd_array_05,axis=0) # mean for each axis
                    pcd_array_median= np.median(pcd_array_05,axis=0) # mean for each axis
                    pcd_array_std = np.std(pcd_array_05,axis=0) # std deviaton for each axis
                    pcd_array_min = np.min(pcd_array_05,axis=0) # min value for each axis
                    pcd_array_max = np.max(pcd_array_05,axis=0) # max value for each axis
                    pcd_array_minmax = abs(pcd_array_max - pcd_array_min) # minmax value for each axis

                    # # debugging:
                    # print(idx_4)
                    # print(cluster_pnts_idx)
                    # # print(pcd_array_04)
                    # print(pcd_array_05)
                    # print(pcd_array_mean)
                    # print(pcd_array_std)
                    # print(pcd_array_minmax)
                    # print()

                    # statistical features
                    # STDEVX_MIN = 0.00 # landmark width 
                    # STDEVY_MIN = 0.00 # landmark width 
                    # STDEVZ_MIN = 0.2 # landmark height: 1.20m
                    # STDEVX_MAX = 0.50 # landmark width: 0.40m
                    # STDEVY_MAX = 0.50 # landmark width: 0.40m
                    # STDEVZ_MAX = 1.3 # landmark height: 1.20m

                    # # geometric features
                    # MINMAXX_MIN = 0.00 # landmark width 
                    # MINMAXY_MIN = 0.00 # landmark width 
                    # MINMAXZ_MIN = 0.65 # landmark third of the height: 1.20m
                    # MINMAXX_MAX = 0.50 # landmark width: 0.40m
                    # MINMAXY_MAX = 0.50 # landmark width: 0.40m
                    # MINMAXZ_MAX = 1.3 # landmark height: 1.20m

                    ARRAY_FLAG_FEATURES = np.array([0,0,0,0,0,0])
                    print(pcd_array_minmax[2])
                    # check if statistical features are true
                    if pcd_array_std[0] > STDEVX_MIN and pcd_array_std[0] < STDEVX_MAX:
                        ARRAY_FLAG_FEATURES[0] = 1
                    if pcd_array_std[1] > STDEVY_MIN and pcd_array_std[1] < STDEVY_MAX:
                        ARRAY_FLAG_FEATURES[1] = 1
                    if pcd_array_std[2] > STDEVZ_MIN and pcd_array_std[2] < STDEVZ_MAX:
                        ARRAY_FLAG_FEATURES[2] = 1
                    # check if geometric features are true
                    if pcd_array_minmax[0] > MINMAXX_MIN and pcd_array_minmax[0] < MINMAXX_MAX:
                        ARRAY_FLAG_FEATURES[3] = 1
                    if pcd_array_minmax[1] > MINMAXY_MIN and pcd_array_minmax[1] < MINMAXY_MAX:
                        ARRAY_FLAG_FEATURES[4] = 1
                    if pcd_array_minmax[2] > MINMAXZ_MIN and pcd_array_minmax[2] < MINMAXZ_MAX:
                        ARRAY_FLAG_FEATURES[5] = 1

                    # derive landmark point from features
                    sum_aff = np.sum(ARRAY_FLAG_FEATURES)
                    print(ARRAY_FLAG_FEATURES)
                    print()
                    if sum_aff == 6:
                        print("Landmark found", "Cluster",idx_4)
                        print(pcd_array_05)
                        print()
                        lm_color_cluster_idx = idx_4 # assign idx landmark cluster

                        # for eval
                        lm_cluster_list.append(pcd_array_05)
                        lm_cluster_mean_list.append(pcd_array_mean.tolist())
                        lm_cluster_median_list.append(pcd_array_median.tolist())
                        lm_cluster_idx_list.append(lm_color_cluster_idx)
            
            if DOUBLE_CLUSTERING:
                # apply intensity distance profile
                ###################################################################
                intensity = pcd_array_03
                xyaxis = pcd_array_04
                xyzaxis = pcd_array_02
                dist_list = [] # distance in polar coordinates (x,y)
                xyz_list = [] # coordinates (x,y,z)
                int_list = [] # intensity
                idx_list = [] # global indices for coloring pcd
                nums_list = [] # number of elements
                labels_list = [] # cluster labels
                ego_pos_list = [] # number of elements

                for idx6 in range(len(intensity_thres_list)):
                    # get temporarily values from intensity threshold
                    intensity_idx = np.where(intensity > intensity_thres_list[idx6])[0].tolist()
                    xyaxistmp = xyaxis[intensity_idx] 
                    xyzaxistmp = xyzaxis[intensity_idx]
                    intensitytmp = intensity[intensity_idx]
                
                    # check distance thresholds:
                    distances_polar = np.linalg.norm(xyaxistmp,axis=1)
                    # distances_spherical = np.linalg.norm(xyzaxistmp,axis=1)
                    # distances = distances_spherical
                    distances = distances_polar
                    # print("intensity_thres", intensity_thres_list[idx])
                    # print(distances_polar)
                    distances_idx = np.where(np.logical_and(distances > distances_thres_list[idx6], distances < distances_thres_list[idx6+1]))[0].tolist()
                    distances_polar_filtered = distances[distances_idx]
                    xyz_filtered = xyzaxistmp[distances_idx]
                    intensity_filtered = intensitytmp[distances_idx]
                    idx_filtered = np.asarray(intensity_idx)[distances_idx]

                    # distances_median = np.median(distances)
                    # dist_list.append(distances_median) 
                    if len(distances_polar_filtered) > 0:
                        dist_list.append(distances_polar_filtered) 
                        xyz_list.append(xyz_filtered) 
                        int_list.append(intensity_filtered) 
                        nums_list.append(len(distances_polar_filtered))
                        idx_list.append(idx_filtered)  
                    else: 
                        nums_list.append(len(distances_polar_filtered)) 
                        

                    # labels_list.append(labels)

                    # debugging: all lm candidates
                    # print(intensity_idx)
                    # print(intensitytmp)
                    # print(xyaxistmp)
                    # print(xyzaxistmp)
                    # print(distances_polar_filtered)
                    # print(xyz_filtered)
                    # print(intensity_filtered)
                    # print()
                    # print(distances_median)
                    # distances_mean = np.mean(distances)
                    # intensity_val = distances[intensity_val]

                print()
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print("\nFrame Num: " + str(cnt))
                print("distances_thres_list", distances_thres_list)
                print("intensity_thres_list", intensity_thres_list)
                # print(dist_list)
                # print(xyz_list)
                # print(idx_list)
                print("Num Pnts per thres:", nums_list)
                print()

                # when insensity features are found:  apply clustering
                ###############################################################
                if xyz_list != []:
                    dist_array = np.concatenate(dist_list, axis=0)
                    xyz_array = np.concatenate(xyz_list, axis=0)
                    idx_array = np.concatenate(idx_list, axis=0)
                    # print(dist_array)
                    # print(xyz_array)
                    # print(ego_pos_list)
                    
                    # apply first clustering (-1 are outliers!!)
                    ###############################################################
                    pcd02 = o3d.geometry.PointCloud()
                    pcd02.points = o3d.utility.Vector3dVector(xyz_array)
                    labels = np.array(pcd02.cluster_dbscan(
                    eps = MINDIST1, # min distance of cluster: in meter
                    min_points = MINPNTS1, # minimum number of pnts per cluster
                    ))
                    labels_max = np.max(labels)
                    lm_color_cluster_idx = -2 # init idx landmark cluster

                    # debugging
                    print(labels_max+1, "Landmark candidates")
                    print(labels)
                    # print("Landmark num pnts:", cluster_num_pnts)
                    print()

                    # apply hierachical clustering to each cluster: level 2
                    ###############################################################
                    for idx_4 in range(labels_max+1):
                        cluster_pnts_idx = np.where(labels== idx_4)[0].tolist() # get indices
                        # extract pnts
                        xyz_array_clustered = xyz_array[cluster_pnts_idx]
                        pcd03 = o3d.geometry.PointCloud()
                        pcd03.points = o3d.utility.Vector3dVector(xyz_array_clustered)
                        labels2 = np.array(pcd03.cluster_dbscan(
                        eps = MINDIST2, # min distance of cluster: in meter
                        min_points = MINPNTS2, # minimum number of pnts per cluster
                        ))
                        labels_max2 = np.max(labels2)

                        # debugging
                        print(labels2)
                        print()
                        if labels_max2 == 1: # we need to find exactly 2 cluster
                            nums2_list = []
                            median2_list = []
                            for idx_5 in range(labels_max2+1):
                                # get num points
                                cluster_pnts_idx2 = np.where(labels2== idx_5)[0].tolist() # get indices
                                nums2_list.append(len(cluster_pnts_idx2))

                                # calculate medians
                                xyz_array_clustered2 = xyz_array_clustered[cluster_pnts_idx2]
                                pnt_median = np.median(xyz_array_clustered2,axis=0) # median for each axis
                                median2_list.append(pnt_median)
                            
                            # final stats
                            diffmedianx = abs(median2_list[0][0] - median2_list[1][0])
                            diffmediany = abs(median2_list[0][1] - median2_list[1][1])
                            diffmedianz = abs(median2_list[0][2] - median2_list[1][2])
                            maxdiffmedianxy = max(diffmedianx, diffmediany)
                            final_pntx = min(median2_list[0][0],median2_list[1][0]) + diffmedianx/2
                            final_pnty = min(median2_list[0][1],median2_list[1][1]) + diffmediany/2
                            final_pntz = min(median2_list[0][2],median2_list[1][2]) + diffmedianz/2
                            final_pnt = np.array([final_pntx, final_pnty, final_pntz])
                            final_dist = np.linalg.norm(final_pnt)

                            # for eval
                            # final_frame_list.append(cnt)
                            # final_pnt_list.append(final_pnt.tolist())
                            # final_dist_list.append(final_dist.tolist())

                            if diffmedianz < 0.5 and maxdiffmedianxy > 0.4:
                                print("Landmark found Cluster:", idx_4)
                                print("Hierachy Clusters num:", nums2_list)
                                print("Hierachy Clusters medians:", median2_list)
                                print("FinalPoint:", final_pntx, final_pnty, final_pntz)
                                print("FinalDistance:", final_dist)
                                print()
                                lm_color_cluster_idx = idx_4 # init idx landmark cluster

                                # for eval
                                final_frame_list.append(cnt)
                                final_pnt_list.append(final_pnt.tolist())
                                final_dist_list.append(final_dist.tolist())
                                final_num_pnt_list.append(nums2_list[0]+nums2_list[1])
                                final_num_pntc1_list.append(nums2_list[0])
                                final_num_pntc2_list.append(nums2_list[1])
                                final_acc_list.append(len(final_pnt_list)/cnt)
                                candidate_list.append(labels_max+1)


                                # azimuth = azimuthAngle(0.0, 0.0, final_pntx, final_pnty) # (x1, y1, x2, y2)

                                # azimuth calculation
                                distance = math.sqrt((final_pntx-0.0)**2+(final_pnty-0.0)**2+(final_pntz -0.0)**2)
                                plunge = math.degrees(math.asin((final_pntz-0.0)/distance))
                                azimuth = math.degrees(math.atan2((final_pntx-0.0),(final_pnty-0.0)))

                                azimuth = azimuth + 270
                                if azimuth > 360:
                                    azimuth = azimuth - 360

                                final_pnt_azimuth_list.append(azimuth)
                                # final_pnt_elevation_list.append()
                       
                    # assign different colors to each cluster
                    ###############################################################
                    for idx3 in range(len(labels)):
                        if labels[idx3] > -1: # remove outliers
                            # assign different colors to each cluster
                            if labels[idx3] == lm_color_cluster_idx: # idx landmark cluster (red color)
                                # print("Landmark color" , lm_color_cluster_idx)
                                colors2[idx_array[idx3]] = tableau20[6]
                            else:
                                if labels[idx3]+7 > len(tableau20)-1: # prevent overflow from too many clusters
                                    colors2[idx_array[idx3]] = tableau20[0]
                                else:
                                    colors2[idx_array[idx3]] = tableau20[labels[idx3]+7]
                    lm_color_cluster_idx = -2 # reset idx landmark cluster

            # debugging:
            # # print(*lm_list, sep = "\n")
            # total_lm_list.append(lm_list)
            # a_pnts = np.asarray(lm_list)
            # total_lm_pnts_median.append(np.median(a_pnts, axis=0).tolist())
            # total_lm_idx_list.append(lm_idx_list)
            # total_lm_int_list.append(lm_int_list)
            # # total_lm_polar_dist = np.linalg.norm(pos_dif_vec)
            # # distances_polar = np.linalg.norm(xyaxistmp,axis=1)
            
            # assign final colors
            # # colors2 = [(0.6, 0.6, 0.6) for i in range(len(pcd_array_03))]
            pcd01.colors = o3d.utility.Vector3dVector(colors2)
    
            # final rendering of visualization
            ####################################################################################
            vis.add_geometry(pcd01) # env, for visualization only
            ctr =  vis.get_view_control()
            ctr.convert_from_pinhole_camera_parameters(params_liveview, allow_arbitrary=True)
            vis.poll_events()
            vis.update_renderer()

            # time.sleep(1)
        
        if EXPORT_EVAL:
            accuracy = len(final_pnt_list)/cnt
            dateTimeObj = datetime.now()
            timestampStr = dateTimeObj.strftime("_%d%b%Y_%H%M_") + str(accuracy)[0:4]
            path_ex = path_02 + name_02 + timestampStr + extension_02
            print()
            with open(path_ex, "w") as text_file:
                # create header
                # print("final_frame_list", final_frame_list)
                # print("final_pnt_list", final_pnt_list)
                # print("final_dist_list", final_dist_list)

                text_file.write(
                    "EVAL" + ";" +\
                    "\n" +\
                    "recframes" + ";" +\
                    str(len(final_pnt_list)) + ";" +\
                    "\n" +\
                    "totalframes" + ";" +\
                    str(cnt) + ";" +\
                    "\n" +\
                    "accuracy" + ";" +\
                    str(accuracy) + ";" +\
                    "\n\n" +\
                    "CALIBRATION" + ";" +\
                    "\n" +\
                    "cluster1" + ";" +\
                    "MinDistance" + ";" +\
                    str(MINDIST1) + ";" +\
                    "MinPoints" + ";" +\
                    str(MINPNTS1) + ";" +\
                    "\n" +\
                    "cluster2" + ";" +\
                    "MinDistance" + ";" +\
                    str(MINDIST2) + ";" +\
                    "MinPoints" + ";" +\
                    str(MINPNTS2) + ";" +\
                    "\n" +\
                    "intensity_thres" + ";" +\
                    str(intensity_thres_list) + ";" +\
                    "\n" +\
                    "distances_thres" + ";" +\
                    str(distances_thres_list) + ";" +\
                    "\n\n\n")
           
                text_file.write(
                    "frame" + ";" +\
                    "landmark_candidates" + ";" +\
                    "azimuth" + ";" +\
                    "x" + ";" +\
                    "y" + ";" +\
                    "z" + ";" +\
                    "distance" + ";" +\
                    "total_pnts" + ";" +\
                    "c1_pnts" + ";" +\
                    "c2_pnts" + ";" +\
                    "accuracy" + ";" +\
                    "\n")
            
                # create data: x,y,z
                for idx_2 in range(0,len(final_frame_list),1):
                    text_file.write(
                        str(final_frame_list[idx_2]) + ";" +\
                        str(candidate_list[idx_2]) + ";" +\
                        str(final_pnt_azimuth_list[idx_2]) + ";" +\
                        str(final_pnt_list[idx_2][0]) + ";" +\
                        str(final_pnt_list[idx_2][1]) + ";" +\
                        str(final_pnt_list[idx_2][2]) + ";" +\
                        str(final_dist_list[idx_2]) + ";" +\
                        str(final_num_pnt_list[idx_2]) + ";" +\
                        str(final_num_pntc1_list[idx_2]) + ";" +\
                        str(final_num_pntc2_list[idx_2]) + ";" +\
                        str(final_acc_list[idx_2]) + ";" +\
                        "\n")


        # global stats
        # print(total_lm_pnts_median)
        # print(*total_lm_list, sep = "\n")
        # print(total_lm_idx_list)

        # # print(lm_cluster_list)
        # print()
        # print(*lm_cluster_mean_list, sep = "\n")
        print(*lm_cluster_median_list, sep = "\n")
        print(len(lm_cluster_median_list))
        # print(lm_cluster_idx_list)
        # print("Total num cluster found", len(lm_cluster_idx_list))
        print()
        vis.run()
        
    finally:
        print()
        print("done")
        # print(min(list_polarmin))
        # print(max(list_polarmax))
        

if __name__ == '__main__':
    main()