#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ST-Twincat2-AutoMapping
Purpose: Load EXP Variablen di and do from exp file
Version: 01/2020 Roboball (MattK.)
"""
import os
import pandas as pd
# import xml.etree.ElementTree as ET
# from pprint import pprint

# define globals
project_name = "ZALA_BLEISWIJK_PLC01"
sheet_name = "pb01.csv"
plc_name = "DF-ZALBLE-PLC01"
path = "C:\\Users\KorfM\Desktop\Python\\project_DB_IO_EXP\\" + project_name + "\\Create_Objeclist\\"



def read_csv_files(path, sheet_name , num_files):
    ''' read_csv_files '''
    list_des = []
    list_pba = []
    # list_sla = []
    for idx_1 in range(num_files): 
        df = pd.read_csv(path + sheet_name[0:3]+ str(idx_1+1)+sheet_name[4:], skiprows = 1, header=None, na_values = ['no info', '.'], sep=';')
        print(df)
        print(df.keys())
        # print(len(df.index))
        list_des.append(df[1].tolist())
        list_pba.append(df[2].tolist())
        # list_sla.append(len(df.index))
    print("\nlist_des, " + ", len:", len(list_des))
    print(*list_des, sep = "\n")
    print("\nlist_pba, " + ", len:", len(list_pba))
    print(*list_pba, sep = "\n")
    # print("\nlist_sla, " + ", len:", len(list_sla))
    # print(*list_sla, sep = "\n")

    return list_des, list_pba


if __name__ == '__main__':

    ##########################################################
    # read in csv files: for pb slaves, adresses
    ##########################################################

    # get descriptions and pb addresses from csv files
    list_des,\
    list_pba = read_csv_files(path, sheet_name , 6)

    # split up description into uid, pb etc..
    list_uid_des = []
    for idx_1 in range(len(list_des)):
        list_temp = []
        for idx_2 in range(len(list_des[idx_1])):
            # list_temp = list_des[idx_1].split(',')
            list_temp.append([x.strip() for x in list_des[idx_1][idx_2].split(',')])
            # print(*list_temp, sep = "\n")
        list_uid_des.append(list_temp)

    print(*list_uid_des, sep = "\n")


  
