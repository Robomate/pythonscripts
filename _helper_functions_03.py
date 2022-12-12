#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ST-Twincat2-AutoMapping
Purpose: Helper Functions
Version: 01/2020 Roboball (MattK.)
"""
import os
import pandas as pd

# define functions

###############################################################
# functions: for objektliste, systemkonfiguration
###############################################################

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

def print_sheet(sheet):
    ''' print all data from an excel sheet '''
    print ('Sheet name: %s' % sheet.name)
    num_cols = sheet.ncols   # Number of columns
    for row_idx in range(0, sheet.nrows):    # Iterate through rows
        print ('Row: %s' % row_idx)   # Print row number
        for col_idx in range(0, num_cols):  # Iterate through columns
            cell_obj = sheet.cell(row_idx, col_idx)  # Get cell object by row, col
            print (cell_obj.value)

def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]

def get_row_from_sheet(
                        sheet_object,
                        set_row, 
                        set_col,
                        print_opt,
                        step_size, 
                        ):
    ''' get_col_from_sheet '''
    list_row = []
    num_cols = sheet_object.ncols   # Number of columns
    # print("\nCols: Outputs") 
    for idx_1 in range(set_col,num_cols,step_size):
        list_row.append(sheet_object.cell_value(set_row-1, idx_1-1))
        if print_opt:
            print(sheet_object.cell_type(set_row-1, idx_1-1)) # type: 1 = text, type: 0 = empty, row, col
            print(sheet_object.cell_value(set_row-1, idx_1-1)) # row, col
    
    return list_row

def get_col_from_sheet(
                        sheet_object,
                        set_row, 
                        set_col,
                        print_opt,
                        step_size, 
                        ):
    ''' get_col_from_sheet '''
    list_col = []
    num_rows = sheet_object.nrows   # Number of columns
    # print("\nCols: Outputs") 
    for idx_1 in range(set_row,num_rows+1,step_size):
        list_col.append(sheet_object.cell_value(idx_1-1, set_col-1))
        if print_opt:
            print(sheet_object.cell_type(idx_1-1, set_col-1)) # type: 1 = text, type: 0 = empty, row, col
            print(sheet_object.cell_value(idx_1-1, set_col-1)) # row, col
    
    return list_col

###############################################################
# functions: for mapping
###############################################################

def get_io_data(
                path,
                data_file,
                ):
    ''' filter by io variables: di do, description, links '''
    fname = os.path.join(path,data_file) # open exp file
    content_list_dido_1 = read_txt_file(fname) # put all content into a list of string elements
    # print(*content_list_1, sep = "\n")
    content_list_dido_2 = search_list("di_", content_list_dido_1) # filter by di 
    # print(*content_list_2, sep = "\n")
    content_list_dido_3 = search_list("do_" , content_list_dido_1) # filter by do
    # print(*content_list_3, sep = "\n")

    substring_1 = "%" # set substring
    substring_2 = "(*" # set substring
    substring_3 = "~{L" # set substring
    content = content_list_dido_2 # set string list to search in
    di_var, di_des, di_lks = search_io_decription_link(substring_1, substring_2, substring_3, content)
    content = content_list_dido_3 # set string list to search in
    do_var, do_des, do_lks = search_io_decription_link(substring_1, substring_2, substring_3, content)

    # io clean-up data
    di_var = clean_up_empty_strings_from_list(di_var)
    di_des = clean_up_empty_strings_from_list(di_des)
    di_lks = clean_up_empty_strings_from_list(di_lks)
    do_var = clean_up_empty_strings_from_list(do_var)
    do_des = clean_up_empty_strings_from_list(do_des)
    do_lks = clean_up_empty_strings_from_list(do_lks)
    # io complete data
    io_var = di_var + do_var
    io_des = di_des + do_des
    io_lks = di_lks + do_lks

    io_variables_and_io_description = []
    for idx in range(len(io_var)):
        io_variables_and_io_description_temp = io_var[idx] + " " + io_des[idx]
        io_variables_and_io_description.append(io_variables_and_io_description_temp)
    # print(*io_variables_and_io_description, sep = "\n")

    # io empty dummy lists
    io_empty = [0] * len(io_var)
    di_empty = [0] * len(di_var)
    do_empty = [0] * len(do_var)

    return io_var, io_des, io_lks,\
           di_var, di_des, di_lks,\
           do_var, do_des, do_lks,\
           io_empty, di_empty, do_empty


def get_arr_len(array):
	''' get array length '''
	return len(array)

def read_txt_file(fname):
    ''' read in txt file into a list of string elements '''
    with open(fname) as f:
        content = f.readlines()
    return [x.strip() for x in content] # content into list

def write_txt_file(path, data_file, content_list):
    ''' write to txt file '''
    fname = os.path.join(path, data_file) # open exp file
    content_list = map(lambda x: x + '\n', content_list)
    with open(fname,"w+") as f:
        f.writelines(content_list)
    return print("** Write to txt file complete **")

def search_list(search_str, content):
    ''' search list and return all results by a list '''
    return [s for s in content if search_str in s]

def search_substr_in_str(substring, string):
    ''' search for index of an substring in a string '''
    if substring in string:
        return string.index(substring)
    else:
        return -1

def concat_two_lists(list_1, list_2, divider):
    ''' concat_two_lists '''
    concat_list = []

    for idx in range(len(list_1)):
        concat_list_temp = list_1[idx] +  divider +  list_2[idx]
        concat_list.append(concat_list_temp)

    return concat_list

def concat_two_list_of_lists(list_of_lists_1,list_of_lists_2, divider):
    ''' concat_two_list_of_lists '''
    return_list_of_lists = []
    for idx in range(len(list_of_lists_1)):
        content = concat_two_lists(list_of_lists_1[idx], list_of_lists_2[idx], divider)
        return_list_of_lists.append(content)

    return return_list_of_lists

def search_io_decription_link(substring_1, substring_2, substring_3, content):
    ''' search for io variables, description and links as strings'''
    io_list = []
    des_list = []
    link_list = []
    for str_row in content:
        string = str_row
        idx_1 = search_substr_in_str(substring_1, string) # call search char function
        # print("idx_1:", idx_1)
        idx_2 = search_substr_in_str(substring_2, string) # call search char function
        # print("idx_2:", idx_2)
        idx_3 = search_substr_in_str(substring_3, string) # call search char function
        # print("idx_3:", idx_3)
        io_list.append(str_row[0:idx_1 -3])
        des_list.append(str_row[idx_2:idx_3]+ " *)")  
        link_list.append(str_row[idx_3:])  
    return io_list, des_list, link_list

def find_index_of_substring_in_string(substring, content):
    ''' find_index_of_substring_in_string'''
    return_list = []
    for str_row in content:
        string = str_row
        # print("str_row:", str_row)
        idx_1 = search_substr_in_str(substring, string) # call search char function
        # print("idx_1:", idx_1)
        if idx_1 != -1:
            return_list.append(idx_1)
    return return_list

def find_index_of_substring_in_stringlist(substring, content):
    ''' find_index_of_substring_in_stringlist:
        return idxs of a list, return idx of a substring e.g. Pos of all elements
    '''
    return_list_idx_content = []
    return_list_idx_of_pos_substring = []
    for idx in range(len(content)):
        # print("idx list", idx )
        idx_1 = search_substr_in_str(substring, content[idx]) # call search char function
        # print("idx_1:", idx_1)
        if idx_1 != -1:
            return_list_idx_content.append(idx)
            return_list_idx_of_pos_substring.append(idx_1)
    return return_list_idx_content, return_list_idx_of_pos_substring 


def print_list_by_index_list(index_list, print_list):
    ''' print_list_by_index_list '''
    return_print_list = []
    for idx in index_list:
        print(print_list[idx])
        return_print_list.append(print_list[idx])
    return return_print_list

def get_list_by_index_list(index_list, search_list):
    ''' get_list_by_index_list '''
    return_list = []
    for idx in index_list:
        return_list.append(search_list[idx])
    return return_list

def search_systemkonfiguration_tp(substring_1, substring_2, index_list, content):
    ''' search_systemkonfiguration_tp '''
    pos_list = []
    unitid_list = []
    description_list = []
    for idx in index_list:
        string = content[idx]
        idx_1 = search_substr_in_str(substring_1, string) # call search char function
        idx_2 = search_substr_in_str(substring_2, string) # call search char function
        pos_list.append(string[idx_1+5:idx_1+10])
        unitid_list.append(string[idx_2+3:idx_2+10])
        description_list.append(string[3:idx_1+10])
    return pos_list, unitid_list, description_list

def clean_up_empty_strings_from_list(string_list):
    ''' clean_up_empty_strings_from_list '''
    return_list = []
    for idx in range(len(string_list)):
        return_list.append(string_list[idx].strip())

    return return_list

def find_index_list_of_search_string_list(search_string_list,content_list):
    ''' find_index_list_of_search_string_list'''
    return_list = []
    for idx in range(len(search_string_list)):
        return_temp = find_index_of_substring_in_stringlist(search_string_list[idx], content_list)
        # print("return_temp", return_temp)
        if return_temp != []:
            return_list.append(return_temp[0][0])
    return return_list 

def search_nested(
                    key_word_list,
                    where_to_search, # io_variables, io_description, io_links
                    io_variables, # io_variables, 
                    io_description, # io_description, 
                    io_links, # io_links
                    ):
    ''' search_nested '''
    io_variables_temp = io_variables
    io_description_temp = io_description
    io_links_temp = io_links

    for idx in range(len(key_word_list)):
        if where_to_search == "io_variables": 
            list_idx_temp, _ = find_index_of_substring_in_stringlist(key_word_list[idx], io_variables_temp)
        elif where_to_search == "io_description": 
            list_idx_temp, _ = find_index_of_substring_in_stringlist(key_word_list[idx], io_description_temp)
        elif where_to_search == "io_links": 
            list_idx_temp, _ = find_index_of_substring_in_stringlist(key_word_list[idx], io_links_temp)

        io_variables_temp = get_list_by_index_list(list_idx_temp , io_variables_temp)
        io_description_temp = get_list_by_index_list(list_idx_temp, io_description_temp)
        io_links_temp = get_list_by_index_list(list_idx_temp , io_links_temp)
        # print("\n" + key_word_list[idx])  
        # print(*io_description_temp, sep = "\n")

    return io_variables_temp, io_description_temp, io_links_temp

def replace_diS_by_doY_in_string_list(
                    substring_to_be_replaced, # substring_to_be_replaced
                    substring_replacement_01, # substring_replacement_01
                    substring_replacement_02, # substring_replacement_02 
                    string_list, # string_list
                    cng_adder, # cng_adder
                    ):
    ''' replace_substring_in_string_list '''
    return_list = []
    cng_adder_list_temp = []
    return_list_temp = find_index_of_substring_in_string(substring_to_be_replaced, string_list)
    for idx in range(len(string_list)):
        cng_adder_list_temp.append(str(int(string_list[idx][return_list_temp[idx]+1:]) + cng_adder))
        # print("\n"+"cng_adder_list_temp[idx]  ",cng_adder_list_temp[idx] )  
    print("\n"+"cng_adder_list_temp ") 
    print(*cng_adder_list_temp, sep = "\n")

    for idx in range(len(string_list)):
        return_list.append(
                            string_list[idx][0:1]
                            + substring_replacement_01
                            + string_list[idx][2:return_list_temp[idx]] 
                            + substring_replacement_02
                            + cng_adder_list_temp[idx]
                            )
    return return_list

def sort_two_lists_by_first_list(first_list,second_list):
    ''' sort_two_lists_by_first_list'''
    return_list = []
    for idx in range(len(first_list)):
        return_list.append([first_list[idx], second_list[idx]])
    return_list.sort()

    return return_list 

def sort_multi_lists_by_first_list(first_list, multi_list):
    ''' sort_two_lists_by_first_list'''
    return_list = []
    for idx in range(len(first_list)):
        nested_list = []
        nested_list.append(first_list[idx])
        for element in multi_list:
            nested_list.append(element[idx])
        return_list.append(nested_list)
    return_list.sort()

    return return_list 

def search_by_depth_one_and_ret_lists(
                                        search_str_01,  # e.g. Anomalie
                                        search_str_02,  # e.g. Pos
                                        search_list_01, # content_list_idx
                                        io_var,
                                        io_des, # content_list_idx_uid
                                        io_lks,
                                        start_idx_uid,
                                        end_idx_uid,
                                        start_idx_hpo,
                                        end_idx_hpo,
                                        print_matrix_list,
                                        ):
    ''' search_by_depth_one_and_ret_lists'''
    content_list_idx, _ = find_index_of_substring_in_stringlist(search_str_01, search_list_01) # return_list_idx_content, return_list_idx_of_pos_substring 
    content_list_var = get_list_by_index_list(content_list_idx, io_var)
    content_list_des = get_list_by_index_list(content_list_idx, io_des)
    content_list_lks = get_list_by_index_list(content_list_idx, io_lks)
    # print("content_list")
    # print(*content_list_var, sep = "\n")
    # print(*content_list_des, sep = "\n")
    _, content_list_idx_uid = find_index_of_substring_in_stringlist(search_str_02, content_list_des) # return_list_idx_content, return_list_idx_of_pos_substring
    content_list_uid = []
    content_list_hpo = []
    for idx in range(len(content_list_idx_uid)):
        content_list_uid.append(content_list_des[idx][content_list_idx_uid[idx]\
                                       + start_idx_uid :content_list_idx_uid[idx] + end_idx_uid])
        content_list_hpo.append(content_list_des[idx][content_list_idx_uid[idx]\
                                       + start_idx_hpo :content_list_idx_uid[idx] + end_idx_hpo])
    # print("content_list_uid")
    # print(*content_list_uid, sep = "\n")
    # print(*content_list_hpo, sep = "\n")

    multi_lists_sorted = sort_multi_lists_by_first_list(
                                                        content_list_uid, # first_list 
                                                        [ 
                                                        content_list_var,
                                                        content_list_des,
                                                        content_list_hpo,
                                                        content_list_lks,
                                                        ]# multi_list
                                                        )
    
    if print_matrix_list:
        print("\n"+ search_str_01 + ", len:", len(content_list_uid))
        print(*multi_lists_sorted, sep = "\n")

    content_list_uid = []
    content_list_var = []
    content_list_des = []
    content_list_hpo = []
    content_list_lks = []
    for idx in range(len(multi_lists_sorted)):
        content_list_uid.append(multi_lists_sorted[idx][0])
        content_list_var.append(multi_lists_sorted[idx][1])
        content_list_des.append(multi_lists_sorted[idx][2])
        content_list_hpo.append(multi_lists_sorted[idx][3])
        content_list_lks.append(multi_lists_sorted[idx][4])
    
    return content_list_uid, content_list_var, content_list_des, content_list_hpo, content_list_lks



