#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#==============================================================================================================================================
# Purpose: Ghost Mouse scripts fuer Notaus
# Version: 07/2019 Roboball
# Links: https://pythonhosted.org/pynput/mouse.html
# Scripts:
# (1) Bezeichnungen von Txt.file copy, paste into Notausboxen
# (2) TwinSAFE Verbindungsliste -> VTs: Watchdog 200ms + 4x Map State, Diag, Inputs, Outputs/ Conn-No = Conn-Id + copy Conn-Id for NotausExcel 
# (3) Outputs(Estops): Map State, Map Diag + 1500ms Delay + EDM 1 Aktiviert
# (4) Variables ANDs/Estops: Search in Verknuepfungen
#==============================================================================================================================================
'''
import sys
import time
from pynput.keyboard import Key, Listener
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

keyboard = KeyboardController()
mouse = MouseController()


# add path to import helper files
# define globals
project_name = "S_P_PLC02"
sys.path.append("C:\\Users\xDesktop\Python\\project_DB_IO_EXP\\" + project_name + "\\Create_Project_Mappings\\")
import _helper_globals_05 as hg
import _helper_functions_03 as hf
# import _helper_globals_notaus_02 as hn
import _helper_globals_notaus_03_bnotaus_50_falsch_fix as hn

# first record start position
# then playback
# finally hit save

# init wait
time.sleep(5) # Wait for secs
cnt_dp_obj = 0
UnitID_list_KF_PF = hg.UnitID_list_KF + hg.UnitID_list_PF

# define functionns
def on_press(key):
    # print('{0} pressed'.format(key))   
    if key == Key.enter: # Stop listener
        return False
    else:
        print("Hit Enter to finish the process")


def get_mouse_positions(
                        num_positions, 
                        wait_time
                        ):
    ''' get_mouse_positions'''
    return_list = []
    for idx_1 in range(0, num_positions):
        return_list.append(mouse.position)
        print("mouse.position = (" + str(mouse.position[0]) + " + x_offset, " + str(mouse.position[1]) + " + y_offset" + ")")
        time.sleep(wait_time) # Wait for 5 seconds
    return return_list



if __name__ == '__main__':

    ########################################################################
    # Get: Notausgroups for every ESTOP , EDM signal get DP Master address 
    ########################################################################

    # load: di do vars from TC_IMPORT_AT_VARIABLEN.EXP
    ##########################################################
    io_var, io_des, io_lks,\
    di_var, di_des, di_lks,\
    do_var, do_des, do_lks,\
    io_empty, di_empty, do_empty = hf.get_io_data( 
                                                hg.path_dido, # path
                                                hg.data_file_dido, # data_file
                                                )


    # # search: KNA1_OK // Warum funktioniert das nicht???? meine search fkt schein buggy zu sein!?
    # ###################################################################################
    # # KNA (Schuetze)
    # start_idx_uid = 5
    # content_list_uid_01,\
    # content_list_var_01,\
    # content_list_des_01,\
    # content_list_hpo_01,\
    # content_list_lks_01  = hf.search_by_depth_one_and_ret_lists(
    #                                                             "KNA",# search_str_01,  # e.g. Anomalie
    #                                                             "Pos",# search_str_02,  # e.g. Pos
    #                                                             di_var, # search_list_01, # content_list_idx
    #                                                             di_var, # io_var,
    #                                                             di_des, # search_list_02, # content_list_uid, hpo
    #                                                             di_lks, # io_lks,
    #                                                             start_idx_uid, # start_idx_uid,
    #                                                             start_idx_uid + 6, # end_idx_uid,
    #                                                             start_idx_uid, # start_idx_hpo,
    #                                                             start_idx_uid + 3, # end_idx_hpo,
    #                                                             True, # print_matrix_list
    #                                                             )
    
    # KF+PF + Steilförderer (CAN VTS)
    ###################################################################################
    # Rückführung Not-Halt 
    start_idx_uid = 5
    content_list_uid_02,\
    content_list_var_02,\
    content_list_des_02,\
    content_list_hpo_02,\
    content_list_lks_02  = hf.search_by_depth_one_and_ret_lists(
                                                                "Rückführung Not-Halt",# search_str_01,  # e.g. Anomalie
                                                                "Pos.",# search_str_02,  # e.g. Pos
                                                                di_des, # search_list_01, # content_list_idx
                                                                di_var, # io_var,
                                                                di_des, # search_list_02, # content_list_uid, hpo
                                                                di_lks, # io_lks,
                                                                start_idx_uid, # start_idx_uid,
                                                                start_idx_uid + 6, # end_idx_uid,
                                                                start_idx_uid, # start_idx_hpo,
                                                                start_idx_uid + 3, # end_idx_hpo,
                                                                True, # print_matrix_list
                                                                )
    
    # create Notausgroup index # KF, PF, SF(CAN)
    content_list_not_02 =  [0] * len(content_list_uid_02)
    for idx_1 in range(len(content_list_uid_02)):
        if content_list_uid_02[idx_1] in hg.UnitID_list_KF:
            content_list_not_02[idx_1] = 1  # KF
        elif content_list_uid_02[idx_1] in hg.UnitID_list_PF:
            content_list_not_02[idx_1] = 2  # PF
        else:
            content_list_not_02[idx_1] = 3 # SF (CAN)

    # BLPs
    ###################################################################################
    # Rückführung NOT-AUS Hauptschütz Beladeplatz 
    start_idx_uid = 17
    content_list_uid_03,\
    content_list_var_03,\
    content_list_des_03,\
    content_list_hpo_03,\
    content_list_lks_03  = hf.search_by_depth_one_and_ret_lists(
                                                                "Rückführung NOT-AUS Hauptschütz Beladeplatz Pos.",# search_str_01,  # e.g. Anomalie
                                                                "Beladeplatz",# search_str_02,  # e.g. Pos
                                                                di_des, # search_list_01, # content_list_idx
                                                                di_var, # io_var,
                                                                di_des, # search_list_02, # content_list_uid, hpo
                                                                di_lks, # io_lks,
                                                                start_idx_uid, # start_idx_uid,
                                                                start_idx_uid + 6, # end_idx_uid,
                                                                start_idx_uid, # start_idx_hpo,
                                                                start_idx_uid + 3, # end_idx_hpo,
                                                                True, # print_matrix_list
                                                                )
    # manually adjust, Error Ekonstruktion
    # content_list_uid_03[-1] = "805040"
    # content_list_hpo_03[-1] = "805"

    # create Notausgroup index
    content_list_not_03 = [4] * len(content_list_uid_03)
    

    # Extern (nur ANDs also nicht gebraucht im Notaus)
    ###################################################################################
    # Rückführung NOT-AUS-Modul
    start_idx_uid = 5
    content_list_uid_04,\
    content_list_var_04,\
    content_list_des_04,\
    content_list_hpo_04,\
    content_list_lks_04  = hf.search_by_depth_one_and_ret_lists(
                                                                "Rückführung NOT-AUS-Modul",# search_str_01,  # e.g. Anomalie
                                                                "Rückführung NOT-AUS-Modul",# search_str_02,  # e.g. Pos
                                                                di_des, # search_list_01, # content_list_idx
                                                                di_var, # io_var,
                                                                di_des, # search_list_02, # content_list_uid, hpo
                                                                di_lks, # io_lks,
                                                                start_idx_uid, # start_idx_uid,
                                                                start_idx_uid + 6, # end_idx_uid,
                                                                start_idx_uid, # start_idx_hpo,
                                                                start_idx_uid + 3, # end_idx_hpo,
                                                                True, # print_matrix_list
                                                                )
    # manually adjust, Error Ekonstruktion
    content_list_uid_04[0] = "ISS"
    content_list_hpo_04[0] = "ISS"

     # create Notausgroup index
    content_list_not_04 = [5] * len(content_list_uid_04)

    # for all: find DP Master
    ###################################################################################
    content_list_uid_05 = content_list_uid_02 + content_list_uid_03 + content_list_uid_04
    content_list_var_05 = content_list_var_02 + content_list_var_03 + content_list_var_04
    content_list_not_05 = content_list_not_02 + content_list_not_03 + content_list_not_04
    content_list_des_05 = content_list_des_02 + content_list_des_03 + content_list_des_04
    content_list_hpo_05 = content_list_hpo_02 + content_list_hpo_03 + content_list_hpo_04
    content_list_lks_05 = content_list_lks_02 + content_list_lks_03 + content_list_lks_04
    

    # DP Master and Addresses
    search_term_01 = '-DP'
    content_list_dps_05 = [x[x.index(search_term_01)+len(search_term_01):x.index(search_term_01)+len(search_term_01)+1] if search_term_01 in x else 'EL' for x in content_list_lks_05]
    print("\n"+"content_list_dps_05" + ", num:", len(content_list_dps_05))
    print(*content_list_dps_05 , sep = "\n")
    # search_term_02 = ':A'
    # content_list_adr_05 = [x[x.index(search_term_02)+len(search_term_02)-1:x.index(search_term_02)+len(search_term_02)+3] if search_term_01 in x else x for x in content_list_lks_05]
    # print("\n"+"content_list_adr_05" + ", num:", len(content_list_adr_05))
    # print(*content_list_adr_05 , sep = "\n")

    # print("\n"+"content_list_lks_05" + ", num:", len(content_list_lks_05))
    # print(*content_list_lks_05 , sep = "\n")

    # resort
    ###################################################################################
    multi_lists_sorted_01 = hf.sort_multi_lists_by_first_list(
                                                    content_list_not_05, # first_list 
                                                    [ 
                                                    content_list_uid_05,
                                                    content_list_var_05,
                                                    content_list_des_05,
                                                    content_list_dps_05,
                                                    # content_list_hpo_05,
                                                    # content_list_lks_05,       
                                                    ]# multi_list
                                                    )
    print("\nmulti_lists_sorted, "+ ", len:", len(content_list_uid_05))
    print(*multi_lists_sorted_01, sep = "\n")

    content_list_not_05 = [] # NotausKreis
    content_list_uid_05 = []
    content_list_var_05 = []
    content_list_des_05 = []
    content_list_dps_05 = [] # Profibus: DP Master
    # content_list_hpo_05 = []
    # content_list_lks_05 = []
    for idx in range(len(multi_lists_sorted_01)):
        content_list_not_05.append(multi_lists_sorted_01[idx][0])
        content_list_uid_05.append(multi_lists_sorted_01[idx][1])
        content_list_var_05.append(multi_lists_sorted_01[idx][2])
        content_list_des_05.append(multi_lists_sorted_01[idx][3])
        content_list_dps_05.append(multi_lists_sorted_01[idx][4])
        # content_list_hpo_05.append(multi_lists_sorted_01[idx][5])
        # content_list_lks_05.append(multi_lists_sorted_01[idx][6])
        
    #########################################################
    # for playback: mapstate, diag, inputs, outputs
    #########################################################

    # Such Einstellungen: Alle und Alle Typen, sonst alle Haeckchen entfernen!!

    # Monitor Einstellungen:
    # full screen, left Monitor: 1920 x 1080, 24 Zoll
    # fuer x_offset, Null Reference: Trennwand ziwschen: ++++ | Toggelt Lagersicht 
    x_offset = 0 # Null Reference
    y_offset = 0 # Null Reference

    ###################################################
    # do for every output group by: idx_unter_group_estops 

    # globals
    idx_unter_group_estops = 4 #  entspricht: , Z.b. 1 = KF Outputs, 2 = PF Outputs, 3 = CAN, 4 = BLPs, 5 = EXterne Outputs
    # set_notausgruppe = 7
    playback_speed = 0.5
    dif_val_01 = 18 # difference to next click

    
    # # get: anzahl estops/ands pro output fb gruppe main notaus group, fbgroup, type, uid, var, vt, des, baustein, bnotausOK, output AND, input ANDs 
    # print("\nnum_fbs_gruppe, "+ ", len:", len(hn.num_fbs_gruppe))
    # print(*hn.num_fbs_gruppe, sep = "\n")

    # print("\nhnum_and_gruppe, "+ ", len:", len(hn.num_and_gruppe))
    # print(*hn.num_and_gruppe, sep = "\n")
    # print()

    # project specific in menue how many arrow keys down !!, 
    # Abstand zwischen Gruppen: +4
    # Gruppe 1 = 2
    # Gruppe 2 = 6
    # Gruppe 3 = 10
    # Gruppe 4 = 14
    list_cnt_bRESET_NOT_AUS_EL6900 = [ 
        14, # gruppe 4, KF
        14, # gruppe 4, PF
        18, # gruppe 5, CAN
        22, # gruppe 6, BLPs
        26, # gruppe 7
    ]

  
    ########################################################
    # get data per notaus Untergruppe for: 
    #  bNotAusKreis_OK_EL 
    #  Output ANDs
    ########################################################
    list_bNotAusKreis_OK_EL = []
    list_Output_Ands = []
    list_EDM1_KNA_OK = []
    list_EDM1_KNA_OK_DP_Master = []
    list_EstopDelOut_KNA_VT = []

    for idx_1 in range(len(content_list_not_05)):
        if content_list_not_05[idx_1] == idx_unter_group_estops:
            list_EDM1_KNA_OK_DP_Master.append(content_list_dps_05[idx_1])

    for idx_1 in range(len(hn.notaus_fbs_list)):
        if hn.notaus_fbs_list[idx_1][1] == idx_unter_group_estops:
            list_bNotAusKreis_OK_EL.append(hn.notaus_fbs_list[idx_1][8])
            list_Output_Ands.append(hn.notaus_fbs_list[idx_1][9])
            list_EDM1_KNA_OK.append(hn.notaus_fbs_list[idx_1][4][1:]+"_OK")
            list_EstopDelOut_KNA_VT.append(hn.notaus_fbs_list[idx_1][4])
    # print("\nlist_bNotAusKreis_OK_EL, "+ ", len:", len(list_bNotAusKreis_OK_EL))
    # print(list_bNotAusKreis_OK_EL)
    # print("\nlist_Output_Ands, "+ ", len:", len(list_Output_Ands))
    # print(list_Output_Ands)
    # print("\nlist_EDM1_KNA_OK + DP Master, "+ ", len:", len(list_EDM1_KNA_OK))
    # print(list_EDM1_KNA_OK)
    # print( list_EDM1_KNA_OK_DP_Master)
    # print("\nlist_Output_Ands, "+ ", len:", len(list_Output_Ands))
    # print(list_EstopDelOut_KNA_VT)

    print("\n" + "bNotAusKreis_OK_EL, Output_Ands, EDM1_KNA_OK, "+\
              "EDM1_KNA_OK_DP_Master, EstopDelOut_KNA_VT"+ ", len:", len(list_bNotAusKreis_OK_EL))
    for a,b,c,d,e in zip(
                    list_bNotAusKreis_OK_EL,\
                    list_Output_Ands,\
                    list_EDM1_KNA_OK,\
                    list_EDM1_KNA_OK_DP_Master,\
                    list_EstopDelOut_KNA_VT,\
                    ):
        # print (w,x,y,z, end='\n') 
        print ('{:<5}{:<5}{:<20}{:<5}{:<}'.format(a,b,c,d,e))
    print()

    cnt_bRESET_NOT_AUS_EL6900 = list_cnt_bRESET_NOT_AUS_EL6900[idx_unter_group_estops-1]
    num_objects =  hn.num_fbs_gruppe[2][idx_unter_group_estops-1] #  how many estops
    # num_objects = 1 # set manual for how many objects
    print("num_objects: ", num_objects)

    ########################################################
    # Optional: debugging
    ########################################################
    # return_list = get_mouse_positions(
    #                     10, # num_positions, 
    #                     5, # wait_time 
    #                     )

    ########################################################
    # for recording
    ########################################################
    cnt_val_01 = mouse.position[1] # set start value
    # print('\n' + 'mouse.position = {0}'.format(mouse.position))
    time.sleep(5.2) # Wait for 5 seconds

    #########################################################
    # settings for Desktop:
    # set vertical bar between crosses(left), and sheet (right)
    # set mouse on first FB-Estop Output: eg. KF1
   
    for idx_1 in range(0, num_objects): 
        # print(idx_1+1, ", ", cnt_val_01)

        # open vts
        mouse.position = (-1690, cnt_val_01)
        cnt_val_01 += dif_val_01
        time.sleep(playback_speed) # Wait for secs
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs

        if idx_1 == 0: # do only, during first loop 
            mouse.position = (-1232 + x_offset, 84 + y_offset)
            mouse.click(Button.left, 1)
            time.sleep(playback_speed) # Wait for secs

        #########################################################
        # run main action 
        #########################################################

        #########################################################
        # check: map state, map diag 
        mouse.position = (-630 + x_offset, 126 + y_offset)
        mouse.click(Button.left, 1) 
        # time.sleep(playback_speed) # Wait for secs
        mouse.position = (-630 + x_offset, 143 + y_offset)
        mouse.click(Button.left, 1)  
        time.sleep(playback_speed) # Wait for secs

        ########################################################
        # activate EDM1
        mouse.position = (-1040 + x_offset, 490 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs 

        ########################################################
        # increase Verzoergerungszeit: 1500ms
        mouse.position = (-888 + x_offset, 535 + y_offset)
        mouse.click(Button.left, 140) 
        time.sleep(playback_speed) # Wait for secs

        # ########################################################
        # # optional: decrease Verzoergerungszeit: 1500ms
        # mouse.position = (-888 + x_offset, 543 + y_offset)
        # mouse.click(Button.left, 140) 
        # time.sleep(playback_speed) # Wait for secs

        ########################################################
        # check: EstopIn1 (inputs)
        mouse.position = (-1084 + x_offset, 230 + y_offset)
        mouse.click(Button.left, 1) 
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-1111 + x_offset, 499 + y_offset)
        mouse.click(Button.left, 1) 
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-1080 + x_offset, 520 + y_offset)
        mouse.click(Button.left, 1) 
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-902 + x_offset, 620 + y_offset) 
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs

        ##################################################################################################################

        #########################################################
        # bRESET_NOT_AUS_EL6900.ST_Output_Not_Aus_Gruppe_7
        # Restart: Standard Input 
        # (rote VAR, erst Notausmatrix fertig Exportieren -> importieren in Projekt -> und TSM neu eingelesen von Project .tpy file)
        mouse.position = (-1150 + x_offset, 150 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-1174 + x_offset, 679 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-953 + x_offset, 694 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(8.0) # Wait for secs, extra delay weil TSM zu langsam laedt!!

        # scroll: reset to start position, x
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-1233 + x_offset, 713 + y_offset)
        mouse.click(Button.right, 1)
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-1205 + x_offset, 756 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs

        # scroll: reset to start position, y
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-852 + x_offset, 351 + y_offset)
        mouse.click(Button.right, 1)
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-827 + x_offset, 388 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs

        mouse.position = (-1164 + x_offset, 362 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs
        keyboard.type('br')
        time.sleep(playback_speed) # Wait for secs

        # set specific location:
        for idx_2 in range(0,cnt_bRESET_NOT_AUS_EL6900):
            # keyboard.type('br')
            keyboard.press(Key.down)
            keyboard.release(Key.down)
            time.sleep(playback_speed) # Wait for secs
      
        # final ok, and close
        mouse.position = (-724 + x_offset, 709 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-771 + x_offset, 711 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs


        #########################################################
        # bNotAusKreis_OK_EL[1][39]
        # kommen aus der NotausMatrix: Ausgangsklemmen, Zeilenweise hochgezaehlt
        # EstopOUT: Standard Output 
        # (gelbe VAR, erst Notausmatrix fertig Exportieren -> importieren in Projekt -> und TSM neu eingelesen von Project .tpy file)
        mouse.position = (-818 + x_offset, 460 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-1178 + x_offset, 677 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-959 + x_offset, 697 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(10.0) # Wait for secs

        # scroll: reset to start position, x
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-1233 + x_offset, 713 + y_offset)
        mouse.click(Button.right, 1)
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-1205 + x_offset, 756 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs

        # scroll: reset to start position, y
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-847 + x_offset, 344 + y_offset)
        mouse.click(Button.right, 1)
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-789 + x_offset, 388 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs

        mouse.position = (-1164 + x_offset, 362 + y_offset)
        mouse.click(Button.left, 1)
        keyboard.type('bn')
        time.sleep(playback_speed) # Wait for secs

        # set specific location:
        for idx_2 in range(0,list_bNotAusKreis_OK_EL[idx_1]):
            # keyboard.type('b')
            keyboard.press(Key.down)
            keyboard.release(Key.down)
            time.sleep(playback_speed) # Wait for secs

        # final ok, and close
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-719 + x_offset, 713 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-783 + x_offset, 713 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs

        # list_bNotAusKreis_OK_EL_old = list_bNotAusKreis_OK_EL[idx_1]
        time.sleep(playback_speed) # Wait for secs
   
        #########################################################
        # 20101_AVT_KNA1_OK
        # EDM1: Standard Input 
        # Zeige Variablen: alle, und alle Typen (sonst keine Haeckchen setzen!!!)
        # (gelbe VAR, erst Notausmatrix fertig Exportieren -> importieren in Projekt -> und TSM neu eingelesen von Project .tpy file)
        # find via PB, :A.1;KL1408, Kanal2 = KNA1_OK, Kanal3 =KNA2_OK
        # nur umzusehen im TSM: alternative find EthercatBox (master) -> EL31,DP-Master -> VT (gelbe inputs)-> Kanal 2.011 / Kanal 3.011

        # apply to 'EDM signal 
        ###################################################################################
        mouse.position = (-1138 + x_offset, 488 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-1176 + x_offset, 681 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-960 + x_offset, 694 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(8.0) # Wait for secs

        # scroll: reset to start position, x
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-1233 + x_offset, 713 + y_offset)
        mouse.click(Button.right, 1)
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-1205 + x_offset, 756 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs

        # scroll: reset to start position, y
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-852 + x_offset, 351 + y_offset)
        mouse.click(Button.right, 1)
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-827 + x_offset, 388 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs

        cnt_diff_01 = 0
        cnt_diff_02 = 0
        if list_EDM1_KNA_OK_DP_Master[idx_1] != "EL":
            for idx_2 in range(0,9 + int(list_EDM1_KNA_OK_DP_Master[idx_1])-1):
                mouse.position = (-1188 + x_offset, 380 + y_offset + cnt_diff_01)
                mouse.click(Button.left, 1)
                time.sleep(playback_speed) # Wait for secs
                cnt_diff_01 += 16 
            print('\n' + "find value, click left and hit enter:")
            print(
                str(idx_1+1) + "  ",\
                list_EDM1_KNA_OK[idx_1],\
                "  DP Master:",\
                list_EDM1_KNA_OK_DP_Master[idx_1],\
                "       Check Estop Rest:",\
                " Output_Ands:",\
                list_Output_Ands[idx_1],\
                " bNotAusKreis_OK_EL:",\
                list_bNotAusKreis_OK_EL[idx_1],\
                # " bRESET_NOT_AUS_EL6900:",\
                # str(cnt_bRESET_NOT_AUS_EL6900),\
                )
        elif list_EDM1_KNA_OK_DP_Master[idx_1] == "EL":
            for idx_2 in range(0,8):
                mouse.position = (-1188 + x_offset, 380 + y_offset + cnt_diff_01)
                mouse.click(Button.left, 1)
                time.sleep(playback_speed) # Wait for secs
                cnt_diff_01 += 16 
            for idx_2 in range(0,7):
                mouse.position = (-1170 + x_offset, 526 + y_offset + cnt_diff_02)
                mouse.click(Button.left, 1)
                time.sleep(playback_speed) # Wait for secs
                cnt_diff_02 += 16 
            print('\n' + "find value, click left, and hit enter:")
            print(
                str(idx_1+1) + "  ",\
                list_EDM1_KNA_OK[idx_1],\
                "  EL Master:",\
                list_EDM1_KNA_OK_DP_Master[idx_1],\
                "       Check Estop Rest:",\
                " Output_Ands:",\
                list_Output_Ands[idx_1],\
                " bNotAusKreis_OK_EL:",\
                list_bNotAusKreis_OK_EL[idx_1],\
                # " bRESET_NOT_AUS_EL6900:",\
                # str(cnt_bRESET_NOT_AUS_EL6900),\
                )
        
        # wait for keyboard input: Hit Enter  (blocking main thread)
        with Listener(
                    on_press=on_press,
                    ) as listener:
                    listener.join()
        
        # final ok, and close
        time.sleep(playback_speed) # Wait for secs
        mouse.position = (-771 + x_offset, 711 + y_offset)
        mouse.click(Button.left, 1)
        time.sleep(playback_speed) # Wait for secs


        # #########################################################
        # # Optional Project Special:
        # # EstopIn1: ZALBLE, Input AND Group 3
        # mouse.position = (-1145 + x_offset, 212 + y_offset)
        # mouse.click(Button.left, 1)
        # time.sleep(playback_speed) # Wait for secs
        # mouse.position = (-1176 + x_offset, 657 + y_offset)
        # mouse.click(Button.left, 1)
        # time.sleep(playback_speed) # Wait for secs
        # mouse.position = (-960 + x_offset, 696 + y_offset)
        # mouse.click(Button.left, 1)
        # time.sleep(playback_speed) # Wait for secs

        # # scroll: reset to start position, x
        # time.sleep(playback_speed) # Wait for secs
        # mouse.position = (-1196 + x_offset, 669 + y_offset)
        # mouse.click(Button.right, 1)
        # time.sleep(playback_speed) # Wait for secs
        # mouse.position = (-1161 + x_offset, 713 + y_offset)
        # mouse.click(Button.left, 1)
        # time.sleep(playback_speed) # Wait for secs

        # # scroll: reset to start position, y
        # time.sleep(playback_speed) # Wait for secs
        # mouse.position = (-836 + x_offset, 387 + y_offset)
        # mouse.click(Button.right, 1)
        # time.sleep(playback_speed) # Wait for secs
        # mouse.position = (-791 + x_offset, 430 + y_offset)
        # mouse.click(Button.left, 1)
        # time.sleep(playback_speed) # Wait for secs

        # # set specific location: DecouplerGroup 4
        # cnt_diff_03 = 0
        # for idx_2 in range(0,3):
        #         mouse.position = (-1193 + x_offset, 385 + y_offset + cnt_diff_03)
        #         mouse.click(Button.left, 1)
        #         time.sleep(playback_speed) # Wait for secs
        #         cnt_diff_03 += 16 
        # mouse.position = (-1170 + x_offset, 385 + y_offset + cnt_diff_03)
        # mouse.click(Button.left, 1)
        # time.sleep(playback_speed) # Wait for secs

        # # set number of down typing
        # if list_Output_Ands[idx_1] == 3:
        #     num_a_down = 11
        # elif list_Output_Ands[idx_1] == 9:
        #     num_a_down = 16 
        # elif list_Output_Ands[idx_1] == 1:
        #     num_a_down = 19 + list_Output_Ands[idx_1]
        # elif list_Output_Ands[idx_1] == 2:
        #     num_a_down = 19 + list_Output_Ands[idx_1]
        # elif list_Output_Ands[idx_1] == 10:
        #     num_a_down = 17 + list_Output_Ands[idx_1]
        # elif list_Output_Ands[idx_1] == 11:
        #     num_a_down = 17 + list_Output_Ands[idx_1]
        # else:
        #     num_a_down = 18 + list_Output_Ands[idx_1]


        # for idx_2 in range(0,num_a_down):
        #     keyboard.type('a')
        #     # time.sleep(playback_speed) # Wait for secs

        # # final ok, and close
        # mouse.position = (-771 + x_offset, 390 + y_offset) 
        # mouse.click(Button.left, 1)
        # time.sleep(playback_speed) # Wait for secs
        # mouse.position = (-778 + x_offset, 713 + y_offset)
        # mouse.click(Button.left, 1)
        # time.sleep(playback_speed) # Wait for secs

               
    # #########################################################
    # # hit save button
    # #########################################################
    # time.sleep(playback_speed) # Wait for secs
    # mouse.position = (-1831 + x_offset, 51 + y_offset)
    # time.sleep(0.5) # Wait for secs
    # mouse.press(Button.left)
    # mouse.release(Button.left) 