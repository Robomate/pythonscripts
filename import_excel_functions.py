#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=======================================================================
# Purpose: Import excel files
# Version: 07/2019 Roboball (MattK.)
# Links: https://bodo-schoenfeld.de/excel-daten-mit-python-einlesen/
#=======================================================================
'''
import pandas as pd
import xlrd
import numpy as np
from pprint import pprint

# define globals
path = r'C:\Users\x\Desktop\Python\project_AT_code\test_pdf\Systemkonfiguration.xlsm'
sheet_list_backup = [
                    'Projekteinstellungen',
                    'Deckblatt',
                    'Inhaltsverzeichnis',
                    'Computername',
                    'Benutzer',
                    'PcAnywhere',
                    'TwinCAT',
                    'Panel',
                    'Portkonfiguration',
                    'Kreisfoerderer', #
                    'Zufuehrfoerderer', # 10
                    'LSP_Lienear_FDR', #
                    'Drehgeber', # 
                    'LS_Abtastungen', # 
                    'Transponderleser', # 
                    'Weichenüberwachungen', # 15
                    'Basiserfassungen', # 
                    'Linearspeicherverwalter', # 
                    'Abzugsverwalter', #
                    'Leertaschenverwalter', # 
                    'Blockaufgaben', # 20 
                    'Aufgabefachgenerator', # 
                    'Rückmeldungskanäle', # 
                    'Eventkanäle', # 
                    'Kommandokanäle', # 
                    'Projektkanäle', # 25
                    'Erfassungskanäle', # 
                    'Routen_PLC', # 
                    'Routen_PC',
                    'Versionen',
                    'Steuerschrank', # 30,  ab hier nur noch Erklärungen
                    'Verteiler',
                    'Pickspeicher',
                    'Linearspeicher',
                    'Sorter',
                    'SorterLight',
                    'BeladeplatzLiegeware',
                    'BeladeplatzHaengeware',
                    'Packplatz',
                    'Packstation',
                    'Anomalieplatz', # 40
                    'UebersichtTabellenblaetter',
                    'Flexspeicher',
                    'Kettenlängungsmessung',
                    'Tabelle1',
                    'Tabelle2',
                    'TempGlobaleVariablen',
                    'Schluesselwoerter',
                    'ArbeitsblattSystemkonfiguration' # 48, di_ und do_ vars
                    ]

def import_excel_sheets_pd(file_path, sheet_name):
    ''' import excel sheets '''
    return pd.read_excel(file_path, sheet_name=sheet_name)

def get_column_from_sheet(sheet, col):
    ''' get data from a sheet by column and save into a list  '''
    return [sheet.cell(i, col).value for i in range(1, sheet.nrows)] # get column

def get_data_from_sheet(sheet, col_dn, col_up):
    ''' get all data from a sheet and save into a list  
        dependency: get_column_from_sheet(sheet, col)
    '''
    data_list = []
    for col in range(col_dn, col_up):
        data_list.append(get_column_from_sheet(sheet, col)) 
    return data_list

# def print_sheet(sheet):
#     ''' print all data from an excel sheet '''
#     print ('Sheet name: %s' % sheet.name)
#     num_cols = sheet.ncols   # Number of columns
#     for row_idx in range(0, sheet.nrows):    # Iterate through rows
#         print ('Row: %s' % row_idx)   # Print row number
#         for col_idx in range(0, num_cols):  # Iterate through columns
#             cell_obj = sheet.cell(row_idx, col_idx)  # Get cell object by row, col
#             print ('Column: [%s] cell_obj: [%s]' % (col_idx, cell_obj))

def print_sheet(sheet):
    ''' print all data from an excel sheet '''
    print ('Sheet name: %s' % sheet.name)
    num_cols = sheet.ncols   # Number of columns
    for row_idx in range(0, sheet.nrows):    # Iterate through rows
        print ('Row: %s' % row_idx)   # Print row number
        for col_idx in range(0, num_cols):  # Iterate through columns
            cell_obj = sheet.cell(row_idx, col_idx)  # Get cell object by row, col
            print (cell_obj.value)



if __name__ == '__main__':

    ###########
    # XLRD
    ###########

    # read in sheet names
    book = xlrd.open_workbook(path, on_demand=True, encoding_override = "utf-8")
    sheet_list = book.sheet_names()
    # pprint (sheet_list)

    

    # read in data from sheets
    sheet = book.sheet_by_index(9)
    print_sheet(sheet)
    num_cols = sheet.ncols   # Number of columns

    # get data per sheet arranged in list of columns
    y_data_09 = get_data_from_sheet(sheet, 1, num_cols) # KF data
    # pprint(y_data_09)

    

    # as lists
    # y_data_01 = [sheet.cell(i, 0).value for i in range(1, sheet.nrows)] # 1. spalte
    # y_data_02 = [sheet.cell(i, 1).value for i in range(1, sheet.nrows)] # 2. spalte
    # y_data_03 = [sheet.cell(i, 2).value for i in range(1, sheet.nrows)] # 3. spalte

    # as np arrays
    # y_data_01 = np.asarray([sheet.cell(i, 0).value for i in range(1, sheet.nrows)]) # 1. spalte
    # y_data_02 = np.asarray([sheet.cell(i, 1).value for i in range(1, sheet.nrows)]) # 2. spalte
    # y_data_03 = np.asarray([sheet.cell(i, 2).value for i in range(1, sheet.nrows)]) # 3. spalte

    # print (x_data)
    # pprint (y_data_02) # Nr.
    # pprint (y_data_03) # Beschreibung
    
    # create a list
    # data_list = [y_data_01, y_data_02, y_data_03]
    # for item in data_list:
    #     pprint (data_list)






    ###########
    # pandas
    ###########

    # read in data from sheets
    # data_01 = import_excel_sheets_pd(path, sheet_list[48])
    # print (data_01)

    # bsp fuer antriebe: outputs, 9-11
    # data_KF = import_excel_sheets_pd(path, sheet_list[9])
    # data_ZF = import_excel_sheets_pd(path, sheet_list[10]) #7 PundF
    # data_SF = import_excel_sheets_pd(path, sheet_list[11])
    #print (data_KF)
    # print (data_ZF)
    # print (data_SF)

    





    

