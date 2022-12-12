#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Purpose: Correlations on Death data by destatis
Date: 01/2021
Version: V01

pip install xlrd==1.2.0


Links: https://realpython.com/numpy-scipy-pandas-correlation-python/#example-scipy-correlation-calculation
       https://stackoverflow.com/questions/24432101/correlation-coefficients-and-p-values-for-all-pairs-of-rows-of-a-matrix
       https://stackoverflow.com/questions/42734109/two-or-more-graphs-in-one-plot-with-different-x-axis-and-y-axis-scales-in-pyth
"""
import numpy as np
import requests
import xlrd
import datetime
# import isoweek
import matplotlib as plt2
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.signal import savgol_filter

# import dependencies (globals and functions)
import _globals_deaths_destatis_02 as hg
import _functions_deaths_destatis_01 as hf

sheet_name_01 = "sonderauswertung-sterbefaelle.xlsx"
sheet_name_01 = "sonderauswertung-sterbefaelle_160321_01.xlsx"
sheet_name_02 = "14_bevoelkerungsvorausberechnung_daten.xlsx"
username = "X"
path_01 = "C:\\Users\\" + username + "\\Desktop\\backup_Acer2021_12\covid\\" # win 10
path_02 = "C:\\Users\\" + username + "\\Desktop\\backup_Acer2021_12\covid\plt_figs\\" # win 10

name_02 = "prediction_all_age_groups_2021"
vers_02 = "01"
# web download
link_01 = "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Sterbefaelle-Lebenserwartung/Tabellen/sonderauswertung-sterbefaelle.xlsx;jsessionid=3BA260E648E8A398F2B64AE383EF1E2E.live721?__blob=publicationFile"
spreadsheet_new_name_01 = 'sonderauswertung-sterbefaelle_web.xlsx'

##################################################################################################
# Activate options:

# language prefs: default is English
lang_ge = False # German
lang_ge = True # German

# export fig as jpg
plt_save_im = False
plt_save_im = True

web_download = False
web_download = True

# plot original data:
plot_signals_01 = False
plot_signals_01 = True

# plot random numbers:
plot_random_number_1yr = False
# plot_random_number_1yr = True

plot_random_number_3yr = False
# plot_random_number_3yr = True

# plot smoothing filter:
plot_smooth_filter_01 = False
# plot_smooth_filter_01 = True

# filter settings
filter_size_01 = 53 # odd number
poly_order_01 = 3

# plot linear trends:
plot_1yr_linear_trends = False
# plot_1yr_linear_trends = True

plot_2yr_linear_trends = False
# plot_2yr_linear_trends = True

plot_3yr_linear_trends = False
# plot_3yr_linear_trends = True

plot_4yr_linear_trends = False
# plot_4yr_linear_trends = True

plot_5yr_linear_trends = False
plot_5yr_linear_trends = True

linear_offset = 0 # original linear trend

# RKI offsets
# linear_offset = 1910 # OLd RKI sinus method, WS17/18: 25.100 Tote set to: 1910  seite: 48, https://influenza.rki.de/Saisonberichte/2018.pdf
# linear_offset = 550 # PCR Corona Tote: 1welle (RKI bis CW 24: ca. 9000 Tote), bis CW10-CW20: 8000 Tote
# linear_offset = -430 # PCR Corona Tote: 2welle (RKI bis CW 15: ca. 73000 Tote)

# Hmd offsets

# Bottom-Level Wave Estimators
# linear_offset = -2370 # 5Y (16-20) Yearly Low Qtil Week
# linear_offset = -1120 # 5Y (16-20) Summer Avg Week

# Mid-Level Wave Estimators
# linear_offset =  # 5Y (16-20) Week Specific Low Qtil
# linear_offset =  # 5Y (16-20) Yearly Avg Week

# Top-Level Wave Estimators

# add predictions
plot_predictions_lin_3_yrs_roll_annual = False
# plot_predictions_lin_3_yrs_roll_annual = True

plot_predictions_lin_3_yrs_roll_season = False
plot_predictions_lin_3_yrs_roll_season = True

# add Top5
add_top5 = False
add_top5 = True

# add seasonal vertical grid (winter season: cw40-cw20)
add_seasonal_grid = False
# add_seasonal_grid = True

# seasonal deaths: excess deaths baselines
plot_table_excess_death_lin5y = False
plot_table_excess_death_lin5y = True

plot_table_excess_death_total_ws = False
# plot_table_excess_death_total_ws = True

plot_table_excess_death_smooth = False
# plot_table_excess_death_smooth = True

# which data to calculate:
srt_plot_idx = 0
end_plot_idx = 15
step_plot_idx = 1

# which data to plot:
age_groups_plot = [
            0, # "00-29"
            1, # "00-34"
            0, # "00-39"
            1, # "00-44"
            0, # "00-49"
            1, # "00-54"
            0, # "00-59"
            1, # "00-64"
            0, # "00-69"
            1, # "00-74"
            0, # "00-79"
            1, # "00-84"
            0, # "00-89"
            0, # "00-94"
            1, # "00-95+"
            ]

# which options are activated (for num option labels):
option_labels = [
            plot_random_number_1yr,
            plot_random_number_3yr,
            plot_smooth_filter_01,
            plot_1yr_linear_trends,
            plot_2yr_linear_trends,
            plot_3yr_linear_trends,
            plot_4yr_linear_trends,
            plot_5yr_linear_trends,
            ]


if __name__ == '__main__':
    ##################################################################################################
    # read in excel sheets (by XLRD)
    if web_download: # download from the web
        spreadsheet = path_01 + spreadsheet_new_name_01
        resp = requests.get(link_01, allow_redirects=True)
        with open( path_01 + spreadsheet_new_name_01, 'wb') as output:
            output.write(resp.content)
        print(spreadsheet_new_name_01 + " Downloaded from web and Saved!")
    else: # local opening
        spreadsheet = path_01 + spreadsheet_new_name_01

    book = xlrd.open_workbook(
                            spreadsheet, 
                            on_demand=True, 
                            encoding_override = "utf-8"
                            )
    sheet_list = book.sheet_names()
    print("\nsheet_list" + ", len:", len(sheet_list))
    print(*sheet_list, sep = "\n")

    # read in data from sheets
    sheet_01 = book.sheet_by_index(4) # D_2016_2020_KW_AG_Ins
    sheet_02 = book.sheet_by_index(7) # D_2016-2020_Monate_AG_Ins

    ##################################################################################################
    # import data: yearly cw data, deaths by age groups
    set_srt_col = 4
    set_end_col = 57
    num_cols = set_end_col - set_srt_col # cw weeks
    list_of_array_yr = []
    for idx_1 in range(0,len(hg.annual_header21),1):
        cnt_year = idx_1 * len(hg.age_groups)
        list_yr = []
        for idx_2 in range(0,len(hg.age_groups),1):
            list_01 = hf.get_row_from_sheet_by_xlrd(
                                        sheet_01, # sheet_object
                                        10 + cnt_year + idx_2, # set_row, like excel
                                        set_srt_col, # set_col, e.g. J=10
                                        1, # step_size
                                        set_end_col, # set_manual_rows
                                        False, # print_opt val
                                        False, # print_opt type
                                        )
            list_temp_01 = []
            for i in list_01:
                try:
                    list_temp_01.append(int(i))
                except:
                    pass # add only none zero values
                    # list_temp.append(int(0)) # zero padding
            list_yr.append(list_temp_01)

        # transform list_yr into numpy array
        array_yr = np.zeros(shape=(len(hg.age_groups),len(list_temp_01))).astype(int)
        for idx_1 in range(0,len(list_yr),1):
            array_yr[idx_1,:] = np.array(list_yr[idx_1])
        list_of_array_yr.append(array_yr)
    
    list_yr_rev = list(reversed(list_of_array_yr)) # 2016-2021
    x_cws_in_yrs_list = []
    x_cws_in_srt_list = []
    x_cws_in_end_list = []
    cnt_cws_srt = 0
    cnt_cws_end = 0
    for idx_1 in range(0,len(list_yr_rev),1):
        cnt_cws_end += len(list_yr_rev[idx_1][0])
        cnt_cws_srt = cnt_cws_end - len(list_yr_rev[idx_1][0][1:]) 
        x_cws_in_yrs_list.append(len(list_yr_rev[idx_1][0]))
        x_cws_in_srt_list.append(cnt_cws_srt)
        x_cws_in_end_list.append(cnt_cws_end)  
    print("\nCWS per year:")
    print(list(reversed(hg.annual_header21)))
    print(x_cws_in_yrs_list)
    print(x_cws_in_srt_list)
    print(x_cws_in_end_list)

    # optional: print all years: cw data
    # print("\nall years: cw data")
    # print("Years: " , hg.annual_header21, ", len:", len(list_of_array_yr))
    # print("Age Groups: " , hg.age_groups[1:], ", len:", len(hg.age_groups[1:]))
    # print(*list_of_array_yr, sep = "\n")

    iso_date = hf.from_iso_cw_week_to_date(int(hg.annual_header21[0]), len(list_of_array_yr[0][0]))
    print(iso_date)
    if web_download: # download from the web
        with open( path_01 + spreadsheet_new_name_01[0:-5] + "_21cw" + str(len(list_of_array_yr[0][0])) + ".xlsx" , 'wb') as output:
                output.write(resp.content)

    ##################################################################################################
    # visualisation with matplotlib 
    ##################################################################################################

    ##################################################################################################
    # fig: annual cw data, deaths by age groups
    # style total layout with size in lists for each plot
    widths = [1,]
    heights = [4.0,0.2,0.2]
    # gs_kw = dict(width_ratios=widths, height_ratios=heights)
    # gs_kw = dict(wspace=1.0, hspace=0.8)
    gs_kw = dict(wspace=1.0, hspace=0.6, width_ratios=widths, height_ratios=heights)
    # gs_kw = dict()
    fig1, ax1 = plt.subplots(nrows=len(heights), ncols=len(widths), figsize=(8, 8), gridspec_kw=gs_kw,) # subplot_kw=, constrained_layout=True


    # do not show plot
    # ax1[0].axis('off')
    # ax1[0].axis('tight')

    ##################################################################################################
    # create list of lists with arrays for all age groups
    list_of_list_yrs_age_groups_stacked = [] 
    list_of_list_yrs_age_groups_not_stacked = []
    for idx_1 in range(1,len(hg.age_groups[1:])+1,1):
        list_of_list_yrs_age_groups_stacked.append(np.empty(shape=[0], dtype=int))
        list_of_list_yrs_age_groups_not_stacked.append(np.empty(shape=[0], dtype=int))

    for idx_1 in range(len(hg.annual_header21)-1,0-1,-1): # reverse 2016-2021
        for idx_2 in range(1,len(hg.age_groups[1:])+1,1): # do for all age-groups (without total)
            
            # classification: age groups, for stacked plots
            list_tmp_01 = []
            for idx_3 in range(1,idx_2+1,1):
                list_tmp_01.append(list_of_array_yr[idx_1][idx_3])
            # sum-up vertically, and append horizontally annual data
            list_of_list_yrs_age_groups_stacked[idx_2-1] = np.append(list_of_list_yrs_age_groups_stacked[idx_2-1],\
                 np.sum(np.array(list_tmp_01), axis = 0), axis = 0)
                
            # append  horizontally annual data
            list_of_list_yrs_age_groups_not_stacked[idx_2-1] = np.append(list_of_list_yrs_age_groups_not_stacked[idx_2-1],\
                list_of_array_yr[idx_1][idx_2], axis = 0)
    
    # optional: print all years: cw data
    # print("\nStacked sums: All-Yrs, len total:", len(list_of_list_yrs_age_groups_stacked[0]), len(list_of_list_yrs_age_groups_not_stacked[0]))
    # print("Years: " , list(reversed(hg.annual_header21)))
    # print("Age Groups: " , hg.age_groups[1:], ", len:", len(list_of_list_yrs_age_groups_not_stacked))
    print(*list_of_list_yrs_age_groups_stacked, sep = "\n")
    # print(*list_of_list_yrs_age_groups_not_stacked, sep = "\n")
    
    # stacked:
    ##################################################################################################      
    # get linear trend per age group: all years
    list_min_max = []
    list_lin_trend_all_years = []
    srt_num_cws = 0 # set start cw for data science
    end_num_cws = 4*52+53 # set end cw for data science
    for idx_1 in range(srt_plot_idx,end_plot_idx,step_plot_idx):
        # get min/max per age group:
        mini = min(list_of_list_yrs_age_groups_stacked[idx_1][srt_num_cws:end_num_cws])
        maxi = max(list_of_list_yrs_age_groups_stacked[idx_1][srt_num_cws:end_num_cws])
        list_min_max.append([mini,maxi])
        # print("Min/Max:",mini,maxi)

        # get linear trend per age group: all years
        x = np.arange(0,len(list_of_list_yrs_age_groups_stacked[idx_1][srt_num_cws:end_num_cws]))
        y = list_of_list_yrs_age_groups_stacked[idx_1][srt_num_cws:end_num_cws]
        z = np.polyfit(x,y,1)
        # print("Linear Trends:")
        # print("{0}x + {1}".format(*z))
        list_lin_trend_all_years.append(z)
    
   
    # non-stacked:
    ##################################################################################################  
    # get linear trend per age group: annually
    list_lin_trend_annually = []
    list_x_len = []
    srt_cws = 1
    end_cws = len(list_of_array_yr[-1][0])+1 
    for idx_1 in range(len(hg.annual_header21)-1,0-1,-1): # reverse 2016-2021
        list_lin_trend_temp = []
        list_x_len.append(len(list_of_array_yr[idx_1][0])+1)
        for idx_2 in range(1,len(hg.age_groups[1:])+1,1): # do for all age-groups (without total)
            # non stacked
            x = np.arange(srt_cws, end_cws, 1) # cws
            y = list_of_array_yr[idx_1][idx_2]
            # print(x, len(x), len(y))
            z = np.polyfit(x,y,1)
            # print("Linear Trends: annually")
            # print("{0}x + {1}".format(*z))
            list_lin_trend_temp.append(z)
            
        list_lin_trend_annually.append(list_lin_trend_temp)
        srt_cws = end_cws
        try:
            end_cws = end_cws + len(list_of_array_yr[idx_1-1][0])
        except:
            pass
    
    # optional: print all years: Linear Trends: annually
    # print("\nall years: Linear Trends: annually")
    # print("Years: " , list(reversed(hg.annual_header21)), ", len:", len(list_lin_trend_annually))
    # print("Age Groups: " , hg.age_groups[1:], ", len:", len(hg.age_groups[1:]))
    # print(*list_lin_trend_annually, sep = "\n")

    # non-stacked:
    #################################################################################################  
    # get linear trend per age group: 3 years
    list_lin_trend_02 = []
    list_lin_trend_03 = []
    list_min_03 = []
    list_max_03 = []
    list_x_len_02 = []
    list_x_len_03 = []
    list_y_len_02 = [] # not-stacked
    list_y_len_03 = [] # stacked
    # 3yrs rolling
    srt_cws_list = [52*0,52*1,52*2]
    end_cws_list = [52*3,52*4,52*5+1]

    for idx_1 in range(0,len(srt_cws_list),1):
        list_lin_trend_temp = []
        list_lin_trend_temp_z_stacked = []
        list_lin_trend_temp_y_stacked = []
        srt_cws = srt_cws_list[idx_1]
        end_cws = end_cws_list[idx_1]
        x = np.arange(srt_cws, end_cws, 1) # cws
        x3 = np.arange(srt_cws, end_cws+1, 1) # cws
        list_x_len_02.append(x)
        list_x_len_03.append(x3)
        for idx_2 in range(srt_plot_idx,end_plot_idx,step_plot_idx):
            print(idx_2)
            # non-stacked
            y = list_of_list_yrs_age_groups_not_stacked[idx_2][srt_cws:end_cws]
            list_y_len_02.append(y) 
            z = np.polyfit(x,y,1)
            # print("Linear Trends: 3 years")
            # print("{0}x + {1}".format(*z))
            list_lin_trend_temp.append(z)
            # stacked:
            y_stacked = list_of_list_yrs_age_groups_stacked[idx_2][srt_cws:end_cws+1]
            list_lin_trend_temp_y_stacked.append(y_stacked) 
            z_stacked = np.polyfit(x3,y_stacked,1)
            # print("Linear Trends: 3 years")
            # print("{0}x + {1}".format(*z_stacked))
            list_lin_trend_temp_z_stacked.append(z_stacked)
        list_lin_trend_02.append(list_lin_trend_temp)
        list_lin_trend_03.append(list_lin_trend_temp_z_stacked)
        list_y_len_03.append(list_lin_trend_temp_y_stacked) 
    
    # # optional: print all years: Linear Trends: annually
    # print("\nall years: Linear Trends: 3yrs")
    # print("Years: " , list(reversed(hg.annual_header21)), ", len:", len(list_lin_trend_annually))
    # print("Age Groups: " , hg.age_groups[1:], ", len:", len(hg.age_groups[1:]))
    # print(*list_lin_trend_02, sep = "\n")
            
    ##################################################################################################
    # plot age groups
    if lang_ge:
        lang_02 = "de"
        # title_des = "Todesprognose 2021 Deutsche Millenials GenXYZ (Altersgruppen < 45)\nLineare Trends mit randomisierten MinMax Rauschen"
        # title_des = "Todes-Bereichs-Prognosen 2021 Deutschland alle Altersgruppen\nLineare Trends mit MinMax Intervallen"
        title_des = "Todes-Bereichs-Prognosen 2021 Deutschland alle Altersgruppen\nLineare Trends mit saisonalen MinMax Intervallen"
        y_axis_des = "KW Tote"
        label_des_01 = "Vorhersagen\nZufallszahlen"
        label_des_02 = 'Letztes Update: KW'
        label_des_03 = 'Top5 Tote'
        label_des_04 = 'Rekordtiefs: '
        label_des_05 = ": KW"
        label_des_06 = "Alter: "
        label_des_07 = 'Pseudo Random Fit Stats: '
        filter_des_01 = "Geglättete Trends"
        filter_des_02 = "Lineare Trends 5J"
        filter_des_03 = "Lineare Trends 3J"
        prediction_des_01 = "Accuracy für Vorhersagen (Baseline: Lineare Trends 3 Jahre roll)"
        excess_des_01 = "Übersterblichkeit (Baseline: Linear Trends 5 Jahre)"
        # excess_des_01 = "Übersterblichkeit (Baseline: Linear Trends 5J, RKI Influenza Report 18/19 Simuliert)"
        excess_des_02 = "Übersterblichkeit (Baseline: Gesamttote Winter Season)"
    else: # default: English
        lang_02 = "en"
        # title_des  = "Death-Predictions 2021 German Millenials GenXYZ (Age Groups < 45)\nLinear Trends with Random MinMax Noise"
        # title_des  = "Death-Range-Predictions 2021 Germany all Age Groups\nLinear Trends with MinMax Intervals"
        title_des  = "Death-Range-Predictions 2021 Germany all Age Groups\nLinear Trends with seasonal MinMax Intervals"
        y_axis_des = "CW Deaths"
        label_des_01 = "Random\nPredictions"
        label_des_02 = 'Last Update: CW'
        label_des_03 = 'Top5 Death'
        label_des_04 = 'Record Lows: '
        label_des_05 = ": CW"
        label_des_06 = "Age: "
        label_des_07 = 'Pseudo Random Fit Stats: '
        filter_des_01 = "Smoothed Trends"
        filter_des_02 = "Linear Trends 5Y"
        filter_des_03 = "Linear Trends 3Y"
        prediction_des_01 = "Accuracy of Predictions (Baseline: Linear Trends 3 Years roll)"
        excess_des_01 = "Excess Deaths (Baseline: Linear Trends 5 Years)"
        # excess_des_01 = "Excess Deaths (Baseline: Linear Trends 5Y, RKI Influenza Report 18/19 Simulated)"
        excess_des_02 = "Excess Deaths (Baseline: Total Deaths Winter Season)"
    
    # ax1[0].set_title("2021 Random MinMax Predictions with Linear Trend\nfor German Age Groups < 45 (s:destatis)", fontsize=11)
    ax1[0].set_title(title_des, fontsize=12)
    # choose html color families:
    hmtl_colors_list = list(reversed(hg.hmtl_colors_10)) +\
                                    hg.hmtl_colors_09 +\
                                    hg.hmtl_colors_08 +\
                                    hg.hmtl_colors_06
    # set limits for axis, grid, etc. ..
    num_years = 6 # till end 2020 = 5
    x2 = np.arange(1, 52*num_years+2, 1) # cws
    y_min = 0

    # # for under 45:
    # y_max = 600 
    # y_step = 100

    # # for under 60:
    # y_max = 30000 # for all: 30000
    # y_step = 2000 # for all: 2000

    # for all:
    y_max = 30000 # for all: 30000
    y_step = 2000 # for all: 2000


    yticks2 = np.arange(y_min, y_max, y_step)
    yrange2 = (yticks2[0], yticks2[-1])
    xrange2 = (x2[0], x2[-1])
    xticks2 = np.arange(1, 52*num_years+1, 52)

    # do manually: vertical grid (due to CW 53)
    ax1[0].grid(True, color='grey', alpha=0.5, linestyle='solid',axis='y')

    # do manually: vertical grid (due to CW 53)
    annual_marker = [
                52*1,
                52*2,
                52*3,
                52*4,
                52*5 + 1,
                ]
    for idx_1 in range(0,len(annual_marker),1):
        ax1[0].axvline(x=annual_marker[idx_1], ymin=y_min, ymax=y_max, linewidth=1, color='grey', alpha=0.5, linestyle='solid')

    # add seasonal vertical grid (winter season: cw40-cw20, summer season: cw20-cw40)
    seasonal_marker = [
                52*0 + 20,
                52*0 + 40,
                52*1 + 20,
                52*1 + 40,
                52*2 + 20,
                52*2 + 40,
                52*3 + 20,
                52*3 + 40,
                52*4 + 20,
                52*4 + 40,
                52*5 + 20 + 1,
                52*5 + 40 + 1,
                ]
    
    if add_seasonal_grid:
        for idx_1 in range(0,len(seasonal_marker),1):
            ax1[0].axvline(x=seasonal_marker[idx_1], ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')

    # ax1[0].axvline(x=52*0 + 20, ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')
    # ax1[0].axvline(x=52*0 + 40, ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')
    # ax1[0].axvline(x=52*1 + 20, ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')
    # ax1[0].axvline(x=52*1 + 40, ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')
    # ax1[0].axvline(x=52*2 + 20, ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')
    # ax1[0].axvline(x=52*2 + 40, ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')
    # ax1[0].axvline(x=52*3 + 20, ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')
    ax1[0].axvline(x=52*3 + 40, ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')
    ax1[0].axvline(x=52*4 + 20, ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')
    # ax1[0].axvline(x=52*4 + 40, ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')
    # ax1[0].axvline(x=52*5 + 20 + 1, ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')
    # ax1[0].axvline(x=52*5 + 40 + 1, ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')
    
    # manual seasonal grid:
    ax1[0].axvline(x=52*4 + 40, ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')
    ax1[0].axvline(x=52*5 + 1 + 20, ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')
    ax1[0].axvline(x=52*5 + 1 + 40, ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')

    # corona: 1 welle
    # ax1[0].axvline(x=52*4 + 10, ymin=y_min, ymax=y_max, linewidth=1, color='blue', alpha=0.5, linestyle='solid')
    # ax1[0].axvline(x=52*4 + 20, ymin=y_min, ymax=y_max, linewidth=1, color='red', alpha=0.5, linestyle='solid')

    
    # major xticks
    x_pos = 52
    x_list_empty = [''] * len(hg.annual_header21)
    x_list_empty[-2] = " \nWS20/21\nCW40-20" # ; WS:= Winterseason CW40-CW20
    print(x_list_empty)
    x_locator = plt2.ticker.FixedLocator(annual_marker)
    x_formatter = plt2.ticker.FixedFormatter(x_list_empty)
    ax1[0].xaxis.set_major_locator(x_locator)
    ax1[0].xaxis.set_major_formatter(x_formatter)
    ax1[0].tick_params(which='major', axis="x", direction="out", length=2, width=1, color="black", labelsize=7, labelcolor='red', labelleft=True, labelbottom=True)
    ax1[0].set_xlabel(' ', fontsize=9)
    # [t.set_color('red') for t in ax1[0].xaxis.get_ticklabels()]
#     {'fontsize': rcParams['axes.titlesize'],
#  'fontweight': rcParams['axes.titleweight'],
#  'verticalalignment': 'baseline',
#  'horizontalalignment': loc}

    # ax1[0].set_xticklabels(ax1[0].xaxis.get_ticklabels(), verticalalignment= 'baseline')
    
    # minor xticks
    x_pos2 = 26
    annual_header21_reverse = list(reversed(hg.annual_header21))
    x_locator2 = plt2.ticker.FixedLocator([x_pos2*1, x_pos2*3, x_pos2*5, x_pos2*7, x_pos2*9, x_pos2*11])
    x_formatter2 = plt2.ticker.FixedFormatter(annual_header21_reverse + ["2021"])
    ax1[0].xaxis.set_minor_locator(x_locator2)
    ax1[0].xaxis.set_minor_formatter(x_formatter2)
    ax1[0].tick_params(which='minor', axis="x", direction="in", length=0, width=0, color="white")
    ax1[0].yaxis.set_minor_locator(plt2.ticker.MultipleLocator(1000))
    ax1[0].set_ylabel(y_axis_des, fontsize=10)
    ax1[0].set_yticks(yticks2)
    ax1[0].set_yticklabels(list(yticks2), fontsize=8)
    ax1[0].set_xlim(xrange2)
    ax1[0].set_ylim(yrange2)
    box = ax1[0].get_position() # shrink current axis by 20%
    ax1[0].set_position([box.x0, box.y0, box.width * 0.8, box.height])
    
    ##################################################################################################
    # plot data and legend
    ##################################################################################################
    # plot all
    # for idx_1 in range(len(list_of_list_yrs_age_groups_stacked)-1,-1,-1): 
    #     ax1[0].plot(x2, list_of_list_yrs_age_groups_stacked[idx_1],label=hg.age_groups[idx_1+1],color=hmtl_colors_list[idx_1+1])
    # ax1[0].legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8)

    # set which groups to plot
    set_group_sub = 12 # 12 for under 45
    # set_group_sub = 1 # 1 for al

    # pseudo line at zero
    ax1[0].plot(x2, np.zeros(len(x2)),label="",color="black", linewidth=0.0)

    #################################################################################################
    # add trend predictions: 5 years
    # plot trends: age < 45
    list_lin_trends_y = []
    cnt_obj = 0
    for idx_1 in range(srt_plot_idx,end_plot_idx,step_plot_idx): # plot trends: age < 45
        x5 = np.arange(1, len(x2)+1, 1) # cws
        y5 = np.zeros(len(x5)) + linear_offset
        for idx_2 in range(len(x5)):
            y5[idx_2] += list_lin_trend_all_years[idx_1][0] * x5[idx_2] + list_lin_trend_all_years[idx_1][1]
        list_lin_trends_y.append(y5)
        # print(list_lin_trend_all_years[idx_1][0], list_lin_trend_all_years[idx_1][1])

        if plot_5yr_linear_trends:
            if age_groups_plot[idx_1] == 1:
                if cnt_obj == 1:
                    print("\n Plot Linear Trends: 5 years")
                    ax1[0].plot(x5, y5,label= filter_des_02 + "\n+ Offset:" + str(linear_offset),color="#252625",alpha=1.0)
                    # ax1[0].plot(x5, y5,label= filter_des_02,color="grey",alpha=1.0)
                else:
                    ax1[0].plot(x5, y5,label= "",color="#252625",alpha=1.0)
                    # ax1[0].plot(x5, y5,label= "",color="grey",alpha=1.0)
                cnt_obj += 1

    
    ################################################################################################
    # add trend predictions: 1 years
    # plot trends: age < 45
    if plot_1yr_linear_trends:
        print("\n Plot Linear Trends: 1 years")
        x7 = np.empty([0], dtype=int)
        list_lin_trends_y2 = []
        srt_cws = 1
        end_cws = list_x_len[0]
        for idx_1 in range(srt_plot_idx,end_plot_idx,step_plot_idx): # init empty list with empty np.arrays
            list_lin_trends_y2.append(np.empty([0], dtype=int))
        for idx_0 in range(0,len(list_lin_trend_annually),1): 
            # print(list(reversed(hg.annual_header21))[idx_0])
            x7 = np.append(x7, np.arange(srt_cws, end_cws, 1), axis=None) 
            for idx_1 in range(srt_plot_idx,end_plot_idx,step_plot_idx): 
                x6 = np.arange(srt_cws, end_cws, 1) # cws
                y6 = np.zeros(list_x_len[idx_0]-1)
                for idx_2 in range(len(y6)):
                    y6[idx_2] = list_lin_trend_annually[idx_0][idx_1][0] * x6[idx_2] + list_lin_trend_annually[idx_0][idx_1][1]
                list_lin_trends_y2[idx_1] = np.append(list_lin_trends_y2[idx_1],y6, axis=None) 
            srt_cws = end_cws
            try:
                end_cws = end_cws + list_x_len[idx_0+1] - 1
            except:
                pass
        y7_stack = np.zeros([1,len(list_lin_trends_y2[0])], dtype=int)
        
        for idx_1 in range(srt_plot_idx,end_plot_idx,step_plot_idx):
            y7_stack = np.append(y7_stack,[list_lin_trends_y2[idx_1]], axis=0)
            y7 = np.sum(y7_stack, axis = 0)
            if age_groups_plot[idx_1] == 1:
                ax1[0].plot(x7, y7,label= "",color="blue")
    
    ################################################################################################
    # add trend predictions: 3 years
    # plot trends: age < 45

    # for eval
    array_eval_accuracy_3yrs = np.empty((len(age_groups_plot),len(hg.annual_header21),), dtype=object) # table rows, table cols
    array_eval_accuracy_3yrs[:] = "-"
    array_eval_accuracy_3yrs_02 = np.empty((len(hg.annual_header21),len(age_groups_plot),), dtype=object) # table rows, table cols
    array_eval_accuracy_3yrs_02[:] = "-"

    y6_list_lin_trends = []
    y6_range_list_annual_min = []
    y6_range_list_annual_max = []
    y6_range_list_season_ws_min = []
    y6_range_list_season_ws_max = []
    y6_range_list_season_ss_min = []
    y6_range_list_season_ss_max = []

    # all years for evaluation
    y7_list_lin_trends = []
    y7_range_list_min = []
    y7_range_list_max = []

    for idx_0 in range(0,len(list_x_len_02),1):
        x6 = list_x_len_03[idx_0]
        y6_list_temp = []
        y6_range_temp_annual_min = []
        y6_range_temp_annual_max = []
        y6_range_temp_season_ws_min = []
        y6_range_temp_season_ws_max = []
        y6_range_temp_season_ss_min = []
        y6_range_temp_season_ss_max = []

        for idx_1 in range(0,len(list_lin_trend_03[0]),1):
            y6 = np.zeros(len(x6))
            y6_range_min = np.zeros(len(x6))
            y6_range_max = np.zeros(len(x6))
            # y6_range_min = []
            # y6_range_max = [] 
            print()
            for idx_2 in range(len(y6)):
                y6[idx_2] = list_lin_trend_03[idx_0][idx_1][0] * x6[idx_2] + list_lin_trend_03[idx_0][idx_1][1]
                y6_diff = list_y_len_03[idx_0][idx_1][idx_2] - y6[idx_2]
                if y6_diff > 0: # max case, maxs
                    # y6_range_max.append(abs(y6_diff))
                    y6_range_max[idx_2] = abs(y6_diff)
                elif y6_diff <= 0: # max case, mins
                    # y6_range_min.append(abs(y6_diff))
                    y6_range_min[idx_2] = abs(y6_diff)
            y6_list_temp.append(y6)
            y6_range_temp_annual_min.append(max(y6_range_min))
            y6_range_temp_annual_max.append(max(y6_range_max))
        
            #filter by seasonal data:
            # print(y6_range_min, len(y6_range_min), max(y6_range_min))
            # print( len(y6_range_max), max(y6_range_max))
            

            y6_range_min_list = y6_range_min.tolist()
            y6_range_max_list = y6_range_max.tolist()

            # ws
            y6_range_temp_season_ws_min.append(max(
                y6_range_min_list[-52-52-53-12:-52-53-32]+\
                y6_range_min_list[-52-53-12:-53-32]+\
                y6_range_min_list[-53-12:0-33]
            ))
            y6_range_temp_season_ws_max.append(max(
                y6_range_max_list[-52-52-53-12:-52-53-32]+\
                y6_range_max_list[-52-53-12:-53-32]+\
                y6_range_max_list[-53-12:0-33]
            ))
        
            # ss
            y6_range_temp_season_ss_min.append(max(
                y6_range_min_list[-52-53-32:-52-53-12]+\
                y6_range_min_list[-53-32:-53-12]+\
                y6_range_min_list[0-33:0-13]
                ))
            y6_range_temp_season_ss_max.append(max(
                y6_range_max_list[-52-53-32:-52-53-12]+\
                y6_range_max_list[-53-32:-53-12]+\
                y6_range_max_list[0-33:0-13]
                ))
    
        y6_list_lin_trends.append(y6_list_temp)
        y6_range_list_annual_min.append(y6_range_temp_annual_min)
        y6_range_list_annual_max.append(y6_range_temp_annual_max)
        y6_range_list_season_ws_min.append(y6_range_temp_season_ws_min)
        y6_range_list_season_ws_max.append(y6_range_temp_season_ws_max)
        y6_range_list_season_ss_min.append(y6_range_temp_season_ss_min)
        y6_range_list_season_ss_max.append(y6_range_temp_season_ss_max)

        #######################################################################
        # all years for evaluation
        x7 = np.arange(1, len(x2)+1, 1) # cws
        y7_list_temp = []
        y7_range_temp_min = []
        y7_range_temp_max = []
        cnt_obj = 4
        for idx_1 in range(0,len(list_lin_trend_03[0]),1): 
            cnt_obj -= 1
            # all years for evaluation
            y7 = np.zeros(len(x7))
            y7_range_min = []
            y7_range_max = []
            for idx_2 in range(len(x7)):
                y7[idx_2] = list_lin_trend_03[idx_0][idx_1][0] * x7[idx_2] + list_lin_trend_03[idx_0][idx_1][1]
            y7_list_temp.append(y7)
        y7_list_lin_trends.append(y7_list_temp) 

    # evaluation stats
    list_eval_accuracy_3yrs = []
    cnt_obj_02 = 0
    cnt_seasonal_ws = -9
    cnt_seasonal_ss = -8
    for idx_1 in range(0,len(list_x_len_02),1):
        list_eval_accuracy_temp = []
        cnt_obj = len(list_lin_trend_03[0])  
        cnt_seasonal_ws += 2
        cnt_seasonal_ss += 2   
        for idx_2 in range(0,len(list_lin_trend_03[0]),1):
            cnt_obj -= 1
            # for debugging only:
            # ax1[0].plot(list_x_len_03[idx_1], y6_list_lin_trends[idx_1][idx_2],label= "",color="lime")
            # ax1[0].plot(list_x_len_03[idx_1], y6_list_lin_trends[idx_1][idx_2]-y6_range_list_annual_min[idx_1][idx_2],label= "",color="blue")
            # ax1[0].plot(list_x_len_03[idx_1], y6_list_lin_trends[idx_1][idx_2] + y6_range_list_annual_max[idx_1][idx_2],label= "",color="orange")
            # ax1[0].plot(np.arange(x_cws_in_srt_list[idx_1+3],x_cws_in_end_list[idx_1+3],1), list_of_list_yrs_age_groups_stacked[idx_2][x_cws_in_srt_list[idx_1+3]:x_cws_in_end_list[idx_1+3]],label= "",color="purple")

            # prediction: 2021 only 
            if age_groups_plot[idx_2] == 1:
                if plot_3yr_linear_trends:
                    if cnt_obj_02 == 0:
                        print("\n Plot Linear Trends: 3 years")
                        ax1[0].plot(x7[-52-52-52-53-1:], y7_list_lin_trends[len(list_x_len_02)-1][idx_2][-52-52-52-53-1:], label= filter_des_03,color="grey") #222422
                    else:
                        ax1[0].plot(x7[-52-52-52-53-1:], y7_list_lin_trends[len(list_x_len_02)-1][idx_2][-52-52-52-53-1:], label= "",color="grey")

                if plot_predictions_lin_3_yrs_roll_annual: # for annual season
                    ax1[0].fill_between(x7[seasonal_marker[-3]-1:],y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[-3]-1:]-y6_range_list_annual_min[len(list_x_len_02)-1][idx_2],\
                        y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[-3]-1:]+y6_range_list_annual_max[len(list_x_len_02)-1][idx_2],\
                            color=hmtl_colors_list[idx_2+1],alpha=0.1,lw=0,zorder=0)
                    
                    # do evaluation for all: annually
                    min_temp = y7_list_lin_trends[idx_1][idx_2][x_cws_in_srt_list[idx_1+3]-1:x_cws_in_end_list[idx_1+3]] - y6_range_list_annual_min[idx_1][idx_2]
                    max_temp = y7_list_lin_trends[idx_1][idx_2][x_cws_in_srt_list[idx_1+3]-1:x_cws_in_end_list[idx_1+3]] + y6_range_list_annual_max[idx_1][idx_2]
                    vec_eval = list_of_list_yrs_age_groups_stacked[idx_2][x_cws_in_srt_list[idx_1+3]-1:x_cws_in_end_list[idx_1+3]]

                if plot_predictions_lin_3_yrs_roll_season:
                    # debugging only
                    # WS
                    # ax1[0].fill_between(x7[seasonal_marker[cnt_seasonal_ws]-1:seasonal_marker[cnt_seasonal_ws + 1]],y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[cnt_seasonal_ws]-1:seasonal_marker[cnt_seasonal_ws + 1]]-y6_range_list_season_ws_min[len(list_x_len_02)-1][idx_2],\
                    #     y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[cnt_seasonal_ws]-1:seasonal_marker[cnt_seasonal_ws + 1]]+y6_range_list_season_ws_max[len(list_x_len_02)-1][idx_2],\
                    #         color="blue",alpha=0.5,lw=0,zorder=0)
                    
                    diff_len = len(x7[seasonal_marker[cnt_seasonal_ws]-1:seasonal_marker[cnt_seasonal_ws + 1]]) \
                        - len(list_of_list_yrs_age_groups_stacked[idx_2][seasonal_marker[cnt_seasonal_ws]-1:seasonal_marker[cnt_seasonal_ws + 1]])
                    # ax1[0].plot(x7[seasonal_marker[cnt_seasonal_ws]-1:seasonal_marker[cnt_seasonal_ws + 1] - diff_len],\
                    #      list_of_list_yrs_age_groups_stacked[idx_2][seasonal_marker[cnt_seasonal_ws]-1:seasonal_marker[cnt_seasonal_ws + 1]],\
                    #          label= "",color="red",linewidth = 5.0)

                    # ax1[0].fill_between(x7[seasonal_marker[cnt_seasonal_ws]-1:seasonal_marker[cnt_seasonal_ws + 1] - diff_len],\
                    #     list_of_list_yrs_age_groups_stacked[idx_2][seasonal_marker[cnt_seasonal_ws]-1:seasonal_marker[cnt_seasonal_ws + 1]],\
                    #     y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[cnt_seasonal_ws]-1:seasonal_marker[cnt_seasonal_ws + 1]- diff_len],\
                    #         color="yellow",alpha=0.9,lw=0,zorder=0)
                
                    # # SS
                    # ax1[0].fill_between(x7[seasonal_marker[cnt_seasonal_ss]-1:seasonal_marker[cnt_seasonal_ss + 1]],y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[cnt_seasonal_ss]-1:seasonal_marker[cnt_seasonal_ss + 1]]-y6_range_list_season_ss_min[len(list_x_len_02)-1][idx_2],\
                    #     y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[cnt_seasonal_ss]-1:seasonal_marker[cnt_seasonal_ss + 1]]+y6_range_list_season_ss_max[len(list_x_len_02)-1][idx_2],\
                    #         color="cyan",alpha=0.5,lw=0,zorder=0)

                    # real:
                    # for winter season
                    ax1[0].fill_between(x7[seasonal_marker[-3]-1:seasonal_marker[-2]],y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[-3]-1:seasonal_marker[-2]]-y6_range_list_season_ws_min[len(list_x_len_02)-1][idx_2],\
                        y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[-3]-1:seasonal_marker[-2]]+y6_range_list_season_ws_max[len(list_x_len_02)-1][idx_2],\
                            color=hmtl_colors_list[idx_2+1],alpha=0.1,lw=0,zorder=0)
                    # extra: for winter season(21/22)
                    ax1[0].fill_between(x7[seasonal_marker[-1]-1:seasonal_marker[-1]+22],y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[-1]-1:seasonal_marker[-1]+22]-y6_range_list_season_ws_min[len(list_x_len_02)-1][idx_2],\
                        y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[-1]-1:seasonal_marker[-1]+22]+y6_range_list_season_ws_max[len(list_x_len_02)-1][idx_2],\
                            color=hmtl_colors_list[idx_2+1],alpha=0.1,lw=0,zorder=0) # hmtl_colors_list[idx_2+1]
                    # for summer season
                    ax1[0].fill_between(x7[seasonal_marker[-2]-1:seasonal_marker[-1]],y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[-2]-1:seasonal_marker[-1]]-y6_range_list_season_ss_min[len(list_x_len_02)-1][idx_2],\
                        y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[-2]-1:seasonal_marker[-1]]+y6_range_list_season_ss_max[len(list_x_len_02)-1][idx_2],\
                            color= hmtl_colors_list[idx_2+1],alpha=0.1,lw=0,zorder=0) # hmtl_colors_list[idx_2+1]
                    
                cnt_obj_02 += 1
            
            ###############################################################
            # for evaluation: accucracy (based on 3yrs MinMax), 3 x 15 (Altergruppen)  
            if plot_predictions_lin_3_yrs_roll_annual: # for annual season
                row_labels_evaluation = annual_header21_reverse # set labels for table

                # do evaluation for all: annually
                min_temp = y7_list_lin_trends[idx_1][idx_2][x_cws_in_srt_list[idx_1+3]-1:x_cws_in_end_list[idx_1+3]] - y6_range_list_annual_min[idx_1][idx_2]
                max_temp = y7_list_lin_trends[idx_1][idx_2][x_cws_in_srt_list[idx_1+3]-1:x_cws_in_end_list[idx_1+3]] + y6_range_list_annual_max[idx_1][idx_2]
                vec_eval = list_of_list_yrs_age_groups_stacked[idx_2][x_cws_in_srt_list[idx_1+3]-1:x_cws_in_end_list[idx_1+3]]

            
            if plot_predictions_lin_3_yrs_roll_season: # for seasons 
                row_labels_evaluation = hg.seasonal_header_03  # set labels for table
                # SS
                # min_temp = y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[cnt_seasonal_ss]-1:seasonal_marker[cnt_seasonal_ss + 1]] - y6_range_list_season_ss_min[len(list_x_len_02)-1][idx_2]
                # max_temp = y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[cnt_seasonal_ss]-1:seasonal_marker[cnt_seasonal_ss + 1]] + y6_range_list_season_ss_max[len(list_x_len_02)-1][idx_2]
                # vec_eval = list_of_list_yrs_
                # age_groups_stacked[idx_2][seasonal_marker[cnt_seasonal_ss]-1:seasonal_marker[cnt_seasonal_ss + 1]]

                # WS (bis 20/21)
                # diff_len = len(y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[cnt_seasonal_ws]-1:seasonal_marker[cnt_seasonal_ws + 1]]) \
                #         - len(list_of_list_yrs_age_groups_stacked[idx_2][seasonal_marker[cnt_seasonal_ws]-1:seasonal_marker[cnt_seasonal_ws + 1]])

                min_temp = y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[cnt_seasonal_ws]-1:seasonal_marker[cnt_seasonal_ws + 1]]-y6_range_list_season_ws_min[len(list_x_len_02)-1][idx_2]
                max_temp = y7_list_lin_trends[len(list_x_len_02)-1][idx_2][seasonal_marker[cnt_seasonal_ws]-1:seasonal_marker[cnt_seasonal_ws + 1]]+y6_range_list_season_ws_max[len(list_x_len_02)-1][idx_2]
                vec_eval = list_of_list_yrs_age_groups_stacked[idx_2][seasonal_marker[cnt_seasonal_ws]-1:seasonal_marker[cnt_seasonal_ws + 1]] 

                

            cnt_TP = 0
            cnt_TN = 0
            cnt_FP = 0
            cnt_FN = 0
            for idx_3 in range(len(vec_eval)):
                if vec_eval[idx_3] >= min_temp[idx_3] and vec_eval[idx_3] <= max_temp[idx_3]: # true positives
                    cnt_TP += 1
                elif vec_eval[idx_3] < min_temp[idx_3] or vec_eval[idx_3] > max_temp[idx_3]: # false positives
                    print("Error")
                    print(idx_1, idx_2)
                    print(min_temp)
                    print(max_temp)
                    print(vec_eval)
                    print(vec_eval[idx_3],min_temp[idx_3],max_temp[idx_3])
                    cnt_FP += 1
                else:
                    print("Error, evaluation stats.")
            # print("\nPredictor Eval:")
            accuracy = round(hf.div_by_zero((cnt_TP + cnt_TN), (cnt_TP + cnt_TN + cnt_FP + cnt_FN)), 2)
            array_eval_accuracy_3yrs[cnt_obj][idx_1+3] = f"{accuracy:4.2f}"
            array_eval_accuracy_3yrs_02[idx_1+3][cnt_obj] = f"{accuracy:4.2f}"
            list_eval_accuracy_temp.append(f"{accuracy:4.2f}")
            print(f"accuracy: {accuracy:4.2f}", cnt_FP, cnt_TP)
        list_eval_accuracy_3yrs.append(list_eval_accuracy_temp)
    # print(array_eval_accuracy_3yrs_02)
    array_eval_accuracy_3yrs_02 = np.fliplr(array_eval_accuracy_3yrs_02)


    # ##################################################################################################
    # add prediction curves
    # for idx_1 in range(1, len(list_of_list_yrs_age_groups_stacked)-set_group_sub+2,1):
    #     set_age_band = - idx_1 # -1 the youngest

        # print("Plot Min/Max:",list_min_max[set_age_band][0],list_min_max[set_age_band][1])
        # x4 = np.arange(len(x2)-51, len(x2)+1, 1) 
        # y4 = np.ones((len(x4),), dtype=int) * list_of_list_yrs_age_groups_stacked[abs(set_age_band)-1][-1]
        # ax1[0].plot(x4,y4 ,label="Prediction Min",color="green")
        # # add min
        # x4 = np.arange(len(x2)-51, len(x2)+1, 1) 
        # y4 = np.ones((len(x4),), dtype=int) * min(list_of_list_yrs_age_groups_stacked[abs(set_age_band)-1][-105:])
        # ax1[0].plot(x4,y4 ,label="Prediction",color="blue")
        # # add max
        # x4 = np.arange(len(x2)-51, len(x2)+1, 1) 
        # y4 = np.ones((len(x4),), dtype=int) * max(list_of_list_yrs_age_groups_stacked[abs(set_age_band)-1][-105:])
        # ax1[0].plot(x4,y4 ,label="Prediction Max",color="red")
    

    #################################################################################################
    # check: Normalized cross correlation btwn years
    srt_yrs_idx = np.arange(0,len(hg.annual_header21)+1,1) * 52
    srt_yrs_idx[5] = srt_yrs_idx[5] + 1 # special case 53cws 2020
    # print("\n", hg.annual_header21[::-1])
    # print(srt_yrs_idx)
    for idx_1 in range(len(hg.annual_header21)-2):
        # print("\nHorizontal: Normalized Cross Correlation btwn years:",hg.annual_header21[::-1][idx_1],hg.annual_header21[::-1][idx_1+1])
        # print("                Stacked Data, ")
        for idx_2 in range(len(list_of_list_yrs_age_groups_stacked)):
            vector_1 = list_of_list_yrs_age_groups_stacked[idx_2][srt_yrs_idx[idx_1]:srt_yrs_idx[idx_1+1]]
            vector_2 = list_of_list_yrs_age_groups_stacked[idx_2][srt_yrs_idx[idx_1+1]:srt_yrs_idx[idx_1+2]]
            a,b,c,_,_ = hf.norm_cross_corr_1D(vector_1, vector_2, 'full') # options: 'valid', 'same' , 'full'
            # print("AgeGroup:",hg.age_groups3[idx_2],'Corr: %.2f' % b, c)
    
    #################################################################################################
    # check: Pearson correlation for each year
    # 2d arrays for matplot plotting
    corr_2d = np.zeros([len(hg.annual_header21), len(hg.age_groups[1:])]) # init matrix
    pval_2d = np.zeros([len(hg.annual_header21), len(hg.age_groups[1:])]) # init matrix

    np.set_printoptions(precision=3, suppress=True)
    list_yr_p1 = []
    list_yr_r1 = []

    # for table, create lists
    corr_2d_list = []
    pval_2d_list = []

    for idx_1 in range(len(hg.annual_header21[::-1])):
        # print("\nVertical: Pearson correlation for each year:",hg.annual_header21[::-1][idx_1])
        # print("                AgeGroup Data, ")
        r1, p1 = hf.corrcoef(list_of_array_yr[::-1][idx_1])
        # print(r1)
        list_yr_r1.append(r1[0,:])
        # print(p1)
        list_yr_p1.append(p1[0,:])
        corr_2d[idx_1,:] = r1[0,1:] # init matrix
        pval_2d[idx_1,:] = p1[0,1:] # init matrix

        list_r1 = ["%.3f" % x for x in r1[0,1:]]
        list_p1 = ["%.2e" % x for x in p1[0,1:]]

        # list_r1 = [int(i) for i in list(r1[0,1:])]
        # list_p1 = [int(i) for i in list(p1[0,1:])]

        corr_2d_list.append(list_r1)
        pval_2d_list.append(list_p1)


    # print("correlation matrix for age groups:", hg.annual_header21[::-1], ",shape:",r1.shape, len(hg.age_groups))
    # print(hg.age_groups, sep = "\n")
    # print(*list_yr_r1, sep = "\n")
    # print("Two-tailed p-value matrix for age groups:", hg.annual_header21[::-1], ",shape:",p1.shape, len(hg.age_groups))
    # # np.set_printoptions(precision=5, suppress=True)
    # np.set_printoptions(precision=3, suppress=False)
    # print(hg.age_groups, sep = "\n")
    # print(*list_yr_p1, sep = "\n")


    #################################################################################################
    # check: Pearson correlation for each season
    list_total_yrs_age_groups = []
    for idx_1 in range(len(list_of_array_yr[::-1][0])): # do for all age groups
        temp_array = np.empty([0], dtype=int)
        for idx_2 in range(len(hg.annual_header21[::-1])): # horizontal stacking
            temp_array = np.append(temp_array, list_of_array_yr[::-1][idx_2][idx_1], axis=None)
            # print(temp_array.shape)
        list_total_yrs_age_groups.append(temp_array)
    # print(*list_total_yrs_age_groups, sep = "\n")

    # srt_yrs_idx = np.arange(0,len(hg.annual_header21)+1,1) * 52
    # srt_yrs_idx[5] = srt_yrs_idx[5] + 1 # special case 53cws 2020
    # print("\n", hg.annual_header21[::-1])
    # print(srt_yrs_idx)
    # for idx_1 in range(len(hg.annual_header21[::-1])-2):
    #     print("\nVertical: Pearson correlation for each season:",hg.annual_header21[::-1][idx_1],hg.annual_header21[::-1][idx_1+1])
    #     print("                Stacked Data, ")
    #     r1, p1 = hf.corrcoef(list_total_yrs_age_groups[:][0:10])
    
    
    # 1yrs prediction
    #################################################################################################
    # add random prediction
    # *   p < 0.05 (2 Sigma)
    # **  p < 0.01
    # *** p < 0.001 (3 Sigma), 1.0e-3
    # p < 3.0e-7 (5 Sigma)
    # set thresholds:
    CORRELATION_THRESHOLD = 0.60 # 0.97 takes some minutes
    PVALUE_THRESHOLD = 1.0e-3 # 1.0e-3

    if plot_random_number_1yr:
        cnt_idx = 0 
        cnt_idx_02 = 0
        list_corr_fit_stats = []
        print("\n Start Sudo Random Correlation Fit:")
        for idx_1 in range(srt_plot_idx,end_plot_idx,step_plot_idx): 
            srt_num_cws = 4*52 # set start cw for data science
            end_num_cws = 4*52+53 # set end cw for data science
            # minmax_range = abs(max(list_of_list_yrs_age_groups_stacked[idx_1][srt_num_cws:end_num_cws]) - min(list_of_list_yrs_age_groups_stacked[idx_1][srt_num_cws:end_num_cws]))
            x4 = np.arange(len(x2)-52, len(x2)+1, 1) 
            # y4 = np.random.rand(len(x4)) * minmax_range + min(list_of_list_yrs_age_groups_stacked[abs(set_age_band)-1][srt_num_cws:end_num_cws]) # minmax_range
            max_diff = max(abs(list_of_list_yrs_age_groups_stacked[idx_1][srt_num_cws:end_num_cws] - list_lin_trends_y[cnt_idx][srt_num_cws:end_num_cws]))
            # min_diff = min(list_lin_trends_y[idx_1-1][srt_num_cws:end_num_cws] - list_of_list_yrs_age_groups_stacked[idx_1][srt_num_cws:end_num_cws])
            # print(max_diff, minmax_range)
            # do curve fitting by correlation threshold fitting > 0.5
            corr_threshold = 0
            pval_threshold = 1
            seed_num = 0
            a = datetime.datetime.now().replace(microsecond=0)
            while corr_threshold < CORRELATION_THRESHOLD or pval_threshold > PVALUE_THRESHOLD:
                np.random.seed(seed=seed_num)
                y4 = np.random.uniform(-1,1,len(x4)) * max_diff + list_lin_trends_y[cnt_idx][-len(x4):] # mean_range
                y4[0] = list_lin_trends_y[cnt_idx][-len(x4)]

                correl_matrix = np.array([y4[0:len(list_of_list_yrs_age_groups_stacked[idx_1][end_num_cws:])+1],\
                    list_of_list_yrs_age_groups_stacked[idx_1][end_num_cws-1:]])
                # print(correl_matrix)
                r1, p1 = hf.corrcoef(correl_matrix)
                # print(cnt_idx+1,' R1: %.3f' % r1[0,1], 'P1: %.3e' % p1[0,1], seed_num)
                corr_threshold = r1[0,1]
                pval_threshold = p1[0,1]
                seed_num += 1
            # time stamp
            b = datetime.datetime.now().replace(microsecond=0)
            print(cnt_idx+1,' R1: %.3f' % r1[0,1], 'P1: %.3e' % p1[0,1], seed_num, b-a)
            list_corr_fit_stats.append([r1[0,1], p1[0,1], seed_num, b-a])

            if age_groups_plot[cnt_idx] == 1:
                if cnt_idx == 1:       
                    label_des = label_des_01
                else:
                    label_des = ""
                cnt_idx_02 += 1
                ax1[0].plot(x4,y4 ,label=label_des,color="#29d963",alpha=0.8, linestyle='dashed',linewidth=0.7) # lime: #29d963 
            cnt_idx +=1
            
                 
        # print("\n Correlation Fit Stats:")
        # print(*list_corr_fit_stats, sep = "\n")
    
    # 3yrs prediction
    #################################################################################################
    # add random prediction
    # *   p < 0.05 (2 Sigma)
    # **  p < 0.01
    # *** p < 0.001 (3 Sigma), 1.0e-3
    # p < 3.0e-7 (5 Sigma)
    # set thresholds:
    CORRELATION_THRESHOLD = 0.6 # 0.97 takes some minutes
    PVALUE_THRESHOLD = 1.0e-1 # 3sigma: 1.0e-3

    if plot_random_number_3yr:
        cnt_idx = 0 
        cnt_idx_02 = 0
        list_corr_fit_stats = []
        x4 = np.arange(len(x2)-52, len(x2)+1, 1)
        print("\n Start Sudo Random Correlation Fit:")
        for idx_1 in range(srt_plot_idx,end_plot_idx,step_plot_idx): 
            srt_num_cws = 4*52 # set start cw for data science
            end_num_cws = 4*52+53 # set end cw for data science 
            # set init values for random mutation (genetic algorithm):
            corr_threshold = 0
            pval_threshold = 1
            seed_num = 0
            min_val = -1 * y6_range_list_annual_min[len(list_x_len_02)-1][cnt_idx]
            max_val = +1 * y6_range_list_annual_max[len(list_x_len_02)-1][cnt_idx]
            # print(min_val)
            # print(max_val)
            a = datetime.datetime.now().replace(microsecond=0)
            while corr_threshold < CORRELATION_THRESHOLD or pval_threshold > PVALUE_THRESHOLD:
                np.random.seed(seed=seed_num)    
                y4 = np.random.uniform(min_val, max_val,len(x4)) + y7_list_lin_trends[len(list_x_len_02)-1][cnt_idx][-53:] # mean_range
                y4[0] = y7_list_lin_trends[len(list_x_len_02)-1][cnt_idx][-len(x4)]

                correl_matrix = np.array([y4[0:len(list_of_list_yrs_age_groups_stacked[idx_1][end_num_cws:])+1],\
                    list_of_list_yrs_age_groups_stacked[idx_1][end_num_cws-1:]])
                # print(correl_matrix)
                r1, p1 = hf.corrcoef(correl_matrix)
                # print(cnt_idx+1,' R1: %.3f' % r1[0,1], 'P1: %.3e' % p1[0,1], seed_num)
                corr_threshold = r1[0,1]
                pval_threshold = p1[0,1]
                seed_num += 1
              
            # time stamp
            b = datetime.datetime.now().replace(microsecond=0)
            print(cnt_idx+1,' R1: %.3f' % r1[0,1], 'P1: %.3e' % p1[0,1], seed_num, b-a)
            list_corr_fit_stats.append([r1[0,1], p1[0,1], seed_num, b-a])

            if age_groups_plot[cnt_idx] == 1:
                if cnt_idx_02 == 0:       
                    label_des = label_des_01
                else:
                    label_des = "" 
                cnt_idx_02 += 1
                ax1[0].plot(x4,y4,label=label_des,color="#fc035e",alpha=0.8, linestyle='dashed',linewidth=0.7) # lime: #29d963
            cnt_idx +=1
                     
        # print("\n Correlation Fit Stats:")
        # print(*list_corr_fit_stats, sep = "\n")


    # optional: add smooting filter
    ##################################################################################################
    # add filtering: Savitzky-Golay
    # https://stackoverflow.com/questions/20618804/how-to-smooth-a-curve-in-the-right-way
    cnt_idx = 0
    for idx_1 in range(srt_plot_idx,end_plot_idx,step_plot_idx): 
        x3 = np.arange(1, len(list_of_list_yrs_age_groups_stacked[idx_1])+1, 1) # cws
        y3 = list_of_list_yrs_age_groups_stacked[idx_1]
        if plot_smooth_filter_01:
            if age_groups_plot[idx_1] == 1:
                # y_filter_01 = savgol_filter(y3, 51, 3) # window size 51 (must be odd), polynomial order 3
                y_filter_01 = savgol_filter(y3, filter_size_01, poly_order_01) # window size 51 (must be odd), polynomial order 3
                list_of_list_yrs_age_groups_stacked[idx_1]
                if cnt_idx == 0:
                    filter_des = filter_des_01
                else:
                    filter_des = ""
                ax1[0].plot(x3, y_filter_01,label=filter_des,color="#0650A7",linewidth=2.0)
                cnt_idx += 1    

    ##################################################################################################
    # plot original data
    num_mins = 5 # get top 5 minima
    list_of_min = []
    list_of_min_idx = []
    list_min_str_all = []
    cnt_idx = 0
    for idx_1 in range(srt_plot_idx,end_plot_idx,step_plot_idx): 
        x3 = np.arange(1, len(list_of_list_yrs_age_groups_stacked[idx_1])+1, 1) # cws
        y3 = list_of_list_yrs_age_groups_stacked[idx_1]
        # plot original
        ##################################################################################################
        if plot_signals_01:
            if age_groups_plot[idx_1] == 1:
                ax1[0].plot(x3, y3,label=hg.age_groups3[idx_1],color=hmtl_colors_list[idx_1+1])

        ##################################################################################################
        # get record lows:
        y6 = list_of_list_yrs_age_groups_not_stacked[idx_1] # unstacked data 
        idx_mins = np.argsort(y6) # unstacked data 
        # print(idx_mins[0] + 1)
        list_of_min_idx.append(idx_mins) # get the indices, for sort by minimum
        list_of_min.append(np.sort(y6)) # get sort by minimum

        list_min_str = []
        for idx_2 in range(0,num_mins,1): 
            if idx_mins[idx_2] + 1 <= 52 * 1: # 2016
                if idx_mins[idx_2] + 1 < 10:
                    list_min_str.append("0" + str(idx_mins[idx_2] + 1) + " " + hg.annual_header21[5])
                else:
                    list_min_str.append(str(idx_mins[idx_2] + 1) + " " + hg.annual_header21[5])
            elif idx_mins[idx_2] + 1 > 52 * 1 and idx_mins[idx_2] + 1 <= 52 * 2:  # 2017
                if idx_mins[idx_2] + 1 - 52 * 1 < 10:
                    list_min_str.append("0" + str(idx_mins[idx_2] + 1 - 52 * 1) + " " + hg.annual_header21[4])
                else:
                    list_min_str.append(str(idx_mins[idx_2] + 1 - 52 * 1) + " " + hg.annual_header21[4])

            elif idx_mins[idx_2] + 1 > 52 * 2 and idx_mins[idx_2] + 1 <= 52 * 3: # 2018
                if idx_mins[idx_2] + 1 - 52 * 2 < 10:
                    list_min_str.append("0" + str(idx_mins[idx_2] + 1 - 52 * 2) + " " + hg.annual_header21[3])
                else:
                    list_min_str.append(str(idx_mins[idx_2] + 1 - 52 * 2) + " " + hg.annual_header21[3])

            elif idx_mins[idx_2] + 1 > 52 * 3 and idx_mins[idx_2] + 1 <= 52 * 4: # 2019
                if idx_mins[idx_2] + 1 - 52 * 3 < 10:
                    list_min_str.append("0" + str(idx_mins[idx_2] + 1 - 52 * 3) + " " + hg.annual_header21[2])
                else:
                    list_min_str.append(str(idx_mins[idx_2] + 1 - 52 * 3) + " " + hg.annual_header21[2])

            elif idx_mins[idx_2] + 1 > 52 * 4 and idx_mins[idx_2] + 1 <= 52 * 4 + 53: # 2020
                if idx_mins[idx_2] + 1 - 52 * 4 < 10:
                    list_min_str.append("0" + str(idx_mins[idx_2] + 1 - 52 * 4) + " " + hg.annual_header21[1])
                else:
                    list_min_str.append(str(idx_mins[idx_2] + 1 - 52 * 4) + " " + hg.annual_header21[1])

            elif idx_mins[idx_2] + 1 > 52 * 4 + 53: # 2021
                if idx_mins[idx_2] + 1 - (52 * 4 + 53) < 10:
                    list_min_str.append( "0" + str(idx_mins[idx_2] + 1 - (52 * 4 + 53)) + " " + hg.annual_header21[0])
                else:
                    list_min_str.append(str(idx_mins[idx_2] + 1 - (52 * 4 + 53)) + " " + hg.annual_header21[0])
       
        list_min_str_all.append(list_min_str)

        
    # print("y6_min_sort, len:", len(y6), "start with 0 - to len()-1")
    # print(*list_of_min, sep = "\n")
    # print("y6_idx, len:", len(y6), "start with 0 - to len()-1")
    # print(*list_of_min_idx, sep = "\n")
    # print("Top", len(list_min_str))
    # print(*list_min_str_all, sep = "\n")
        
    ##################################################################################################
    # # add correlation figure
    # # 2020, down to 2016
    # list_corr_matrix = list_of_array_yr[-1:][0][1:len(list_of_list_yrs_age_groups_stacked)-set_group_sub+2]
    # for idx_1 in range(2, len(list_of_list_yrs_age_groups_stacked)-set_group_sub+2,1):
    #     print(idx_1)
    #     list_corr_matrix = np.append(list_corr_matrix, list_of_array_yr[idx_1][1:len(list_of_list_yrs_age_groups_stacked)-set_group_sub+2], axis=0)
                
    # print(*list_corr_matrix, sep = "\n")
    # r1, p1 = hf.corrcoef(list_corr_matrix)
    # print(r1)

    # # 2d arrays for matplot plotting
    # corr_2d = np.zeros([len(annual_header21)+1, len(list_of_list_yrs_age_groups_stacked)-set_group_sub+2]) # init matrix
    # pval_2d = np.zeros([len(annual_header21)+1, len(list_of_list_yrs_age_groups_stacked)-set_group_sub+2]) # init matrix

    # np.set_printoptions(precision=3, suppress=True)
    # list_yr_r1 = []
    # list_yr_p1 = []

    # # for table, create lists
    # corr_2d_list = []
    # pval_2d_list = []

    # # do for all years
    # for idx_1 in range(0,len(annual_header21)+1,1):
    #     r1, p1 = corrcoef(list_of_array_yr[idx_1])

    #     # print(len(list_of_array_yr[idx_1][0]))
    #     # print(r1.shape)
    #     list_yr_r1.append(r1[0,:])
    #     # print(p1)
    #     list_yr_p1.append(p1[0,:])

    #     corr_2d[idx_1,:] = r1[0,1:] # init matrix
    #     pval_2d[idx_1,:] = p1[0,1:] # init matrix

    #     list_r1 = ["%.3f" % x for x in r1[0,1:]]
    #     list_p1 = ["%.2e" % x for x in p1[0,1:]]

    #     # list_r1 = [int(i) for i in list(r1[0,1:])]
    #     # list_p1 = [int(i) for i in list(p1[0,1:])]

    #     corr_2d_list.append(list_r1)
    #     pval_2d_list.append(list_p1)


    # print("correlation matrix for age groups:", annual_header21, ",shape:",r1.shape)
    # print(hg.age_groups, sep = "\n")
    # print(*list_yr_r1, sep = "\n")
    # print("Two-tailed p-value matrix for age groups:", annual_header21, ",shape:",p1.shape)
    # # np.set_printoptions(precision=5, suppress=True)
    # np.set_printoptions(precision=3, suppress=False)
    # print(hg.age_groups, sep = "\n")
    # print(*list_yr_p1, sep = "\n")

    #################################################################################################
    # add legend, texts, additional styling
    font_weight_01 = 'bold'
    font_weight_02 = 'normal'
    font_weight_03 = 'italic'
    
    # collect age labels

    # todo:
    # https://matplotlib.org/3.1.1/gallery/text_labels_and_annotations/custom_legends.html
    age_labels = []
    age_group_list_reversed = list(reversed(hg.age_groups3))
    for idx_1 in range(srt_plot_idx,end_plot_idx,step_plot_idx):
        age_labels.append(age_group_list_reversed[idx_1])

    # # generate colors
    # cmap = plt.cm.coolwarm
    # heatmap_colors = cmap(np.linspace(0, 1, len(age_labels)))
    # custom_lines = []
    # custom_label = []
    # cnt_idx = 0
    # for idx_1 in range(srt_plot_idx,end_plot_idx,step_plot_idx):
    #     # custom_lines.append(Line2D([0], [0], color=heatmap_colors[cnt_idx], lw=1))
    #     custom_lines.append(Line2D([0], [0], color=hmtl_colors_list[idx_1+1], lw=1))
    #     custom_label.append(hg.age_groups3[idx_1])
    #     cnt_idx += 1

    # order labels manually:
    handles, labels = ax1[0].get_legend_handles_labels()
    print(labels)
    print(sum(option_labels),option_labels)
    if len(labels) > sum(option_labels) and sum(option_labels) != 0:
        # print(option_labels, sum(option_labels))
        order = list(range(0, sum(option_labels))) +\
             list(range(len(labels)-sum(option_labels), sum(option_labels)-1,-1)) 
        print(order)
    elif sum(option_labels) == 0:
        order = list(range(len(labels)-1,-1,-1)) 
        print(order)
    else:
        order = list(range(0, len(labels))) 
    ax1[0].legend([handles[idx] for idx in order],[labels[idx] for idx in order],\
        loc='center left', bbox_to_anchor=(1, 0.2), fontsize=8) # bbox_to_anchor=(1, 0.92)

    # ax1[0].legend(loc='center left', bbox_to_anchor=(1, 0.92), fontsize=8)

    # # addtional comments
    ax1[0].text(0.01, -0.10, label_des_02 + str(len(list_of_array_yr[0][0])) + ", " +\
         hg.annual_header21[0] + iso_date[4:] + ", s: destatis", horizontalalignment='left',\
             verticalalignment='center', transform=ax1[0].transAxes, fontsize=9,\
                  fontweight=font_weight_02, fontstyle= font_weight_03)
    # ax1[0].text(0.01, -0.13, label_des_07 + 'CorrVal:'+  str(CORRELATION_THRESHOLD)+ ', PVal:'+  str(PVALUE_THRESHOLD), horizontalalignment='left',verticalalignment='center', transform=ax1[0].transAxes, fontsize=8, fontweight=font_weight_02, fontstyle= font_weight_03)

       # add Top5
    if add_top5:
        print("add Top5")
        # age_groups_labels = list(reversed(hg.age_groups2))
        age_groups_labels = hg.age_groups2
        list_min_str_all_fill = list_min_str_all
        cnt_vt_00 = 0.95 # start value vertical
        cnt_ht_00 = 1.03 # start value horizontal
        ax1[0].text(cnt_ht_00, cnt_vt_00 , label_des_03 , horizontalalignment='left',\
            verticalalignment='center', transform=ax1[0].transAxes, fontsize=9, fontweight=font_weight_01)
        ax1[0].text(cnt_ht_00, cnt_vt_00 - 0.035, label_des_04 , horizontalalignment='left',\
            verticalalignment='center', transform=ax1[0].transAxes, fontsize=9, fontweight=font_weight_01)
        cnt_vt_01 = cnt_vt_00 - 0.04
        cnt_age = len(list_min_str_all)

        # adjust manually to show only first and last (Total)
        list_min_str_all_fill = []
        list_min_str_all_fill.append(list_min_str_all[-1])
        list_min_str_all_fill.append(list_min_str_all[0])
        age_groups_labels = []
        age_groups_labels.append(hg.age_groups2[-1]) 
        age_groups_labels.append(hg.age_groups2[0]) 
        

        for idx_1 in range(0,len(list_min_str_all_fill),1): 
            cnt_vt_01 -= 0.05
            cnt_age -= 1
            ax1[0].text(cnt_ht_00, cnt_vt_01, label_des_06 + age_groups_labels[idx_1], horizontalalignment='left',\
                verticalalignment='center', transform=ax1[0].transAxes, fontsize=8,fontweight=font_weight_01)
            cnt_vt_02 = cnt_vt_01
            for idx_2 in range(len(list_min_str_all_fill[0])):
                cnt_vt_02 -= 0.035
                ax1[0].text(cnt_ht_00, cnt_vt_02, str(idx_2 + 1) + label_des_05 + list_min_str_all_fill[idx_1][idx_2],\
                    horizontalalignment='left',verticalalignment='center',\
                        transform=ax1[0].transAxes, fontsize=8,fontweight=font_weight_02)
            cnt_vt_01 = cnt_vt_02
    
    # excess deaths
    ##################################################################################################
    # add new ax: table
    print("seasonal deaths")
    list_seasonal_deaths_ws_actal = [] 
    list_seasonal_deaths_ws_total = [] 
    list_seasonal_deaths_ws_lin5y = [] 
    array_seasonal_deaths_ws_actal = np.empty((len(hg.seasonal_header_01),len(age_groups_plot),), dtype=object) # table rows, table cols
    array_seasonal_deaths_ws_actal[:] = "-"
    array_seasonal_deaths_ws_total = np.empty((len(hg.seasonal_header_01),len(age_groups_plot),), dtype=object) # table rows, table cols
    array_seasonal_deaths_ws_total[:] = "-"
    array_seasonal_deaths_ws_lin5y = np.empty((len(hg.seasonal_header_01),len(age_groups_plot),), dtype=object) # table rows, table cols
    array_seasonal_deaths_ws_lin5y[:] = "-"
    array_seasonal_deaths_corona_lin5y = np.empty((1,len(age_groups_plot),), dtype=object) # table rows, table cols
    array_seasonal_deaths_corona_lin5y[:] = "-"
    for idx_1 in range(srt_plot_idx,end_plot_idx,step_plot_idx):
        list_seasonal_deaths_ws_actal_temp = []
        list_seasonal_deaths_ws_total_temp = []   
        x3 = np.arange(1, len(list_of_list_yrs_age_groups_stacked[idx_1])+1, 1) # cws
        y3 = list_of_list_yrs_age_groups_stacked[idx_1]
        cnt_obj = 0
        for idx_2 in range(1,len(seasonal_marker)-1,2):
            sum_ws_actal = sum(y3[seasonal_marker[idx_2]:seasonal_marker[idx_2]+12+14])
            sum_ws_total = sum(y3[seasonal_marker[idx_2]:seasonal_marker[idx_2+1]])
            list_seasonal_deaths_ws_actal_temp.append(sum_ws_actal)
            list_seasonal_deaths_ws_total_temp.append(sum_ws_total)
            array_seasonal_deaths_ws_actal[cnt_obj][idx_1] = str(sum_ws_actal)
            array_seasonal_deaths_ws_total[cnt_obj][idx_1] = str(sum_ws_total)
            cnt_obj += 1
            # print(seasonal_marker[idx_2], idx_2)
        list_seasonal_deaths_ws_total.append(list_seasonal_deaths_ws_total_temp)
        list_seasonal_deaths_ws_actal.append(list_seasonal_deaths_ws_actal_temp)
    print("\nlist_seasonal_deaths_ws_total" + ", len:", len(list_seasonal_deaths_ws_total))
    print(*list_seasonal_deaths_ws_actal, sep = "\n")
    print(*list_seasonal_deaths_ws_total, sep = "\n")


    for idx_1 in range(srt_plot_idx,end_plot_idx,step_plot_idx):
        x3 = np.arange(1, len(list_of_list_yrs_age_groups_stacked[idx_1])+1, 1) # cws
        y3 = list_of_list_yrs_age_groups_stacked[idx_1]
        y3_lin5 = list_lin_trends_y[idx_1][0:len(y3)]
        list_seasonal_deaths_ws_lin5y_temp = []
        cnt_obj = 0
        for idx_2 in range(1,len(seasonal_marker)-1,2):
            # linear trends:
            diff_y3 = y3[seasonal_marker[idx_2]-1:seasonal_marker[idx_2+1]] - y3_lin5[seasonal_marker[idx_2]-1:seasonal_marker[idx_2+1]]
            bin_mask_y3 = [1 if x >= 0 else 0 for x in diff_y3]
            # print(y3[seasonal_marker[idx_2]-1:seasonal_marker[idx_2+1]])
            # print(y3_lin5[seasonal_marker[idx_2]-1:seasonal_marker[idx_2+1]])
            # print(diff_y3 * bin_mask_y3)
            # print(bin_mask_y3)
            sum_ws_lin5y = round(sum(diff_y3 * bin_mask_y3))
            if idx_2 == len(seasonal_marker)-5: # -5 (2020)
                # ax1[0].fill_between(x3[seasonal_marker[idx_2]-1:seasonal_marker[idx_2+1]],\
                # y3[seasonal_marker[idx_2]-1:seasonal_marker[idx_2+1]],0,color="yellow",alpha=0.1,lw=0,zorder=0)
                print("1# Wave Special counting, CW10-20", diff_y3[-10:],bin_mask_y3[-10:],) # RKI, 1st wave
                sum_corona_lin5y = round(sum(diff_y3[-10:] * bin_mask_y3[-10:]))
                print(sum_corona_lin5y)
                array_seasonal_deaths_corona_lin5y[0][idx_1] = str(sum_corona_lin5y)


            list_seasonal_deaths_ws_lin5y_temp.append(sum_ws_lin5y)
            array_seasonal_deaths_ws_lin5y[cnt_obj][idx_1] = str(sum_ws_lin5y)
            cnt_obj += 1
            if age_groups_plot[idx_1] == 1:
                if plot_table_excess_death_lin5y:
                    ax1[0].fill_between(x3[seasonal_marker[idx_2]-1:seasonal_marker[idx_2+1]],\
                        y3[seasonal_marker[idx_2]-1:seasonal_marker[idx_2+1]]*bin_mask_y3,\
                            y3_lin5[seasonal_marker[idx_2]-1:seasonal_marker[idx_2+1]]*bin_mask_y3,bin_mask_y3,\
                                color="blue",alpha=0.3,lw=0,zorder=0)
                if plot_table_excess_death_total_ws and idx_1 == end_plot_idx-1:
                    ax1[0].fill_between(x3[seasonal_marker[idx_2]-1:seasonal_marker[idx_2+1]],\
                        y3[seasonal_marker[idx_2]-1:seasonal_marker[idx_2+1]],color="blue",alpha=0.3,lw=0,zorder=0)
                if plot_table_excess_death_smooth:
                    y3_len = len(y3[seasonal_marker[idx_2]-1:seasonal_marker[idx_2+1]])
                    y_filter_03 = savgol_filter(y3[seasonal_marker[idx_2]-1:seasonal_marker[idx_2+1]], 11, 3) # window size 51 (must be odd), polynomial order 3
                    ax1[0].fill_between(x3[seasonal_marker[idx_2]-1:seasonal_marker[idx_2+1]],\
                        y3[seasonal_marker[idx_2]-1:seasonal_marker[idx_2+1]],\
                            y_filter_03-2000, color="blue",alpha=0.3,lw=0,zorder=0)




        list_seasonal_deaths_ws_lin5y.append(list_seasonal_deaths_ws_lin5y_temp)
    print(*list_seasonal_deaths_ws_lin5y, sep = "\n")
    
    if plot_table_excess_death_lin5y:
        table1_data = array_seasonal_deaths_ws_lin5y
        table1_head = excess_des_01
    elif plot_table_excess_death_total_ws:
        table1_data = array_seasonal_deaths_ws_total
        table1_head = excess_des_02
    else:
        table1_data = array_seasonal_deaths_ws_lin5y
        table1_head = excess_des_01
    
    ##################################################################################################
    # add new ax: table
    # ax1[1].xaxis.set_visible(False) 
    # ax1[1].yaxis.set_visible(False)
    # ax1[1].patch.set_visible(False)
    ax1[1].axis('off')
    # ax1[1].axis('tight')
    # ax1[1].set_title(prediction_des_01, fontsize=11)

    table1 = ax1[1].table(
        cellText = table1_data, 
        rowLabels = hg.seasonal_header_01,  
        colLabels = hg.age_groups3,
        # loc = 8,# 'center',
        # cellLoc = 'right',
        # fontsize = 1, 
        bbox=[0.0,-5.0,1.22,6.0], # table position: [left,bottom,width,height]
        # edges="",
        )
    table1.auto_set_font_size(False)

    for key, cell in table1.get_celld().items():
        cell.set_linewidth(0.0)
        # cell.PAD = 0.0
        cell.get_text().set_fontsize(9)
        # cell.set_edgecolor("grey")
        cell.set_edgecolor("w")
        # cell.set_facecolor("green")
        # cell.get_text().set_color('red')
        # cell._loc = 'right'
        # cell.set_verticalalignment = 'center'

    for idx_2 in range(0,1,1):
        for idx_1 in range(0,len(age_labels),1):
            table1.get_celld()[(idx_2,idx_1)].set_linewidth(0.5)
            table1.get_celld()[(idx_2,idx_1)].PAD = 0.05
            # table1.get_celld()[(idx_2,idx_1)].get_text().set_fontweight(font_weight_01)
            table1.get_celld()[(idx_2,idx_1)].get_text().set_fontsize(8)
            # table1.get_celld()[(idx_2,idx_1)].get_text().set_horizontalalignment("right")
            # table1.get_celld()[(idx_2,idx_1)].set_edgecolor("w")
            # table1.get_celld()[(idx_2,idx_1)].visible_edges = 'vertical'
            # table1.get_celld()[(idx_2,idx_1)].visible_edges = 'horizontal'
            table1.get_celld()[(idx_2,idx_1)].set_edgecolor("white")
            table1.get_celld()[(idx_2,idx_1)].set_facecolor("blue")
            table1.get_celld()[(idx_2,idx_1)].set_alpha(0.3)
            # table1.get_celld()[(idx_2,idx_1)].get_text().set_color('white')
        
    for idx_2 in range(1,6,1):
        for idx_1 in range(0,len(age_labels),1):
            table1.get_celld()[(idx_2,idx_1)].set_fontsize(7.5)
            table1.get_celld()[(idx_2,idx_1)].set_linewidth(0.5)
            table1.get_celld()[(idx_2,idx_1)].PAD = 0.04
            table1.get_celld()[(idx_2,idx_1)].set_edgecolor("black")
            # table1.get_celld()[(idx_2,idx_1)].visible_edges = 'horizontal'
            table1.get_celld()[(idx_2,idx_1)].visible_edges = 'vertical'
    

    # table1.scale(1.4, 1.0) 
    ax1[1].text(0.6, 1.7,table1_head , horizontalalignment='center',\
        verticalalignment='center', transform=ax1[1].transAxes, fontsize=11)

    
    ##################################################################################################
    # add new ax: table
    # ax1[1].xaxis.set_visible(False) 
    # ax1[1].yaxis.set_visible(False)
    # ax1[1].patch.set_visible(False)
    ax1[2].axis('off')
    # ax1[1].axis('tight')
    # ax1[1].set_title(prediction_des_01, fontsize=11)


    plot_table_accuracy = False
    plot_table_accuracy = True

    if plot_table_accuracy:
        table2 = ax1[2].table(
            cellText = array_eval_accuracy_3yrs_02, 
            rowLabels = row_labels_evaluation, # annual_header21_reverse 
            colLabels = hg.age_groups3, 
            # loc = 'center',
            # cellLoc = 'center',
            # fontsize = 20, 
            bbox=[0.0,-7.7,1.22,6.0], # table position: [left,bottom,width,height]
            # edges="",
            )
        table2.auto_set_font_size(False)

        for key, cell in table2.get_celld().items():
            cell.set_linewidth(0.0)
            # cell.PAD = 0.0
            cell.get_text().set_fontsize(9)
            # cell.set_edgecolor("grey")
            cell.set_edgecolor("w")
            # cell.set_facecolor("green")
            # cell.get_text().set_color('red')
            # cell._loc = 'right'
            # cell.set_verticalalignment = 'center'

        for idx_2 in range(0,1,1):
            for idx_1 in range(0,len(age_labels),1):
                table2.get_celld()[(idx_2,idx_1)].set_linewidth(0.5)
                table2.get_celld()[(idx_2,idx_1)].PAD = 0.05
                # table2.get_celld()[(idx_2,idx_1)].get_text().set_fontweight(font_weight_01)
                table2.get_celld()[(idx_2,idx_1)].get_text().set_fontsize(8)
                # table2.get_celld()[(idx_2,idx_1)].get_text().set_horizontalalignment("right")
                # table2.get_celld()[(idx_2,idx_1)].set_edgecolor("w")
                # table2.get_celld()[(idx_2,idx_1)].visible_edges = 'vertical'
                # table2.get_celld()[(idx_2,idx_1)].visible_edges = 'horizontal'
                table2.get_celld()[(idx_2,idx_1)].set_edgecolor("white")
                table2.get_celld()[(idx_2,idx_1)].set_facecolor("green")
                table2.get_celld()[(idx_2,idx_1)].set_alpha(0.3)
                # table2.get_celld()[(idx_2,idx_1)].get_text().set_color('white')

        for idx_2 in range(1,7,1):
            for idx_1 in range(0,len(age_labels),1):
                table2.get_celld()[(idx_2,idx_1)].set_fontsize(8)
                table2.get_celld()[(idx_2,idx_1)].set_linewidth(0.5)
                table2.get_celld()[(idx_2,idx_1)].PAD = 0.05
                table2.get_celld()[(idx_2,idx_1)].set_edgecolor("black")
                # table2.get_celld()[(idx_2,idx_1)].visible_edges = 'horizontal'
                table2.get_celld()[(idx_2,idx_1)].visible_edges = 'vertical'

        # for idx_2 in range(1,len(annual_header21_reverse)+1,1):
        # for idx_2 in range(0,1,1):
        #     for idx_1 in range(0,len(age_labels),1):
        #         table1.get_celld()[(idx_2,idx_1)].get_text().set_fontweight(font_weight_01)
        #         table1.get_celld()[(idx_2,idx_1)].get_text().set_fontsize(15)
        # #         table1.get_celld()[(idx_2,idx_1)].set_edgecolor("black")
        # table1.scale(1.2, 2.4)
        # for key, cell in table1.get_celld().items():
        #     # cell.set_linewidth(0.8)
        #     # cell._loc = 'center'
        #     cell.get_text().set_fontsize(15)
        #     # cell.get_text().set_fontweight(font_weight_01)
        #     # cell.visible_edges = 'horizontal'
        #     # cell.set_verticalalignment = 'bottom'
        #     cell.set_text_props(va='center_baseline', ha='center')
        #     # cell.set_edgecolor("grey")

        ax1[2].text(0.5, -1.00, prediction_des_01, horizontalalignment='center',\
            verticalalignment='center', transform=ax1[2].transAxes, fontsize=11)
        ax1[2].text(0.01, -8.30, "Accuracy = P/(P+N), P:= Actual Value(t) ∈ Predicted Linear MinMaxRange, N:= Not(P)",\
            horizontalalignment='left',verticalalignment='center', transform=ax1[2].transAxes, fontsize=8,fontweight=font_weight_02)
        # # addtional comments
        # ax1[1].text(0.01, -1.20, label_des_02 + str(len(list_of_array_yr[0][0])) + " " + hg.annual_header21[0] + "("+ iso_date[4:] + ")" +", s: destatis",\
        #  horizontalalignment='left',verticalalignment='center', transform=ax1[1].transAxes, fontsize=9, fontweight=font_weight_02, fontstyle= font_weight_03, color="w")
        # ax1[1].text(0.01, -0.85, label_des_07 + 'CorrVal:'+  str(CORRELATION_THRESHOLD)+ ', PVal:'+  str(PVALUE_THRESHOLD),\
        #      horizontalalignment='left',verticalalignment='center', transform=ax1[1].transAxes, fontsize=8, fontweight=font_weight_02)


    # final options
    # fig1.tight_layout()
    # fig1.subplots_adjust(top=0.90)
    # fig1.subplots_adjust(bottom=0.10)
    # fig1.subplots_adjust(right = 0.80)

    fig1.subplots_adjust(top=0.90)
    fig1.subplots_adjust(bottom=0.20)
    fig1.subplots_adjust(right = 0.80)

    # export fig as jpg
    if plt_save_im:
        vers_02 = str(len(list_of_array_yr[0][0]))
        fig1.savefig(path_02 + name_02 + "_"  + vers_02 + "_" + lang_02 + '.jpg', dpi=fig1.dpi, bbox_inches='tight') # , pad_inches=0
        # fig1.savefig(path_02 + name_02 + "_"  + lang_02 + "_" + vers_02 + '.png', dpi=fig1.dpi)
    plt.show()


    

 
 

