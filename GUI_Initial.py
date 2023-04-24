import PySimpleGUI as sg  # pip install pysimplegui
from pathlib import Path  # core python module
import time
import numpy as np
import os
import pickle
import re

from PAC_Classes import Parent, Action, Child, Disassembly, PACUnit # Import PAC Classes
AllParents = []
AllActions = []
AllChildren = []
AllDisassemblies = []
# Brug den her instance til at definere Parent, Action, Child eller Disassembly ID som et objekt. Derefter tilføj desc og andet
#instance = Parent(cells[row][0])
 #       AllParents.append(instance)
#instance.Desc = 'Hej'

setup_type = ["Rectangular setup", "Circular setup", "Table setup"]
BOM_array = []
BOM_array_disp = []
CI_list = []
headings_list = [('Part name', True), ('Quantity', True), ('M rec', False), ('M res', False), ('M collected EoL', False), ('V', False), ('W', False), ('M c', False), ('Wf', False), ('Wc', False), ('L', False), ('Lav', False)]
disassembly_action_type = ["Destructive", "Semi-Destructive", "Non destructive"]
tool_type = ["Hand", "Drill", "Hammer", "Screwdriver"]
action_type = ["Separate", "Remove", "Unscrew", "Disconnect"]
EoL = ["Recyclable", "Non Recyclable"]
yes_no = ["Yes", "No"]

PAC_unit = 1

origin_PAC_unit = [["Origin here"]]
origin_global = ["Origin here"]
check_PAC_ID = []

#First column is the actual row counter, the second is the visible row counter, the third is the visibility value 1 or 0 and the fourth is the PAC unit number
row_parent_DF = [[0], [0], [0], [1]]
row_action_DF = [[0], [0], [0], [1]]
row_child_DF = [[0], [0], [0], [1]]
row_action = [[0], [1], [1], [1]]
row_child = [[0], [1], [1], [1]]
children_name_ID = [[], []]
parent_DF_diff = [0]
action_DF_diff = [0]
child_DF_diff = [0]
action_diff = [0]
child_diff = [0]
error = [0]
origin_number_parent_DF = [[]]
origin_number_action_DF = [[]]
origin_number_child_DF = [[]]


#  Handling BOM heading lists
def toggle_CI(headings_list, index_list, vis):
    updated_headings = headings_list.copy()
    index_list = index_list if isinstance(index_list,list) else [index_list]
    for index in index_list:
        value, status = updated_headings[index]
        updated_headings[index] = (value, vis)
    sorted_headings = sorted(updated_headings, key=lambda x: updated_headings.index(x))
    return headings_list, [value for value, status in sorted_headings if status]
headings_list, headings = toggle_CI(headings_list, 1, True)
headings_list, headings_RR = toggle_CI(headings_list, [2,4], True)
headings_list, headings_RE = toggle_CI(headings_list, [3,4], True)
headings_list, headings_MCI = toggle_CI(headings_list, list(range(5,12)), True)
headings_list, headings_RRRE = toggle_CI(headings_list, list(range(2,5)), True)
headings_list, headings_RRMCI = toggle_CI(headings_list, [2,4,5,6,7,8,9,10,11], True)
headings_list, headings_REMCI = toggle_CI(headings_list, list(range(3,12)), True)
headings_list, headings_RRREMCI = toggle_CI(headings_list, list(range(2,12)), True)
prev_table = "-TABLE-"

def visibility_func(CI_list, prev_table):
    vis_string = ""
    if "RR" in CI_list:
        vis_string +="RR"
    if "RE" in CI_list:
        vis_string += "RE"
    if "MCI" in CI_list:
        vis_string += "MCI"
    window[prev_table].update(visible=False)
    next_table = f"-TABLE{vis_string}-"
    window[next_table].update(visible=True)
    return next_table
def BOM_append(BOM_array, CI_list, prev_table):
    appendlist = [values["BOM names"], values["BOM quantity"]]
    inputlist = ["BOM names", "BOM quantity"]
    if "RR" in CI_list and "RE" in CI_list:
        appendlist.extend([values["-MREC-"], values["-MRES-"], values["-MEOL-"]])
        inputlist.extend(["-MREC-", "-MRES-", "-MEOL-"])
    elif "RR" in CI_list:
        appendlist.extend([values["-MREC-"], values["-MEOL-"]])
        inputlist.extend(["-MREC-", "-MEOL-"])
    elif "RE" in CI_list:
        appendlist.extend([values["-MRES-"], values["-MEOL-"]])
        inputlist.extend(["-MRES-", "-MEOL-"])
    if "MCI" in CI_list:
        appendlist.extend([values["-V-"], values["-W-"], values["-MC-"], values["-WF-"], values["-WC-"], values["-L-"], values["-LAV-"]])
        inputlist.extend(["-V-", "-W-", "-MC-", "-WF-", "-WC-", "-L-", "-LAV-"])
    appendlisterror = appendlist[1:]
    try:
        errorlist = [int(num) if num.isdigit() else float(num) for num in appendlisterror]
    except:
        sg.popup_error("Please fill out all fields with numbers")
        return
    BOM_array.append(appendlist)
    for input in inputlist:
        window[input].update('')
    return BOM_array

def get_BOM_names():
    BOM_names = []
    for i in range(len(BOM_array_disp)):
        if int(BOM_array_disp[i][1]):
            BOM_names.append(BOM_array[i][0])
    return BOM_names

def BOM_quant_left(names_quant, BOM):
    #  Takes a 2D array with names and quantities, ex: [[hest, 1],[abe, 2],[elefant, 6]]. And the BOM to change
    #  Returns a BOM list with the remaining quantities on the list
    for elem in names_quant:
        for item in BOM:
            if item[0] == elem[0]:
                item[1] = int(item[1]) - int(elem[1])
    return BOM

#This function creates the row of the parent disassembly failure, it does so by the program calling a defined row when starting
# and then being able to add similar rows to that.
def create_parent_DF(row_counter, row_number_view):
    # Input: row_counter is the actual row which is about to be showed, counting visible and non visible.
    # Input: row_number_view is the row number for the currently visible rows
    # Output: this function returns a row with the parent DF failure setup, with combo and input key named after the row_counter

    if row_counter == 0:
        row = [sg.pin(
            sg.Column(
                [[
                    sg.Button("X", key=('-DEL_PARENT_DF-', row_counter)),
                    sg.T("Failure description:"), sg.I(key=f"-PARENT_FAILURE_DESCRIPTION_{row_counter}-", s=25),
                    sg.T("Disassembly type:"),
                    sg.Combo(disassembly_action_type, key=f"-PARENT_DISASSEMBLY_TYPE_{row_counter}-"), sg.T("Tool:"),
                    sg.Combo(tool_type, key=f"-PARENT_TOOL_TYPE_{row_counter}-"),
                    sg.T("Origin of DF:"), sg.Combo(origin_global, key=f"-PARENT_ORIGIN_{row_counter}-", readonly=True),
                    sg.T(f"DF ID: {row_number_view}", key=f"-PARENT_DF_ID_{row_counter}-")]],
                justification="center", key=('-ROW_PARENT_DF-', row_counter), visible=False
            ))]
        return row
    else:
        row =  [sg.pin(
        sg.Column(
            [[
              sg.Button("X", key=('-DEL_PARENT_DF-', row_counter)),
              sg.T("Failure description:"), sg.I(key=f"-PARENT_FAILURE_DESCRIPTION_{row_counter}-", s=25), sg.T("Disassembly type:"),
              sg.Combo(disassembly_action_type, key=f"-PARENT_DISASSEMBLY_TYPE_{row_counter}-"), sg.T("Tool:"),
              sg.Combo(tool_type, key=f"-PARENT_TOOL_TYPE_{row_counter}-"),
              sg.T("Origin of DF:"), sg.Combo(origin_global, key=f"-PARENT_ORIGIN_{row_counter}-", readonly=True),
              sg.T(f"DF ID: {row_number_view}", key=f"-PARENT_DF_ID_{row_counter}-")]],
            justification="center", key=('-ROW_PARENT_DF-', row_counter)
        ))]
        return row

def create_action_DF(row_counter, row_number_view):
    # Input: row_counter is the actual row which is about to be showed, counting visible and non visible.
    # Input: row_number_view is the row number for the currently visible rows
    # Output: this function returns a row with the action DF failure setup, with combo and input key named after the row_counter
    origin_without_actions = []
    for values in range(len(origin_PAC_unit[PAC_unit-1])):
        if origin_PAC_unit[PAC_unit-1][values].split("-")[0] != f"{PAC_unit}A1":
            origin_without_actions.append(origin_PAC_unit[PAC_unit-1][values])

    action_ID_for_DF = list(range(1,row_action[1][-1]+1))
    if row_counter == 0:
        row = [sg.pin(
            sg.Column(
                [[
                    sg.Button("X", key=('-DEL_ACTION_DF-', row_counter)),
                    sg.T("Affected action:"), sg.Combo(action_ID_for_DF, key=f"-ACTION_ID_FOR_DF_{row_counter}-"),
                    sg.T("Failure description:"), sg.I(key=f"-ACTION_FAILURE_DESCRIPTION_{row_counter}-", s=25),
                    sg.T("Disassembly type:"),
                    sg.Combo(disassembly_action_type, key=f"-ACTION_DISASSEMBLY_TYPE_{row_counter}-"), sg.T("Tool:"),
                    sg.Combo(tool_type, key=f"-ACTION_TOOL_TYPE_{row_counter}-"),
                    sg.T("Origin of DF:"), sg.Combo(origin_without_actions, key=f"-ACTION_ORIGIN_{row_counter}-", readonly=True),
                    sg.T(f"DF ID: {row_number_view}", key=f"-ACTION_DF_ID_{row_counter}-")]],
                justification="center", key=('-ROW_ACTION_DF-', row_counter), visible=False
            ))]
        return row
    else:
        row =  [sg.pin(
        sg.Column(
            [[
              sg.Button("X", key=('-DEL_ACTION_DF-', row_counter)),
              sg.T("Affected action:"), sg.Combo(action_ID_for_DF, key=f"-ACTION_ID_FOR_DF_{row_counter}-"),
              sg.T("Failure description:"), sg.I(key=f"-ACTION_FAILURE_DESCRIPTION_{row_counter}-", s=25), sg.T("Disassembly type:"),
              sg.Combo(disassembly_action_type, key=f"-ACTION_DISASSEMBLY_TYPE_{row_counter}-"), sg.T("Tool:"),
              sg.Combo(tool_type, key=f"-ACTION_TOOL_TYPE_{row_counter}-"),
              sg.T("Origin of DF:"), sg.Combo(origin_without_actions, key=f"-ACTION_ORIGIN_{row_counter}-", readonly=True),
              sg.T(f"DF ID: {row_number_view}", key=f"-ACTION_DF_ID_{row_counter}-")]],
            justification="center", key=('-ROW_ACTION_DF-', row_counter)
        ))]
        return row
#test
def create_child_DF(row_counter, row_number_view):
    # Input: row_counter is the actual row which is about to be showed, counting visible and non visible.
    # Input: row_number_view is the row number for the currently visible rows
    # Output: this function returns a row with the child DF failure setup, with combo and input key named after the row_counter
    child_ID_for_DF = list(range(1,row_child[1][-1]+1))
    if row_counter == 0:
        row = [sg.pin(
            sg.Column(
                [[
                    sg.Button("X", key=('-DEL_CHILD_DF-', row_counter)),
                    sg.T("Affected child:"), sg.Combo(child_ID_for_DF,key=f"-CHILD_ID_FOR_DF_{row_counter}-"),
                    sg.T("Failure description:"), sg.I(key=f"-CHILD_FAILURE_DESCRIPTION_{row_counter}-", s=25),
                    sg.T("Disassembly type:"),
                    sg.Combo(disassembly_action_type, key=f"-CHILD_DISASSEMBLY_TYPE_{row_counter}-"), sg.T("Tool:"),
                    sg.Combo(tool_type, key=f"-CHILD_TOOL_TYPE_{row_counter}-"),
                    sg.T("Origin of DF:"), sg.Combo(origin_PAC_unit[PAC_unit-1], key=f"-CHILD_ORIGIN_{row_counter}-", readonly=True),
                    sg.T(f"DF ID: {row_number_view}", key=f"-CHILD_DF_ID_{row_counter}-")]],
                justification="center", key=('-ROW_CHILD_DF-', row_counter), visible=False
            ))]
        return row
    else:
        row =  [sg.pin(
        sg.Column(
            [[
              sg.Button("X", key=('-DEL_CHILD_DF-', row_counter)),
              sg.T("Affected child:"), sg.Combo(child_ID_for_DF,key=f"-CHILD_ID_FOR_DF_{row_counter}-"),
              sg.T("Failure description:"), sg.I(key=f"-CHILD_FAILURE_DESCRIPTION_{row_counter}-", s=25), sg.T("Disassembly type:"),
              sg.Combo(disassembly_action_type, key=f"-CHILD_DISASSEMBLY_TYPE_{row_counter}-"), sg.T("Tool:"),
              sg.Combo(tool_type, key=f"-CHILD_TOOL_TYPE_{row_counter}-"),
              sg.T("Origin of DF:"), sg.Combo(origin_PAC_unit[PAC_unit-1], key=f"-CHILD_ORIGIN_{row_counter}-", readonly=True),
              sg.T(f"DF ID: {row_number_view}", key=f"-CHILD_DF_ID_{row_counter}-")]],
            justification="center", key=('-ROW_CHILD_DF-', row_counter)
        ))]
        return row

def create_action(row_counter, row_number_view):
    # Input: row_counter is the actual row which is about to be showed, counting visible and non visible.
    # Input: row_number_view is the row number for the currently visible rows
    # Output: this function returns a row with the action setup. These rows start from the second action visible, because we always need atleast one action
    if row_counter == 0:
        row = [sg.pin(
            sg.Column(
                [[
                    sg.Button("X", key=('-DEL_ACTION-', row_counter)),
                    sg.T("Action name:"), sg.Combo(action_type, key=f"-ACTION_TYPE_{row_counter}-", s=25), sg.T("Action description:"),
                    sg.I(key=f"-ACTION_DESCRIPTION_{row_counter}-", s=25), sg.T("Action times:"), sg.I(key=f"-ACTION_TIMES_NUMBER_{row_counter}-", s=5),
                    sg.T("Tool:"), sg.Combo(tool_type, key=f"-ACTION_TOOL_TYPE_{row_counter}-"),
                    sg.T(f"Action PAC ID: {row_number_view}", key=f"-ACTION_PAC_ID_{row_counter}-")]],
                justification="center", key=('-ROW_ACTION-', row_counter), visible=False
            ))]
        return row
    else:
        row =  [sg.pin(
        sg.Column(
            [[
              sg.Button("X", key=('-DEL_ACTION-', row_counter)),
              sg.T("Action name:"), sg.Combo(action_type, key=f"-ACTION_TYPE_{row_counter}-", s=25),
              sg.I(key=f"-ACTION_DESCRIPTION_{row_counter}-", s=25, visible=False), sg.T("Action times:"), sg.I(key=f"-ACTION_TIMES_NUMBER_{row_counter}-", s=5),
              sg.T("Tool:"), sg.Combo(tool_type, key=f"-ACTION_TOOL_TYPE_{row_counter}-"), sg.T(f"Action PAC ID: {row_number_view}", key=f"-ACTION_PAC_ID_{row_counter}-")]],
            justification="center", key=('-ROW_ACTION-', row_counter)
        ))]
        return row

def create_child(row_counter, row_number_view):
    # Input: row_counter is the actual row which is about to be showed, counting visible and non visible.
    # Input: row_number_view is the row number for the currently visible rows
    # Output: this function returns a row with the child setup. These rows start from the second action visible, because we always need atleast one action
    if row_counter == 0:
        row = [sg.pin(
            sg.Column(
                [[
                    sg.Button("X", key=('-DEL_CHILD-', row_counter)),
                    sg.T("Child name:"), sg.Combo(get_BOM_names(), key=f"-CHILD_NAME_{row_counter}-", s=25), sg.T("Quantity:"),
                    sg.I(key=f"-CHILD_QUANTITY_{row_counter}-", s=5),
                    sg.T("EoL:"), sg.Combo(EoL, key=f"-EoL_{row_counter}-"), sg.T("Fastener:"), sg.Combo(yes_no, key=f"-FASTENER_{row_counter}-", readonly=True), sg.T(f"Child PAC ID: {row_number_view}", key=f"-CHILD_PAC_ID_{row_counter}-")]],
                justification="center", key=('-CHILD_ACTION-', row_counter), visible=False
            ))]
        return row
    else:
        row =  [sg.pin(
        sg.Column(
            [[
              sg.Button("X", key=('-DEL_CHILD-', row_counter)),
                sg.T("Child name:"), sg.Combo(get_BOM_names(), key=f"-CHILD_NAME_{row_counter}-", s=25), sg.T("Quantity:"),
                sg.I(key=f"-CHILD_QUANTITY_{row_counter}-", s=5),
                sg.T("EoL:"), sg.Combo(EoL, key=f"-EoL_{row_counter}-"), sg.T("Fastener:"), sg.Combo(yes_no, key=f"-FASTENER_{row_counter}-", readonly=True), sg.T(f"Child PAC ID: {row_number_view}", key=f"-CHILD_PAC_ID_{row_counter}-")]],
            justification="center", key=('-ROW_CHILD-', row_counter)
        ))]
        return row

def is_valid_path(filepath):
    #Input: Takes a filepath for the computer
    #Output: Returns an error if the file path does not exist
    #This function hasn't been used yet, but can become useful when implementing the files directly in the input GUI
    if filepath and Path(filepath).exists():
        return True
    sg.popup_error("Filepath not correct")
    return False

def is_valid_name(name,BOM_array):
    #Input: Name is the given name of an BOM part wished to be put in the BOM table
    #Input: BOM_array is the current list of names in the BOM table
    #Output: If no name has been filled in an error will be returned, if the name repeats an error will be returned or else the name is considered valid
    if window["BOM names"].get() == '':
        sg.popup_error("Name not filled in correct")
        return False
    flatten_BOM = np.array(BOM_array)
    if name in flatten_BOM:
        sg.popup_error("Name cannot repeat, consider changing quantity of existing part")
        return False
    return True

def is_valid_quantity(quantity):
    if window["BOM quantity"].get() == '':
        sg.popup_error("Quantity not filled in correct")
        return False
    if quantity.isdigit():
        return True
    else:
        sg.popup_error("Quantity can only be integer numbers")
        return False

def ObjFromAttrib(attribute, value, obj_list):  #  finds all objects with a macthing value in the obj list given
    matching_list = []
    for obj in obj_list:
        if getattr(obj, attribute) == value:
            matching_list.append(obj)
    if len(matching_list) == 1:
        return matching_list[0]
    return matching_list

def PACUnitInsert(PACList, AllPACUnits):
    #  Input: AllParents, AllChildren or AllActions. And AllPACUnits list.
    #  Output: AllPACUnits with input list correctly inserted.

    # This loop iterates over the cells again to assign the tree structure as well as Parents, Action and Children
    # to each PACUnit
    for PAC in PACList:
        # Find unit ID for current unit and for its parent
        current_unit_index = len(PAC.ID)
        parent_index = 0
        for char in "PACc":
            index = PAC.ID.find(char)
            if index != -1 and index < current_unit_index:  # Bliver -1 hvis bogstavet ikke findes i stringen
                current_unit_index = index
            if index != -1 and index > parent_index:
                parent_index = index

        # Find PAC ID by finding numbers before P/A/C/c, and converting this into int
        UnitID = re.search(r"[\d]+(?=[PACc])", PAC.ID)
        UnitID = int(UnitID.group(0))

        # If it's not a root node and it's a parent
        if parent_index != current_unit_index and PAC.ID[current_unit_index] == 'P':
            # Find the parent ID
            ParentID = PAC.ID[PAC.ID.index('-') + 1:parent_index]
            ParentID = int(ParentID)
            AllPACUnits[ParentID - 1].addTreeChildren(
                AllPACUnits[UnitID - 1])  # Add the unit as a child to its parent

        IDAsLetters = " ".join(re.split("[^a-zA-Z]*", PAC.ID)).strip()

        # Find objekter med current PACID og sæt dem ind i PAC Uniten
        if IDAsLetters[0] == 'P':
            AllPACUnits[UnitID - 1].Parent = ObjFromAttrib('PACID', UnitID,
                                                       PACList)  # UnitID i den her funktion er det samme som PACID attrib i PACUnit
        if IDAsLetters[0] == 'A':
            AllPACUnits[UnitID - 1].Action = ObjFromAttrib('PACID', UnitID, PACList)
        if IDAsLetters[0] == 'C' or IDAsLetters[0] == 'c':
            AllPACUnits[UnitID - 1].Children = ObjFromAttrib('PACID', UnitID, PACList)
    return AllPACUnits


MOST_layout = [[sg.T("Disassembly setup:"), sg.Combo(setup_type, key="Disassembly setup"),sg.B("Display")],
               [sg.Column([[sg.Image('',key="Disassembly image")]], justification='center')],
               [sg.pin(sg.T("Distance A: ",key="-TA-", visible=False)), sg.pin(sg.I(key="-A-", s=6,visible=False)), sg.pin(sg.T("Distance to storage area: ",key="-TS-", visible=False)), sg.pin(sg.I(key="-S-", s=6, visible=False)), sg.pin(sg.B("Save", key="-SAVESETUP-", visible=False))]
               ]


BOM_layout = [[sg.T("Choose Circularity Indices before inputting items. Do not change Circularity Indicies during item input!")],
              [sg.T("Input BOM from file:"), sg.I(key="BOM names file", s=35), sg.FileBrowse(file_types=()), sg.T("Choose Circularity Indices: "), sg.Combo(["None", "RR", "RE", "MCI"], key='-CICHOICE-'), sg.B("Add CI", key="-ADDCI-")],
              [sg.T("Input BOM names and quantity:"), sg.I(key="BOM names", s=20), sg.I(key="BOM quantity", s=6), sg.B("Add Item", key="Add")],
              [sg.pin(sg.T("Mass recycled in kg (M rec): ", key="-TMRECRR-", visible=False)), sg.pin(sg.I(key="-MREC-", s=6, visible=False)), sg.pin(sg.T("Mass collected at EoL in kg (M collected EoL): ", key="-TEOL-", visible=False)), sg.pin(sg.I(key="-MEOL-", s=6, visible=False))],
              [sg.pin(sg.T("Mass reused in kg (M res): ", key="-TMRESRE-", visible=False)), sg.pin(sg.I(key="-MRES-", s=6, visible=False))],
              [sg.pin(sg.T("Virgin mass (V): ", key="-TV-", visible=False)), sg.pin(sg.I(key="-V-", s=6, visible=False)), sg.pin(sg.T("Unrecoverable waste (W): ", key="-TW-", visible=False)), sg.pin(sg.I(key="-W-", s=6, visible=False))],
              [sg.pin(sg.T("Child mass (M c): ", key="-TMC-", visible=False)), sg.pin(sg.I(key="-MC-", s=6, visible=False)), sg.pin(sg.T("Waste from feedstock (Wf): ", key="-TWF-", visible=False)), sg.pin(sg.I(key="-WF-", s=6, visible=False))],
              [sg.pin(sg.T("Waste from recycling process (Wc): ", key="-TWC-", visible=False)), sg.pin(sg.I(key="-WC-", s=6, visible=False)), sg.pin(sg.T("Actual realised lifetime (L): ", key="-TL-", visible=False)), sg.pin(sg.I(key="-L-", s=6, visible=False))],
              [sg.pin(sg.T("Product average lifetime based on market (Lav): ", key="-TLAV-", visible=False)), sg.pin(sg.I(key="-LAV-", s=6, visible=False))],
              [sg.pin(sg.Table(values=BOM_array, headings=headings, display_row_numbers=True, num_rows=10, key='-TABLE-', enable_events=True, enable_click_events=True, expand_x=False, justification="center", expand_y=False, visible=True, auto_size_columns = True))],
              [sg.pin(sg.Table(values=BOM_array, headings=headings_RR, display_row_numbers=True, num_rows=10, key='-TABLERR-', enable_events=True, enable_click_events=True, expand_x=True, justification="center", expand_y=True, visible=False))],
              [sg.pin(sg.Table(values=BOM_array, headings=headings_RE, display_row_numbers=True, num_rows=10, key='-TABLERE-', enable_events=True, enable_click_events=True, expand_x=True, justification="center", expand_y=True, visible=False))],
              [sg.pin(sg.Table(values=BOM_array, headings=headings_MCI, display_row_numbers=True, num_rows=10, key='-TABLEMCI-', enable_events=True, enable_click_events=True, expand_x=True, justification="center", expand_y=True, visible=False))],
              [sg.pin(sg.Table(values=BOM_array, headings=headings_RRRE, display_row_numbers=True, num_rows=10, key='-TABLERRRE-', enable_events=True, enable_click_events=True, expand_x=True, justification="center", expand_y=True, visible=False))],
              [sg.pin(sg.Table(values=BOM_array, headings=headings_RRMCI, display_row_numbers=True, num_rows=10, key='-TABLERRMCI-', enable_events=True, enable_click_events=True, expand_x=True, justification="center", expand_y=True, visible=False))],
              [sg.pin(sg.Table(values=BOM_array, headings=headings_REMCI, display_row_numbers=True, num_rows=10, key='-TABLEREMCI-', enable_events=True, enable_click_events=True, expand_x=True, justification="center", expand_y=True, visible=False))],
              [sg.pin(sg.Table(values=BOM_array, headings=headings_RRREMCI, display_row_numbers=True, num_rows=10, key='-TABLERRREMCI-', enable_events=True, enable_click_events=True, expand_x=True, justification="center", expand_y=True, visible=False, auto_size_columns = True))]
]

menu_def = [["Help", ["MOST", "BOM", "PAC"]],
            ["Save/Load", ["Save current setup", "Load existing setup"]]]

#ændrer navnene på alle de her, de kan ikke have samme navne som den første tab
PAC_layout = [
              [sg.Column([[sg.T("Input PAC from file:"), sg.I(key="BOM names file", s=35), sg.FileBrowse(file_types=())]], justification="center")],
              [sg.HSeparator()],
              [sg.Column([[sg.T(f"PAC Unit: {PAC_unit}", key="-PAC_UNIT-")]], justification="center")],
              [sg.HSeparator()],

              [sg.Column([
              [sg.Column([[sg.T("Parent")]], justification="center")],
              [sg.Column([[sg.T("Parent name:"), sg.pin(sg.I(key="-PARENT_NAME-", s=25)), sg.pin(sg.Combo(children_name_ID[0], key="-PARENT_NAME_COMBO-",s=25 , visible=False, readonly=True)), sg.T("Parent PAC ID:", key="-PARENT_PAC_ID-")]], justification="center")],
              [sg.Column([[sg.T("Disassembly failure parent")]], justification="center")],
              [sg.Column([create_parent_DF(0,1)],key='-PARENT_DF_PANEL-', justification="center")],
              [sg.Column([[sg.Button('Add DF',key='-ADD_ITEM_PARENT_DF-')]], justification="center")],
              ],key="-PARENT_SCROLL-", scrollable=True, vertical_scroll_only=True, size=[1400,150])],

              [sg.HSeparator()],
              [sg.Column([
              [sg.Column([[sg.T("Action")]], justification="center")],
              [sg.Column([[sg.T("Action name:"), sg.Combo(action_type, key="-ACTION_TYPE-", s=25), sg.T("Action description:"), sg.I(key="-ACTION_DESCRIPTION-", s=25, tooltip="Write description for all actions here"), sg.T("Action times:"), sg.I(key="-ACTION_TIMES_NUMBER-", s=5), sg.T("Tool:"), sg.Combo(tool_type,key="-ACTION_TOOL_TYPE-"), sg.T("Action PAC ID:", key="-ACTION_PAC_ID-")]], justification="center")],
              [sg.Column([create_action(0,1)],key='-ACTION_PANEL-', justification="center")],
              [sg.Column([[sg.Button('Add Action',key='-ADD_ITEM_ACTION-')]], justification="center")],
              [sg.Column([[sg.T("Disassembly failure action")]], justification="center")],
              [sg.Column([create_action_DF(0,1)],key='-ACTION_DF_PANEL-', justification="center")],
              [sg.Column([[sg.Button('Add DF',key='-ADD_ITEM_ACTION_DF-')]], justification="center")]],key="-ACTION_SCROLL-", scrollable=True, vertical_scroll_only=True, size=[1400,200])],


              [sg.HSeparator()],

              [sg.Column([
              [sg.Column([[sg.T("Children")]], justification="center")],
              [sg.Column([[sg.T("Child name:"), sg.Combo(get_BOM_names(), key="-CHILD_NAME-", s=25), sg.T("Quantity:"), sg.I(key="-CHILD_QUANTITY-", s=5), sg.T("EoL:"), sg.Combo(EoL, key="-EoL-"), sg.T("Fastener:"), sg.Combo(yes_no, key="-FASTENER-", readonly=True), sg.T("Child PAC ID:", key="-CHILD_PAC_ID-")]], justification="center")],
              [sg.Column([create_child(0,1)],key='-CHILD_PANEL-', justification="center")],
              [sg.Column([[sg.Button('Add Child',key='-ADD_ITEM_CHILD-')]], justification="center")],
              [sg.Column([[sg.T("Disassembly failure child")]], justification="center")],
              [sg.Column([create_child_DF(0,1)],key='-CHILD_DF_PANEL-', justification="center")],
              [sg.Column([[sg.Button('Add DF',key='-ADD_ITEM_CHILD_DF-')]], justification="center")]], key="-CHILD_SCROLL-", scrollable=True, vertical_scroll_only=True, size=[1400,200])],


              [sg.HSeparator()],
              [sg.Column([[sg.B("Check PAC ID",key="-CHECK_PAC_ID-"), sg.pin(sg.B("Delete PAC unit", key="-DELETE_PAC_UNIT-", visible=False)), sg.pin(sg.B("Previous PAC unit", key="-PREVIOUS_PAC_UNIT-", visible=False)) ,sg.B("Next PAC unit", key="-NEXT_PAC_UNIT-")]], justification="right")]

]

tab_group = [[sg.MenubarCustom(menu_def, tearoff=False)],
    [
        sg.TabGroup(
        [[
            sg.Tab('MOST', MOST_layout),
            sg.Tab('BOM', BOM_layout),
            sg.Tab('PAC', PAC_layout)]],

        tab_location='topleft',title_color='White', tab_background_color='Gray', selected_title_color='Black',
        selected_background_color='White', border_width=5, size=[1350,780]),
        sg.Column([[sg.B("Start timer")], [sg.B("Finish PAC model", key="-FINISH_PAC_MODEL-")]])
    ]
]




window = sg.Window("Initial GUI", tab_group, resizable=True)

def child_relation_ID_1(ID):
    #This function appends the children which are not fasteners to a list, to be used to select a new parent, which
    #then can be used to know what children a PAC unit is related to
    #This function only relates to the first child which is non deleteable in the GUI
    #The input ID is the first 3 values of the PAC ID
    #The output if the child is not a fastener is a 2D list with the first column being the name and the second being the
    #first 3 values of the PAC ID
    if window["-CHILD_NAME-"].get() == "":
        sg.popup_error("Children must have a name")
        error[PAC_unit-1] += 1
        return
    if window["-FASTENER-"].get() == "Yes":
        return
    elif ID in children_name_ID[1]:
        i = children_name_ID[1].index(ID)
        children_name_ID[0][i] = window["-CHILD_NAME-"].get()
    else:
        children_name_ID[0].append(window["-CHILD_NAME-"].get())
        children_name_ID[1].append(ID)

def child_relation_ID(ID, row_counter):
    # This function appends the children which are not fasteners to a list, to be used to select a new parent, which
    # then can be used to know what children a PAC unit is related to
    # This function only relates to the all added children after the first
    # The input ID is the first 3 values of the PAC ID
    # The input row_counter is used to index the correct child, because there can be several
    # The output if the child is not a fastener is a 2D list with the first column being the name and the second being the
    # first 3 values of the PAC ID
    if window[f"-CHILD_PAC_ID_{row_counter}-"].get() == "":
        sg.popup_error("Children must have a name")
        error[PAC_unit - 1] += 1
        return
    if window[f"-FASTENER_{row_counter}-"].get() == "Yes":
        return
    elif ID in children_name_ID[1]:
        i = children_name_ID[1].index(ID)
        children_name_ID[0][i] = window[f"-CHILD_NAME_{row_counter}-"].get()
    else:
        children_name_ID[0].append(window[f"-CHILD_NAME_{row_counter}-"].get())
        children_name_ID[1].append(ID)

def child_relation_name(Name):
    #This function takes the name of a child and gives back the ID which is the 3 first values in the PAC ID
    #Input is a name which is the first column in the children_name_ID list
    #Output is the ID from the second column in the children_name_ID_list
    i = children_name_ID[0].index(Name)
    ID = children_name_ID[1][i]
    return ID

def parent_class_1(ID_Input):
    #This function is called when a PAC unit is checked and inserts all information from the parent in the first PAC unit
    #into the AllParents class. Firstly it checks if the PAC ID already exist, if there has been checked for the PAC unit
    #already, if not it creates the PAC ID and inserts that and the name in the AllParents class. If the PAC ID already
    #exist it only changes the name.
    #This function is only used for the first PAC units parent
    #Input is the PAC ID
    #Output is the addition of the parent to the AllParents class
    if not AllParents:
        ID = ""
    else:
        for parent in AllParents:
            ID = getattr(parent, 'ID')
            if ID == ID_Input:
                continue

    if window["-PARENT_NAME-"].get() == '':
        sg.popup_error("Remember to fill in the parent name, then click Check PAC ID again")
        error[PAC_unit - 1] += 1
        return

    if ID != ID_Input:
        instance = Parent(ID_Input)
        if window["-PARENT_NAME-"] != "": instance.Desc = window["-PARENT_NAME-"].get()
        AllParents.append(instance)
        #print("Object not found")
        #print(instance.ID, instance.Desc)
    else:
        matching_list = ObjFromAttrib('ID', ID_Input, AllParents)
        matching_list.Desc = window["-PARENT_NAME-"].get()
        #print("Object found")
        #print(matching_list.Desc)

def parent_class(ID_Input):
    # This function is called when a PAC unit is checked and inserts all information from the parent in the given PAC unit
    # into the AllParents class. Firstly it checks if the PAC ID already exist, if there has been checked for the PAC unit
    # already, if not it creates the PAC ID and inserts that and the name in the AllParents class. If the PAC ID already
    # exist it only changes the name.
    # This function is used for all parents after the first PAC unit
    # Input is the PAC ID
    # Output is the addition of the parent to the AllParents class
    if not AllParents:
        ID = ""
    else:
        for parent in AllParents:
            ID = getattr(parent, 'ID')
            if ID == ID_Input:
                continue

    if window["-PARENT_NAME_COMBO-"].get() == '':
        sg.popup_error("Remember to fill in the parent name, then click Check PAC ID again")
        error[PAC_unit - 1] += 1
        return

    if ID != ID_Input:
        instance = Parent(ID_Input)
        if window["-PARENT_NAME_COMBO-"] != "": instance.Desc = window["-PARENT_NAME_COMBO-"].get()
        AllParents.append(instance)
        #print("Object not found")
        #print(instance.ID, instance.Desc)
    else:
        matching_list = ObjFromAttrib('ID', ID_Input, AllParents)
        matching_list.Desc = window["-PARENT_NAME_COMBO-"].get()
        #print("Object found")
        #print(matching_list.Desc)

def action_class_1(ID_Input):
    # This function is called when a PAC unit is checked and inserts all information from the action in the given PAC unit
    # into the AllActions class. Firstly it checks if the PAC ID already exist, if there has been checked for the PAC unit
    # already, if not it creates the PAC ID and inserts that and the name in the AllActions class. If the PAC ID already
    # exist it only changes the name.
    # This function is used for the first action in each PAC unit
    # Input is the PAC ID
    # Output is the addition of the action to the AllActions class
    if not AllActions:
        ID = ""
    else:
        for action in AllActions:
            ID = getattr(action, 'ID')
            if ID == ID_Input:
                continue

    if ID != ID_Input:
        instance = Action(ID_Input)
        if window["-ACTION_TYPE-"] != "": instance.Desc = window["-ACTION_TYPE-"].get()
        if window["-ACTION_DESCRIPTION-"] != "": instance.DescDetail = window["-ACTION_DESCRIPTION-"].get()
        if window["-ACTION_TIMES_NUMBER-"] != "": instance.Times = window["-ACTION_TIMES_NUMBER-"].get()
        if window["-ACTION_TOOL_TYPE-"] != "": instance.Tool = window["-ACTION_TOOL_TYPE-"].get()
        AllActions.append(instance)
        #print("Object not found")
        #print(instance.ID, instance.Desc)
    else:
        matching_list = ObjFromAttrib('ID', ID_Input, AllActions)
        matching_list.Desc = window["-ACTION_TYPE-"].get()
        matching_list.DescDetail = window["-ACTION_DESCRIPTION-"].get()
        matching_list.Times = window["-ACTION_TIMES_NUMBER-"].get()
        matching_list.Tool = window["-ACTION_TOOL_TYPE-"].get()
        #print("Object found")
        #print(matching_list.Desc)

def action_class(ID_Input, row_counter):
    #This function takes all actions after the first and add them to the strings of the different values given to the object
    #in the AllActions class.
    #Input the PAC ID
    #Input the row_counter to know which action is being indexed
    #Output an addition to the AllActions for the given PAC unit
    matching_list = ObjFromAttrib('ID', ID_Input, AllActions)
    matching_list.Desc = matching_list.Desc + " & " + window[f"-ACTION_TYPE_{row_counter}-"].get()
    matching_list.Times = matching_list.Times + " & " + window["-ACTION_TIMES_NUMBER-"].get()
    matching_list.Tool = matching_list.Tool + " & " + window["-ACTION_TOOL_TYPE-"].get()
    #print("Combined Actions")
    #print(matching_list.Desc)

def child_class_1(ID_Input):
    # This function is called when a PAC unit is checked and inserts all information from the child in the given PAC unit
    # into the AllChildren class. Firstly it checks if the PAC ID already exist, if there has been checked for the PAC unit
    # already, if not it creates the PAC ID and inserts that and the name in the AllChildren class. If the PAC ID already
    # exist it only changes the name.
    # This function is used for the first child in each PAC unit
    # Input is the PAC ID
    # Output is the addition of the child to the AllChildren class
    if not AllChildren:
        ID = ""
    else:
        for action in AllChildren:
            ID = getattr(action, 'ID')
            if ID == ID_Input:
                break
    #print('ID: '+ ID +' ID_Input: '+ID_Input)
    if ID != ID_Input:
        instance = Child(ID_Input)
        if window["-CHILD_NAME-"] != "": instance.Desc = window["-CHILD_NAME-"].get()
        if window["-CHILD_QUANTITY-"] != "": instance.Number = window["-CHILD_QUANTITY-"].get()
        if window["-EoL-"] != "": instance.EoL = window["-EoL-"].get()
        AllChildren.append(instance)
        #print("Object not found")
        #print(instance.ID, instance.Desc)
    else:
        matching_list = ObjFromAttrib('ID', ID_Input, AllChildren)
        matching_list.Desc = window["-CHILD_NAME-"].get()
        matching_list.Number = window["-CHILD_QUANTITY-"].get()
        matching_list.EoL = window["-EoL-"].get()
        #print("Object found")
        #print(matching_list.Desc)

def child_class(ID_Input, row_counter):
    # This function is called when a PAC unit is checked and inserts all information from the child in the given PAC unit
    # into the AllChildren class. Firstly it checks if the PAC ID already exist, if there has been checked for the PAC unit
    # already, if not it creates the PAC ID and inserts that and the name in the AllChildren class. If the PAC ID already
    # exist it only changes the name.
    # This function is used for all children after the first in a given PAC unit
    # Input is the PAC ID
    # Input is also the row_counter to know which child is being indexed
    # Output is the addition of the child to the AllChildren class
    if not AllChildren:
        ID = ""
    else:
        for action in AllChildren:
            ID = getattr(action, 'ID')
            if ID == ID_Input:
                break
    #print('ID: '+ ID +' ID_Input: '+ID_Input)
    if ID != ID_Input:
        instance = Child(ID_Input)
        if window[f"-CHILD_NAME_{row_counter}-"] != "": instance.Desc = window[f"-CHILD_NAME_{row_counter}-"].get()
        if window[f"-CHILD_QUANTITY_{row_counter}-"] != "": instance.Number = window[f"-CHILD_QUANTITY_{row_counter}-"].get()
        if window[f"-EoL_{row_counter}-"] != "": instance.EoL = window[f"-EoL_{row_counter}-"].get()
        AllChildren.append(instance)
        #print("Object not found")
        #print(instance.ID, instance.Desc)
    elif ID == ID_Input:
        matching_list = ObjFromAttrib('ID', ID_Input, AllChildren)
        matching_list.Desc = window[f"-CHILD_NAME_{row_counter}-"].get()
        matching_list.Number = window[f"-CHILD_QUANTITY_{row_counter}-"].get()
        matching_list.EoL = window[f"-EoL_{row_counter}-"].get()
        #print("Object found")
        #print(matching_list.Desc)
    else:
        print('VI HAR FUCKET OP')

def parent_DF_class(ID_Input,row_counter):
    if not AllDisassemblies:
        ID = ""
    else:
        for rows in AllDisassemblies:
            ID = getattr(rows, 'DFID')
            if ID == ID_Input:
                continue

    if ID != ID_Input:
        instance = Disassembly(ID_Input)
        if window[f"-PARENT_FAILURE_DESCRIPTION_{row_counter}-"] != "": instance.DFEffect = window[f"-PARENT_FAILURE_DESCRIPTION_{row_counter}-"].get()
        if window[f"-PARENT_DISASSEMBLY_TYPE_{row_counter}-"] != "": instance.DAType = window[
            f"-PARENT_DISASSEMBLY_TYPE_{row_counter}-"].get()
        if window[f"-PARENT_TOOL_TYPE_{row_counter}-"] != "": instance.DATool = window[f"-PARENT_TOOL_TYPE_{row_counter}-"].get()

        AllDisassemblies.append(instance)
        #print("Object not found")
        #print(instance.DFID, instance.DFEffect)
    else:
        matching_list = ObjFromAttrib('DFID', ID_Input, AllDisassemblies)
        matching_list.DFEffect = window[f"-PARENT_FAILURE_DESCRIPTION_{row_counter}-"].get()
        matching_list.DAType = window[f"-PARENT_DISASSEMBLY_TYPE_{row_counter}-"].get()
        matching_list.DATool = window[f"-PARENT_TOOL_TYPE_{row_counter}-"].get()
        #print("Object found")
        #print(matching_list.DFEffect)

def action_DF_class(ID_Input,row_counter):
    if not AllDisassemblies:
        ID = ""
    else:
        for rows in AllDisassemblies:
            ID = getattr(rows, 'DFID')
            if ID == ID_Input:
                continue

    if ID != ID_Input:
        instance = Disassembly(ID_Input)
        if window[f"-ACTION_FAILURE_DESCRIPTION_{row_counter}-"] != "": instance.DFEffect = window[f"-ACTION_FAILURE_DESCRIPTION_{row_counter}-"].get()
        if window[f"-ACTION_DISASSEMBLY_TYPE_{row_counter}-"] != "": instance.DAType = window[
            f"-ACTION_DISASSEMBLY_TYPE_{row_counter}-"].get()
        if window[f"-ACTION_TOOL_TYPE_{row_counter}-"] != "": instance.DATool = window[f"-ACTION_TOOL_TYPE_{row_counter}-"].get()

        AllDisassemblies.append(instance)
        #print("Object not found")
        #print(instance.DFID, instance.DFEffect)
    else:
        matching_list = ObjFromAttrib('DFID', ID_Input, AllDisassemblies)
        matching_list.DFEffect = window[f"-ACTION_FAILURE_DESCRIPTION_{row_counter}-"].get()
        matching_list.DAType = window[f"-ACTION_DISASSEMBLY_TYPE_{row_counter}-"].get()
        matching_list.DATool = window[f"-ACTION_TOOL_TYPE_{row_counter}-"].get()
        #print("Object found")
        #print(matching_list.DFEffect)

def child_DF_class(ID_Input, row_counter):
    if not AllDisassemblies:
        ID = ""
    else:
        for rows in AllDisassemblies:
            ID = getattr(rows, 'DFID')
            if ID == ID_Input:
                continue

    if ID != ID_Input:
        instance = Disassembly(ID_Input)
        if window[f"-CHILD_FAILURE_DESCRIPTION_{row_counter}-"] != "": instance.DFEffect = window[f"-CHILD_FAILURE_DESCRIPTION_{row_counter}-"].get()
        if window[f"-CHILD_DISASSEMBLY_TYPE_{row_counter}-"] != "": instance.DAType = window[f"-CHILD_DISASSEMBLY_TYPE_{row_counter}-"].get()
        if window[f"-CHILD_TOOL_TYPE_{row_counter}-"] != "": instance.DATool = window[f"-CHILD_TOOL_TYPE_{row_counter}-"].get()

        AllDisassemblies.append(instance)
        #print("Object not found")
        #print(instance.DFID, instance.DFEffect)
    else:
        matching_list = ObjFromAttrib('DFID', ID_Input, AllDisassemblies)
        matching_list.DFEffect = window[f"-CHILD_FAILURE_DESCRIPTION_{row_counter}-"].get()
        matching_list.DAType = window[f"-CHILD_DISASSEMBLY_TYPE_{row_counter}-"].get()
        matching_list.DATool = window[f"-CHILD_TOOL_TYPE_{row_counter}-"].get()
        #print("Object found")
        #print(matching_list.DFEffect)

def action_DF_affected_ID():
    #This function is used to make sure the affected action counter for the disassembly failure is updated when a new
    #action is added
    #No input is needed, because we can check everything from the global variable PAC_unit
    #The function returns no value but updates the affected action counter in the function
    if PAC_unit > 1:
        counter = 1
    else:
        counter = 0
    for rows in range(0,len(row_action[2])):
        if row_action[2][rows] == 1 and row_action[3][rows] == PAC_unit:
            counter += 1
    for rows in range(0,len(row_action_DF[0])):
        if row_action_DF[3][rows] == PAC_unit:
            window[f"-ACTION_ID_FOR_DF_{rows}-"].update(values=list(range(1, counter+1)))

def child_DF_affected_ID():
    # This function is used to make sure the affected child counter for the disassembly failure is updated when a new
    # child is added
    # No input is needed, because we can check everything from the global variable PAC_unit
    # The function returns no value but updates the affected child counter in the function
    if PAC_unit > 1:
        counter = 1
    else:
        counter = 0
    for rows in range(0, len(row_child[2])):
        if row_child[2][rows] == 1 and row_child[3][rows] == PAC_unit:
            counter += 1
    for rows in range(0, len(row_child_DF[0])):
        if row_child_DF[3][rows] == PAC_unit:
            window[f"-CHILD_ID_FOR_DF_{rows}-"].update(values=list(range(1, counter + 1)))

def PAC_search(PAC_unit, PAC_list):
    for row in PAC_list:
        if row.PACID == PAC_unit:
            matching_list = row
    return matching_list
#What the fuck
def update_parent_DF():
    # Continously updating the DF
    for rows in row_parent_DF[0]:
        if row_parent_DF[2][rows] == 1 and row_parent_DF[3][rows] == PAC_unit:
            # The if statement below will only work once a new button has happened been clicked  in the GUI
            if window[f"-PARENT_ORIGIN_{rows}-"].get() != "":
                print(f"PAC unit: {PAC_unit}")
                print(f"Origin_number_parent: {origin_number_parent_DF}")
                origin_number_parent_DF[PAC_unit - 1].append(rows)
                if rows in origin_number_parent_DF[PAC_unit-1] and origin_number_parent_DF[PAC_unit-1].count(rows) <= 1:
                    if PAC_unit == 1:
                        origin_PAC_unit[0].append(f"1P1-000-000-1D{row_parent_DF[1][rows]}")
                    else:
                        if window[f"-PARENT_ORIGIN_{rows}-"].get() == "Origin here":
                            relation = window[f"-PARENT_ORIGIN_{rows}-"].get().split("-")[0]
                            origin_PAC_unit[PAC_unit - 1].append(f"{PAC_unit}P1-{relation}-{000}-{PAC_unit}D{row_parent_DF[1][rows]}")
                        else:
                            relation = window[f"-PARENT_ORIGIN_{rows}-"].get().split("-")[0]
                            origin_PAC_unit[PAC_unit-1].append(f"{PAC_unit}P1-{relation}-{relation}-{PAC_unit}D{row_parent_DF[1][rows]}")

def update_action_DF():
    for rows in row_action_DF[0]:
        if row_action_DF[2][rows] == 1 and row_action_DF[3][rows] == PAC_unit:
            # The if statement below will only work once a new button has happened been clicked  in the GUI
            if window[f"-ACTION_ORIGIN_{rows}-"].get() != "":
                origin_number_action_DF[PAC_unit-1].append(rows)
                if rows in origin_number_action_DF[PAC_unit - 1] and origin_number_action_DF[PAC_unit-1].count(rows) <= 1:
                    if PAC_unit == 1:
                        #print(window[f"-ACTION_ORIGIN_{rows}-"].get())
                        if window[f"-ACTION_ORIGIN_{rows}-"].get() == "Origin here":
                            origin_PAC_unit[0].append(f"1A1-000-000-1D{row_action_DF[1][rows]}")
                        else:
                            origin_PAC_unit[0].append(f"1A1-000-1P1-1D{row_action_DF[1][rows]}")
                    else:
                        if window[f"-ACTION_ORIGIN_{rows}-"].get() == "Origin here":
                            relation_child = parent_relation()
                            origin_PAC_unit[PAC_unit - 1].append(f"{PAC_unit}A1-{relation_child}-000-{PAC_unit}D{row_action_DF[1][rows]}")
                        else:
                            relation_DF = window[f"-ACTION_ORIGIN_{rows}-"].get().split("-")[0]
                            relation_child = parent_relation()
                            origin_PAC_unit[PAC_unit-1].append(f"{PAC_unit}A1-{relation_child}-{relation_DF}-{PAC_unit}D{row_action_DF[1][rows]}")

def parent_relation():
    parent_name = window["-PARENT_NAME_COMBO-"].get()
    matching_list = ObjFromAttrib('Desc', parent_name, AllChildren)
    ID = matching_list.ID.split("-")[1]
    return ID

def save_setup(objects):
    #Generates a new layout which will be used as a popup when saving the file
    layout = [[sg.T("Save window")],
              [sg.T("File name:"), sg.I(key="-SAVE_FILE_NAME-")],
              [sg.T("Save folder:"), sg.I(key="-SAVE_FOLDER-"), sg.FolderBrowse()],
              [sg.B("Save", key="-SAVE-")]]

    window = sg.Window("Save Window", layout, modal=True)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == "-SAVE-":
            if window["-SAVE_FILE_NAME-"].get() == "":
                sg.popup_error("Fill out name for file")
                continue
            if window["-SAVE_FOLDER-"].get() == "":
                sg.popup_error("Choose folder for file")
                continue

            save_folder = window["-SAVE_FOLDER-"].get()
            save_name = window["-SAVE_FILE_NAME-"].get()
            file_path = save_folder + "/" + save_name + ".pickle"
            print(file_path)

            try:
                with open(file_path, "xb") as fp:
                    pickle.dump(objects, fp)
            except FileExistsError:
                sg.popup_error("File already exists")
                continue

            sg.popup_no_titlebar("Setup saved")
            break
    window.close()

def load_setup():
    # Generates a new layout which will be used as a popup when saving the file
    layout = [[sg.T("Load window")],
              [sg.T("Load file:"), sg.I(key="-LOAD_FILE-"), sg.FileBrowse(file_types=(("Pickle Files", "*.pickle"),))],
              [sg.B("Load", key="-LOAD-")]]

    window = sg.Window("Save Window", layout, modal=True)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == "-LOAD-":
            if window["-LOAD_FILE-"].get() == "":
                sg.popup_error("No file chosen")
                continue
            file_path = window["-LOAD_FILE-"].get()
            with open(file_path, 'rb') as f:
                x = pickle.load(f)
                global AllParents, AllActions, AllChildren, AllDisassemblies, AllPACUnits, origin_PAC_unit, origin_global
                global check_PAC_ID, row_parent_DF, row_action_DF, row_child_DF, row_action, row_child, children_name_ID
                global parent_DF_diff, action_DF_diff, child_DF_diff, action_diff, child_diff, error, origin_number_parent_DF
                global origin_number_action_DF, origin_number_child_DF
                AllParents = x['Parents']
                AllChildren = x['Children']
                AllActions = x['Actions']
                AllDisassemblies = x['Disassemblies']
                AllPACUnits = x['PACUnits']
                origin_PAC_unit = x['origin_PAC_unit']
                origin_global = x['origin_global']
                check_PAC_ID = x['check_PAC_ID']
                row_parent_DF = x['row_parent_DF']
                row_action_DF = x['row_action_DF']
                row_child_DF = x['row_child_DF']
                row_action = x['row_action']
                row_child = x['row_child']
                children_name_ID = x['children_name_ID']
                parent_DF_diff = x['parent_DF_diff']
                action_DF_diff = x['action_DF_diff']
                child_DF_diff = x['child_DF_diff']
                action_diff = x['action_diff']
                child_diff = x['child_diff']
                error = x['error']
                origin_number_parent_DF = x['origin_number_parent_DF']
                origin_number_action_DF = x['origin_number_action_DF']
                origin_number_child_DF = x['origin_number_child_DF']



            sg.popup_no_titlebar("Setup loaded")
            break
    window.close()


while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break
    if event == "-FINISH_PAC_MODEL-":
        try:
            check_PAC_ID[-1]
        except IndexError:
            sg.popup_error("The model needs more than one PAC unit to generate the model")
            continue
        #  Create the AllPACUnits list
        # Creates empty PACUnits according to maximum amount of PAC units
        AllPACUnits = [PACUnit(i) for i in range(1, check_PAC_ID[-1] + 1)]

        #  FUNCTION
        PACUnitInsert(AllParents, AllPACUnits)
        PACUnitInsert(AllChildren, AllPACUnits)
        PACUnitInsert(AllActions, AllPACUnits)
        #  Does not insert DFs. But DFs are handled seperately in GUI_Final.py

        #  Dump files to Pickle
        objects = {"Parents": AllParents, "Actions": AllActions, "Children": AllChildren,
                   "Disassemblies": AllDisassemblies, "PACUnits": AllPACUnits}
        with open('objects.pickle', 'wb') as f:
            pickle.dump(objects, f)


        #  Run final GUI
        os.system('GUI_Final.py')


        #sg.popup_error("Not yet implemented")
    if event == "Start timer":
        if "t1" in locals():
            sg.popup_error("The timer has already been started. Close the program to see the final time")
            continue
        else:
            t1 = time.perf_counter()

    if event == "Save current setup":
        try:
            check_PAC_ID[-1]
        except IndexError:
            sg.popup_error("The model needs more than one PAC unit to be saved")
            continue
        #  Create the AllPACUnits list
        # Creates empty PACUnits according to maximum amount of PAC units
        AllPACUnits = [PACUnit(i) for i in range(1, check_PAC_ID[-1] + 1)]

        #  FUNCTION
        PACUnitInsert(AllParents, AllPACUnits)
        PACUnitInsert(AllChildren, AllPACUnits)
        PACUnitInsert(AllActions, AllPACUnits)
        #  Does not insert DFs. But DFs are handled seperately in GUI_Final.py

        #  Dump files to Pickle
        '''
        objects = {"Parents": AllParents, "Actions": AllActions, "Children": AllChildren,
                   "Disassemblies": AllDisassemblies, "PACUnits": AllPACUnits}
        '''
        objects = {"Parents": AllParents, "Actions": AllActions, "Children": AllChildren,
                   "Disassemblies": AllDisassemblies, "PACUnits": AllPACUnits,
                   "origin_PAC_unit": origin_PAC_unit, "origin_global": origin_global, "check_PAC_ID": check_PAC_ID,
                   "row_parent_DF": row_parent_DF, "row_action_DF": row_action_DF, "row_child_DF": row_child_DF,
                   "row_action": row_action, "row_child": row_child, "children_name_ID": children_name_ID,
                   "parent_DF_diff": parent_DF_diff,
                   "action_DF_diff": action_DF_diff, "child_DF_diff": child_DF_diff, "action_diff": action_diff,
                   "child_diff": child_diff, "error": error,
                   "origin_number_parent_DF": origin_number_parent_DF,
                   "origin_number_action_DF": origin_number_action_DF, "origin_number_child_DF": origin_number_child_DF}

        save_setup(objects)

    if event == "Load existing setup":
        load_setup()
        PAC_unit = AllPACUnits[-1].PACID
        DF_parent = []
        DF_action = []
        DF_children = []
        for DF in AllDisassemblies:
            if "P" in DF.DFID.split("-")[0]:
                DF_parent.append(DF)
            if "A" in DF.DFID.split("-")[0]:
                DF_action.append(DF)
            if "C" in DF.DFID.split("-")[0] or "c" in DF.DFID.split("-")[0]:
                DF_children.append(DF)

        #Creates the parent DF rows that were in the save file
        for rows in range(0,len(row_parent_DF[0])):
            for DF in DF_parent:
                test1 = DF.DFID.split("-")[3][:DF.DFID.split("-")[3].index('D')]
                test2 = DF.DFID.split("-")[3][DF.DFID.split("-")[3].index('D')+1:]
                if row_parent_DF[3][rows] == int(test1) and row_parent_DF[1][rows] == int(test2):
                    matching_DF = DF
            window.extend_layout(window['-PARENT_DF_PANEL-'],[create_parent_DF(row_parent_DF[0][rows], row_parent_DF[1][rows])])
            if rows > 0:
                window[f"-PARENT_FAILURE_DESCRIPTION_{rows}-"].update(matching_DF.ID)
                window[f"-PARENT_DISASSEMBLY_TYPE_{rows}-"].update(matching_DF.DAType)
                window[f"-PARENT_TOOL_TYPE_{rows}-"].update(matching_DF.DATool)
                window[f"-PARENT_DF_ID_{rows}-"].update(matching_DF.DFID)
                if "0" in DF.DFID.split("-")[2]:
                    window[f"-PARENT_ORIGIN_{rows}-"].update("Origin here")
                else:
                    window[f"-PARENT_ORIGIN_{rows}-"].update(DF.DFID)
            window[('-ROW_PARENT_DF-', rows)].update(visible=False)

        #Creates the action DF rows that were in the save file
        for rows in row_action_DF[0]:
            for DF in DF_action:
                test1 = DF.DFID.split("-")[3][:DF.DFID.split("-")[3].index('D')]
                test2 = DF.DFID.split("-")[3][DF.DFID.split("-")[3].index('D')+1:]
                if row_action_DF[3][rows] == int(test1) and row_action_DF[1][rows] == int(test2):
                    matching_DF = DF
            window.extend_layout(window['-ACTION_DF_PANEL-'],[create_action_DF(row_action_DF[0][rows], row_action_DF[1][rows])])
            if rows > 0:
                window[f"-ACTION_ID_FOR_DF_{rows}-"].update(DF.DFID.split("-")[0][DF.DFID.split("-")[0].index('A')+1:])
                window[f"-ACTION_FAILURE_DESCRIPTION_{rows}-"].update(matching_DF.ID)
                window[f"-ACTION_DISASSEMBLY_TYPE_{rows}-"].update(matching_DF.DAType)
                window[f"-ACTION_TOOL_TYPE_{rows}-"].update(matching_DF.DATool)
                window[f"-ACTION_DF_ID_{rows}-"].update(matching_DF.DFID)
                if "0" in DF.DFID.split("-")[2]:
                    window[f"-ACTION_ORIGIN_{rows}-"].update("Origin here")
                else:
                    window[f"-ACTION_ORIGIN_{rows}-"].update(DF.DFID)
            window[('-ROW_ACTION_DF-', rows)].update(visible=False)

        # Creates the children DF rows that were in the save file
        for rows in row_child_DF[0]:
            for DF in DF_children:
                test1 = DF.DFID.split("-")[3][:DF.DFID.split("-")[3].index('D')]
                test2 = DF.DFID.split("-")[3][DF.DFID.split("-")[3].index('D')+1:]
                if row_child_DF[3][rows] == int(test1) and row_child_DF[1][rows] == int(test2):
                    matching_DF = DF
            window.extend_layout(window['-CHILD_DF_PANEL-'],[create_child_DF(row_child_DF[0][rows], row_child_DF[1][rows])])
            if rows > 0:
                if "C" in DF.DFID.split("-")[0]:
                    window[f"-CHILD_ID_FOR_DF_{rows}-"].update(DF.DFID.split("-")[0][DF.DFID.split("-")[0].index('C')+1:])
                else:
                    window[f"-CHILD_ID_FOR_DF_{rows}-"].update(DF.DFID.split("-")[0][DF.DFID.split("-")[0].index('c') + 1:])
                window[f"-CHILD_FAILURE_DESCRIPTION_{rows}-"].update(matching_DF.ID)
                window[f"-CHILD_DISASSEMBLY_TYPE_{rows}-"].update(matching_DF.DAType)
                window[f"-CHILD_TOOL_TYPE_{rows}-"].update(matching_DF.DATool)
                window[f"-CHILD_DF_ID_{rows}-"].update(matching_DF.DFID)
                if "0" in DF.DFID.split("-")[2]:
                    window[f"-CHILD_ORIGIN_{rows}-"].update("Origin here")
                else:
                    window[f"-CHILD_ORIGIN_{rows}-"].update(DF.DFID)
            window[('-ROW_CHILD_DF-', rows)].update(visible=False)

        window.extend_layout(window['-ACTION_PANEL-'], [create_action(row_action[0][0], row_action[1][0])])
        for rows in range(1, len(row_action[0])):
            for actions in AllActions:
                test1 = int(actions.ID.split("-")[0][:actions.ID.split("-")[0].index('A')])
                if row_action[3][rows] == test1:
                    window.extend_layout(window['-ACTION_PANEL-'],[create_action(row_action[0][rows], row_action[1][rows])])
                    for rows in range(1, len(actions.Desc.split("&"))):
                        window[f"-ACTION_TYPE_{rows}-"].update(actions.Desc.split("&")[rows])
                        window[f"-ACTION_TIMES_NUMBER_{rows}-"].update(actions.Times.split("&")[rows])
                        window[f"-ACTION_TOOL_TYPE_{rows}-"].update(actions.Tool.split("&")[rows])
                        ID = actions.ID.split("-")
                        ID_0 = ID[0][:actions.ID.split("-")[0].index('A')]
                        window[f"-ACTION_PAC_ID_{rows}-"].update(f"{ID_0}A{rows}-{ID[1]}")
            window[('-ROW_ACTION-', rows)].update(visible=False)

        window.extend_layout(window['-CHILD_PANEL-'], [create_child(row_child[0][0], row_child[1][0])])
        for rows in range(1, len(row_child[0])):
            for children in AllChildren:
                if "C" in children.ID.split("-")[0]:
                    test1 = int(children.ID.split("-")[0][:children.ID.split("-")[0].index('C')])
                    test2 = int(children.ID.split("-")[0][children.ID.split("-")[0].index('C') + 1:])
                    fastener = False
                else:
                    test1 = int(children.ID.split("-")[0][:children.ID.split("-")[0].index('c')])
                    test2 = int(children.ID.split("-")[0][children.ID.split("-")[0].index('c') + 1:])
                    fastener = True
                if row_child[3][rows] == test1 and row_child[1][rows] == test2:
                    window.extend_layout(window['-CHILD_PANEL-'],[create_child(row_child[0][rows], row_child[1][rows])])
                    window[f"-CHILD_NAME_{rows}-"].update(children.Desc)
                    window[f"-CHILD_QUANTITY_{rows}-"].update(children.Number)
                    window[f"-EoL_{rows}-"].update(children.EoL)
                    if fastener == True:
                        window[f"-FASTENER_{rows}-"].update("Yes")
                    else:
                        window[f"-FASTENER_{rows}-"].update("No")
                    window[f"-CHILD_PAC_ID_{rows}-"].update(children.ID)

            window[('-ROW_CHILD-', rows)].update(visible=False)

        if PAC_unit > 1:
            window["-PARENT_NAME_COMBO-"].update(values=children_name_ID[0])
            window["-PARENT_NAME-"].update(visible=False)
            window["-PARENT_NAME_COMBO-"].update(visible=True)
            window["-PREVIOUS_PAC_UNIT-"].update(visible=True)
            window["-DELETE_PAC_UNIT-"].update(visible=True)

        window["-PAC_UNIT-"].update(f"PAC Unit: {PAC_unit}")
        if PAC_unit == 1:
            window["-PARENT_NAME_COMBO-"].update(values=children_name_ID[0])
            window["-PARENT_NAME-"].update(visible=True)
            window["-PARENT_NAME_COMBO-"].update(visible=False)
            window["-PREVIOUS_PAC_UNIT-"].update(visible=False)
            window["-DELETE_PAC_UNIT-"].update(visible=False)

        # Updating Parent
        if PAC_unit == 1:
            window["-PARENT_NAME-"].update(AllPACUnits[PAC_unit - 1].Parent.Desc)
            window["-PARENT_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Parent.ID)
        else:
            window["-PARENT_NAME_COMBO-"].update(AllPACUnits[PAC_unit - 1].Parent.Desc)
            window[f"-PARENT_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Parent.ID)

        # Updating Parent DF's
        for rows in range(1, len(row_parent_DF[1])):
            if row_parent_DF[2][rows] == 1 and row_parent_DF[3][rows] == PAC_unit:
                window[('-ROW_PARENT_DF-', rows)].update(visible=True)

        # Updating Actions

        if "&" in AllPACUnits[PAC_unit - 1].Action.Desc:
            window["-ACTION_TYPE-"].update(
                AllPACUnits[PAC_unit - 1].Action.Desc[:AllPACUnits[PAC_unit - 1].Action.Desc.index('&') - 1])
            window["-ACTION_TIMES_NUMBER-"].update(
                AllPACUnits[PAC_unit - 1].Action.Times[:AllPACUnits[PAC_unit - 1].Action.Times.index('&') - 1])
            window["-ACTION_TOOL_TYPE-"].update(
                AllPACUnits[PAC_unit - 1].Action.Tool[:AllPACUnits[PAC_unit - 1].Action.Tool.index('&') - 1])
            window["-ACTION_DESCRIPTION-"].update(AllPACUnits[PAC_unit - 1].Action.DescDetail)
            window["-ACTION_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Action.ID)
        else:
            window["-ACTION_TYPE-"].update(AllPACUnits[PAC_unit - 1].Action.Desc)
            window["-ACTION_TIMES_NUMBER-"].update(AllPACUnits[PAC_unit - 1].Action.Times)
            window["-ACTION_TOOL_TYPE-"].update(AllPACUnits[PAC_unit - 1].Action.Tool)
            window["-ACTION_DESCRIPTION-"].update(AllPACUnits[PAC_unit - 1].Action.DescDetail)
            window["-ACTION_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Action.ID)

        for rows in range(1, len(row_action[1])):
            if row_action[2][rows] == 1 and row_action[3][rows] == PAC_unit:
                window[('-ROW_ACTION-', rows)].update(visible=True)

        # Updating Action DF's
        for rows in range(1, len(row_action_DF[1])):
            if row_action_DF[2][rows] == 1 and row_action_DF[3][rows] == PAC_unit:
                window[('-ROW_ACTION_DF-', rows)].update(visible=True)

        # Updating Children
        counter = 0
        for rows in row_child[1]:
            if row_child[2][rows - 1] == 1 and row_child[3][rows - 1] == PAC_unit:
                counter += 1
        if counter == 0:
            window["-CHILD_NAME-"].update(AllPACUnits[PAC_unit - 1].Children.Desc)
            window["-CHILD_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Children.ID)
            window["-EoL-"].update(AllPACUnits[PAC_unit - 1].Children.EoL)
            window["-CHILD_QUANTITY-"].update(AllPACUnits[PAC_unit - 1].Children.Number)
            IDAsLetters = " ".join(re.split("[^a-zA-Z]*", AllPACUnits[PAC_unit - 1].Children.ID)).strip()
            if IDAsLetters[0] == 'c':
                window["-FASTENER-"].update("Yes")
            else:
                window["-FASTENER-"].update("No")
        else:
            window["-CHILD_NAME-"].update(AllPACUnits[PAC_unit - 1].Children[0].Desc)
            window["-CHILD_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Children[0].ID)
            window["-EoL-"].update(AllPACUnits[PAC_unit - 1].Children[0].EoL)
            window["-CHILD_QUANTITY-"].update(AllPACUnits[PAC_unit - 1].Children[0].Number)
            IDAsLetters = " ".join(re.split("[^a-zA-Z]*", AllPACUnits[PAC_unit - 1].Children[0].ID)).strip()
            if IDAsLetters[0] == 'c':
                window["-FASTENER-"].update("Yes")
            else:
                window["-FASTENER-"].update("No")

            for rows in range(1, len(row_child[1])):
                if row_child[2][rows] == 1 and row_child[3][rows] == PAC_unit:
                    window[('-ROW_CHILD-', rows)].update(visible=True)

        # Updating Child DF's
        for rows in range(1, len(row_child_DF[1])):
            if row_child_DF[2][rows] == 1 and row_child_DF[3][rows] == PAC_unit:
                window[('-ROW_CHILD_DF-', rows)].update(visible=True)

        window.refresh()
        window["-CHILD_SCROLL-"].contents_changed()
        window["-ACTION_SCROLL-"].contents_changed()
        window["-PARENT_SCROLL-"].contents_changed()

    #  BOM tab
    if event == "-ADDCI-":
        CI_list.append(values["-CICHOICE-"])
        if BOM_array:
            sg.popup_error("Please don't change CI's when adding items to BOM")
            break
        if values["-CICHOICE-"] == "None":
            CI_list = []
            window["-TMRECRR-"].update(visible=False)
            window["-MREC-"].update(visible=False)
            window["-TEOL-"].update(visible=False)
            window["-MEOL-"].update(visible=False)
            window["-TMRESRE-"].update(visible=False)
            window["-MRES-"].update(visible=False)
            window["-TV-"].update(visible=False)
            window["-V-"].update(visible=False)
            window["-TW-"].update(visible=False)
            window["-W-"].update(visible=False)
            window["-TMC-"].update(visible=False)
            window["-MC-"].update(visible=False)
            window["-TWF-"].update(visible=False)
            window["-WF-"].update(visible=False)
            window["-TWC-"].update(visible=False)
            window["-WC-"].update(visible=False)
            window["-TL-"].update(visible=False)
            window["-L-"].update(visible=False)
            window["-TLAV-"].update(visible=False)
            window["-LAV-"].update(visible=False)
            prev_table = visibility_func(CI_list, prev_table)
            # BRUG Headings table
        if values["-CICHOICE-"] == "RR":
            window["-TMRECRR-"].update(visible=True)
            window["-MREC-"].update(visible=True)
            window["-TEOL-"].update(visible=True)
            window["-MEOL-"].update(visible=True)
            prev_table = visibility_func(CI_list, prev_table)
        if values["-CICHOICE-"] == "RE":
            window["-TMRESRE-"].update(visible=True)
            window["-MRES-"].update(visible=True)
            window["-TEOL-"].update(visible=True)
            window["-MEOL-"].update(visible=True)
            prev_table = visibility_func(CI_list, prev_table)

        if values["-CICHOICE-"] == "MCI":
            window["-TV-"].update(visible=True)
            window["-V-"].update(visible=True)
            window["-TW-"].update(visible=True)
            window["-W-"].update(visible=True)
            window["-TMC-"].update(visible=True)
            window["-MC-"].update(visible=True)
            window["-TWF-"].update(visible=True)
            window["-WF-"].update(visible=True)
            window["-TWC-"].update(visible=True)
            window["-WC-"].update(visible=True)
            window["-TL-"].update(visible=True)
            window["-L-"].update(visible=True)
            window["-TLAV-"].update(visible=True)
            window["-LAV-"].update(visible=True)
            prev_table = visibility_func(CI_list, prev_table)
    if event == "Add":
        if is_valid_name(values["BOM names"], BOM_array) & is_valid_quantity(values["BOM quantity"]):
            BOM_append(BOM_array, CI_list, prev_table)
            window[prev_table].update(values=BOM_array)
            BOM_array_disp = BOM_array
    if "+CLICKED+" in event:
        print(event)
        if None in event[2] or -1 == event[2][0]:
            continue
        ch = sg.popup_ok_cancel("Press OK to remove part", "Press Cancel to go back", title="OKCancel",
                                grab_anywhere=True)
        if ch == "OK":
            BOM_array.remove(BOM_array[event[2][0]][:])
            window[event[0]].update(values=BOM_array)

    # MOST tab
    if "Display" in event:
        if values["Disassembly setup"] == "Rectangular setup":
            window["Disassembly image"].update(filename="Rectangular setup.png", size=(200, 200))
            window["-TA-"].update(visible=True)
            window["-A-"].update(visible=True)
            window["-TS-"].update(visible=True)
            window["-S-"].update(visible=True)
            window["-SAVESETUP-"].update(visible=True)
        if values["Disassembly setup"] == "Circular setup":
            window["Disassembly image"].update(filename="Circular setup.png")
        if values["Disassembly setup"] == "Table setup":
            window["Disassembly image"].update(filename="Table setup.png")
    if event == "-SAVESETUP-":
        A = values["-A-"]
        S = values["-S-"]
        os.environ['A'] = str(A)
        os.environ['S'] = str(S)
    #PAC tab

    update_parent_DF()
    update_action_DF()
    if event == '-ADD_ITEM_PARENT_DF-':
        if window["-PARENT_NAME_COMBO-"].get() == "" and PAC_unit > 1:
            sg.popup_error("Choose a parent before adding disassembly failures")
            continue
        row_parent_DF[0].append(row_parent_DF[0][-1]+1)
        row_parent_DF[1].append(row_parent_DF[1][-1] + 1)
        row_parent_DF[2].append(1)
        row_parent_DF[3].append(PAC_unit)
        window.extend_layout(window['-PARENT_DF_PANEL-'], [create_parent_DF(row_parent_DF[0][-1], row_parent_DF[1][-1])])
        window.refresh()
        window["-PARENT_SCROLL-"].contents_changed()

    if event[0] == '-DEL_PARENT_DF-':
        order_test = []
        for row in range(len(row_parent_DF[2])):
            if row_parent_DF[2][row] == 1:
                order_test.append(row_parent_DF[0][row])

        if event[1] != max(order_test):
            sg.popup_error("Start by deleting the lowest disassembly failure")
            continue

        print(row_parent_DF)
        row_parent_DF[0].append(row_parent_DF[0][-1])
        row_parent_DF[1].append(row_parent_DF[1][-1] - 1)
        row_parent_DF[2].append(0)
        row_parent_DF[3].append(PAC_unit)

        for rows in range(len(origin_PAC_unit[PAC_unit-1])):
            if origin_PAC_unit[PAC_unit-1][rows][0:3] == f"{PAC_unit}P1":
                result = rows
        if PAC_unit > 1:
            try:
                origin_PAC_unit[PAC_unit-1].pop(result)
            except NameError:
                continue
        row_parent_DF[0].pop(-2)
        row_parent_DF[1].pop(-2)
        row_parent_DF[2].pop(-2)
        row_parent_DF[3].pop(-2)
        row_parent_DF[2][event[1]] = 0
        print(row_parent_DF)
        window[('-ROW_PARENT_DF-', event[1])].update(visible=False)
        window.refresh()
        window["-PARENT_SCROLL-"].contents_changed()

    if event == '-ADD_ITEM_ACTION_DF-':
        row_action_DF[0].append(row_action_DF[0][-1] + 1)
        row_action_DF[1].append(row_action_DF[1][-1] + 1)
        row_action_DF[2].append(1)
        row_action_DF[3].append(PAC_unit)
        window.extend_layout(window['-ACTION_DF_PANEL-'], [create_action_DF(row_action_DF[0][-1], row_action_DF[1][-1])])
        window.refresh()
        window["-ACTION_SCROLL-"].contents_changed()
        #This loop changes the different actions that a disassembly failure can be attributed to when the amount of actions changes
        action_DF_affected_ID()

    if event[0] == '-DEL_ACTION_DF-':
        order_test = []
        for row in range(len(row_action_DF[2])):
            if row_action_DF[2][row] == 1:
                order_test.append(row_action_DF[0][row])
        if event[1] != max(order_test):
            sg.popup_error("Start by deleting the lowest disassembly failure")
            continue

        row_action_DF[0].append(row_action_DF[0][-1])
        row_action_DF[1].append(row_action_DF[1][-1] - 1)
        row_action_DF[2].append(0)
        row_action_DF[3].append(PAC_unit)
        window[('-ROW_ACTION_DF-', event[1])].update(visible=False)

        for rows in range(len(origin_PAC_unit[PAC_unit-1])):
            if origin_PAC_unit[PAC_unit-1][rows][0:3] == f"{PAC_unit}A1":
                result = rows
        try:
            origin_PAC_unit[PAC_unit-1].pop(result)
        except NameError:
            continue
        row_action_DF[0].pop(-2)
        row_action_DF[1].pop(-2)
        row_action_DF[2].pop(-2)
        row_action_DF[3].pop(-2)
        row_action_DF[2][event[1]] = 0
        window.refresh()
        window["-ACTION_SCROLL-"].contents_changed()
        #This loop changes the different actions that a disassembly failure can be attributed to when the amount of actions changes
        action_DF_affected_ID()

    if event == '-ADD_ITEM_CHILD_DF-':
        row_child_DF[0].append(row_child_DF[0][-1] + 1)
        row_child_DF[1].append(row_child_DF[1][-1] + 1)
        row_child_DF[2].append(1)
        row_child_DF[3].append(PAC_unit)
        window.extend_layout(window['-CHILD_DF_PANEL-'], [create_child_DF(row_child_DF[0][-1], row_child_DF[1][-1])])
        window.refresh()
        window["-CHILD_SCROLL-"].contents_changed()
        #Same as for the action DF
        child_DF_affected_ID()

    if event[0] == '-DEL_CHILD_DF-':
        order_test = []
        for row in range(len(row_child_DF[2])):
            if row_child_DF[2][row] == 1:
                order_test.append(row_child_DF[0][row])
        if event[1] != max(order_test):
            sg.popup_error("Start by deleting the lowest disassembly failure")
            continue

        row_child_DF[0].append(row_child_DF[0][-1])
        row_child_DF[1].append(row_child_DF[1][-1] - 1)
        row_child_DF[2].append(0)
        row_child_DF[3].append(PAC_unit)
        window[('-ROW_CHILD_DF-', event[1])].update(visible=False)
        row_child_DF[0].pop(-2)
        row_child_DF[1].pop(-2)
        row_child_DF[2].pop(-2)
        row_child_DF[3].pop(-2)
        row_child_DF[2][event[1]] = 0
        window.refresh()
        window["-CHILD_SCROLL-"].contents_changed()
        # Same as for the action DF
        child_DF_affected_ID()

    if event == '-ADD_ITEM_ACTION-':
        row_action[0].append(row_action[0][-1] + 1)
        row_action[1].append(row_action[1][-1] + 1)
        row_action[2].append(1)
        row_action[3].append(PAC_unit)
        window.extend_layout(window['-ACTION_PANEL-'], [create_action(row_action[0][-1], row_action[1][-1])])
        window.refresh()
        window["-ACTION_SCROLL-"].contents_changed()
        #This loop changes the different actions that a disassembly failure can be attributed to when the amount of actions changes
        action_DF_affected_ID()

    if event[0] == '-DEL_ACTION-':
        order_test = []
        for row in range(len(row_action[2])):
            if row_action[2][row] == 1:
                order_test.append(row_action[0][row])
        if event[1] != max(order_test):
            sg.popup_error("Start by deleting the lowest action")
            continue

        row_action[0].append(row_action[0][-1])
        row_action[1].append(row_action[1][-1] - 1)
        row_action[2].append(0)
        row_action[3].append(PAC_unit)
        window[('-ROW_ACTION-', event[1])].update(visible=False)
        row_action[0].pop(-2)
        row_action[1].pop(-2)
        row_action[2].pop(-2)
        row_action[3].pop(-2)
        row_action[2][event[1]] = 0
        window.refresh()
        window["-ACTION_SCROLL-"].contents_changed()
        #This loop changes the different actions that a disassembly failure can be attributed to when the amount of actions changes
        action_DF_affected_ID()

    if event == '-ADD_ITEM_CHILD-':
        row_child[0].append(row_child[0][-1] + 1)
        row_child[1].append(row_child[1][-1] + 1)
        row_child[2].append(1)
        row_child[3].append(PAC_unit)
        window.extend_layout(window['-CHILD_PANEL-'], [create_child(row_child[0][-1], row_child[1][-1])])
        window.refresh()
        window["-CHILD_SCROLL-"].contents_changed()
        # Same as for the action DF
        child_DF_affected_ID()

    if event[0] == '-DEL_CHILD-':
        order_test = []
        for row in range(len(row_child[2])):
            if row_child[2][row] == 1:
                order_test.append(row_child[0][row])
        if event[1] != max(order_test):
            sg.popup_error("Start by deleting the lowest child")
            continue

        row_child[0].append(row_child[0][-1])
        row_child[1].append(row_child[1][-1] - 1)
        row_child[2].append(0)
        row_child[3].append(PAC_unit)
        window[('-ROW_CHILD-', event[1])].update(visible=False)
        row_child[0].pop(-2)
        row_child[1].pop(-2)
        row_child[2].pop(-2)
        row_child[3].pop(-2)
        row_child[2][event[1]] = 0
        window.refresh()
        window["-CHILD_SCROLL-"].contents_changed()
        # Same as for the action DF
        child_DF_affected_ID()

    if event == "-CHECK_PAC_ID-":
        #Her skal der laves et tjek for om det givne PAC unit allerede er blevet gemt og hvis det er skal værdierne bare opdateres i stedet for at gemmes igen
        error[PAC_unit - 1] = 0

        if PAC_unit in check_PAC_ID:
            check_PAC_ID.pop()
        check_PAC_ID.append(PAC_unit)
        print(check_PAC_ID)

        #These values should be zero from the get go, the program is just fucking with me on purpose
        row_parent_DF[2][0] = 0
        row_action_DF[2][0] = 0
        row_child_DF[2][0] = 0
        row_action[2][0] = 0
        row_child[2][0] = 0
        row_counter_visible = 0


        #Giving the correct PAC and DF ID to the user and saving all values in classes
        if PAC_unit == 1:
            window["-PARENT_PAC_ID-"].update("Parent PAC ID: 1P1-000")
            window["-ACTION_PAC_ID-"].update("Action PAC ID: 1A1-000")
            window["-CHILD_PAC_ID-"].update("Child PAC ID: 1C1-000")
            child_relation_ID_1("1C1")
            parent_class_1('1P1-000')
            action_class_1('1A1-000')
            if window["-FASTENER-"].get() == '':
                sg.popup_error("You have to choose if the child is a fastener, then click Check PAC ID again")
                error[PAC_unit - 1] += 1
                continue
            elif window["-FASTENER-"].get() == "No":
                child_class_1('1C1-000')
            else:
                child_class_1('1c1-000')
            for rows in row_action[0]:
                if row_action[2][rows] == 1 and row_action[3][rows] == PAC_unit:
                    window[f"-ACTION_PAC_ID_{row_action[0][rows]}-"].update(f"Action PAC ID: {PAC_unit}A{row_action[1][rows]}-000")
                    action_class(f'{PAC_unit}A1-000', row_action[0][rows])
            for rows in row_child[0]:
                if row_child[2][rows] == 1 and row_child[3][rows] == PAC_unit:
                    window[f"-CHILD_PAC_ID_{row_child[0][rows]}-"].update(f"Child PAC ID: {PAC_unit}C{row_child[1][rows]}-000")
                    child_relation_ID(f"{PAC_unit}C{row_child[1][rows]}",row_child[0][rows])
                    if window[f"-FASTENER_{rows}-"].get() == '':
                        sg.popup_error("You have to choose if the child is a fastener, then click Check PAC ID again")
                        error[PAC_unit - 1] += 1
                        continue
                    elif window[f"-FASTENER_{rows}-"].get() == "No":
                        child_class(f'{PAC_unit}C{row_child[1][rows]}-000',row_child[0][rows])
                    else:
                        child_class(f'{PAC_unit}c{row_child[1][rows]}-000',row_child[0][rows])
            for rows in row_parent_DF[0]:
                if row_parent_DF[2][rows] == 1 and row_parent_DF[3][rows] == PAC_unit:
                    window[f"-PARENT_DF_ID_{row_parent_DF[0][rows]}-"].update(f"Parent DF ID: 1P1-000-000-1D{row_parent_DF[1][rows]}")
                    parent_DF_class(f"1P1-000-000-1D{row_parent_DF[1][rows]}", rows)
            for rows in row_action_DF[0]:
                if row_action_DF[2][rows] == 1 and row_action_DF[3][rows] == PAC_unit:
                    action_ID_for_DF = values[f"-ACTION_ID_FOR_DF_{row_action_DF[0][rows]}-"]
                    if action_ID_for_DF == "": #Checks if the DF has been correctly set to a specific action
                        sg.popup_error("Remember to fill out what action is affected by the disassembly failure")
                        error[PAC_unit - 1] += 1
                        continue
                    if window[f"-ACTION_ORIGIN_{rows}-"].get() == "Origin here":
                        window[f"-ACTION_DF_ID_{row_action_DF[0][rows]}-"].update(f"Action DF ID: 1A{row_action_DF[1][rows]}-000-000-1D{row_action_DF[1][rows]}")
                        action_DF_class(f"1A{row_action_DF[1][rows]}-000-000-1D{row_action_DF[1][rows]}", rows)
                    else:
                        #print(origin_PAC_unit[PAC_unit - 1][origin_number_action_DF[PAC_unit - 1].index(row_action_DF[1][rows])])
                        #relation = origin_PAC_unit[PAC_unit-1][origin_number_action_DF[PAC_unit-1].index(row_action_DF[1][rows])].split("-")[2]
                        relation = window[f"-ACTION_ORIGIN_{rows}-"].get().split("-")[0]
                        print(relation)
                        window[f"-ACTION_DF_ID_{row_action_DF[0][rows]}-"].update(f"Action DF ID: 1A{row_action_DF[1][rows]}-000-{relation}-1D{row_action_DF[1][rows]}")
                        action_DF_class(f"1A{row_action_DF[1][rows]}-000-{relation}-1D{row_action_DF[1][rows]}", rows)
            for rows in row_child_DF[0]:
                if row_child_DF[2][rows] == 1 and row_child_DF[3][rows] == PAC_unit:
                    child_ID_for_DF = values[f"-CHILD_ID_FOR_DF_{row_child_DF[0][rows]}-"]
                    if child_ID_for_DF == "": #Checks if the DF has been correctly set to a specific child
                        sg.popup_error("Remember to fill out what child is affected by the disassembly failure")
                        error[PAC_unit - 1] += 1
                        continue
                    related_child = window[f"-CHILD_ID_FOR_DF_{rows}-"].get()
                    if window[f"-CHILD_ORIGIN_{rows}-"].get() == "Origin here":
                        window[f"-CHILD_DF_ID_{row_child_DF[0][rows]}-"].update(f"Child DF ID: 1C{related_child}-000-000-1D{row_child_DF[1][rows]}")
                        child_DF_class(f"1C{related_child}-000-000-1D{row_child_DF[1][rows]}", rows)
                        window[f"-CHILD_DF_ID_{row_child_DF[0][rows]}-"].update(f"Child DF ID: 1C{related_child}-000-000-1D{row_child_DF[1][rows]}")
                    else:
                        print(window[f"-CHILD_ORIGIN_{rows}-"])
                        relation = window[f"-CHILD_ORIGIN_{rows}-"].get().split("-")[0]
                        print(relation)
                        window[f"-CHILD_DF_ID_{row_child_DF[0][rows]}-"].update(f"Child DF ID: 1C{related_child}-000-{relation}-1D{row_child_DF[1][rows]}")
                        child_DF_class(f"1C{related_child}-000-{relation}-1D{row_child_DF[1][rows]}", rows)
                        window[f"-CHILD_DF_ID_{row_child_DF[0][rows]}-"].update(f"Child DF ID: 1C{related_child}-000-{relation}-1D{row_child_DF[1][rows]}")
                    if related_child == 1:
                        if window["-FASTENER-"].get() == "No":
                            if window[f"-CHILD_ORIGIN_{rows}-"].get() == "Origin here":
                                origin_global.append(f"1C{related_child}-000-000-1D{row_child_DF[1][rows]}")
                            else:
                                origin_global.append(f"1C{related_child}-000-{relation}-1D{row_child_DF[1][rows]}")
                    else:
                        for rows in row_child[0]:
                            if row_child[1][rows] == related_child and row_child[2][rows] == 1 and row_child[3][rows] == PAC_unit:
                                row_value = row_child[0][rows]
                        if window[f"-FASTENER_{row_value}-"].get() == "No":
                            if window[f"-CHILD_ORIGIN_{rows}-"].get() == "Origin here":
                                origin_global.append(f"1C{related_child}-000-000-1D{row_child_DF[1][rows]}")
                            else:
                                origin_global.append(f"1C{related_child}-000-{relation}-1D{row_child_DF[1][rows]}")

        else:
            if window["-PARENT_NAME_COMBO-"].get() == "":
                sg.popup_error("Fill out the name of the parent before checking the PAC ID's")
                error[PAC_unit - 1] += 1
                continue

            name = window["-PARENT_NAME_COMBO-"].get()
            ID = child_relation_name(name)
            window["-PARENT_PAC_ID-"].update(f"Parent PAC ID: {PAC_unit}P1-{ID}")
            window["-ACTION_PAC_ID-"].update(f"Action PAC ID: {PAC_unit}A1-{ID}")
            window["-CHILD_PAC_ID-"].update(f"Child PAC ID: {PAC_unit}C1-{ID}")
            child_relation_ID_1(f"{PAC_unit}C1")
            parent_class(f"{PAC_unit}P1-{ID}")
            action_class_1(f"{PAC_unit}A1-{ID}")
            if window["-FASTENER-"].get() == '':
                sg.popup_error("You have to choose if the child is a fastener, then click Check PAC ID again")
                error[PAC_unit - 1] += 1
                continue
            elif window["-FASTENER-"].get() == "No":
                child_class_1(f"{PAC_unit}C1-{ID}")
            else:
                child_class_1(f"{PAC_unit}c1-{ID}")

            for rows in row_action[0]:
                if row_action[2][rows] == 1 and row_action[3][rows] == PAC_unit:
                    window[f"-ACTION_PAC_ID_{row_action[0][rows]}-"].update(f"Action PAC ID: {PAC_unit}A{row_action[1][rows]-action_diff[PAC_unit-1]+1}-{ID}")
                    action_class(f'{PAC_unit}A1-{ID}', row_action[0][rows])
            for rows in row_child[0]:
                if row_child[2][rows] == 1 and row_child[3][rows] == PAC_unit:
                    window[f"-CHILD_PAC_ID_{row_child[0][rows]}-"].update(f"Child PAC ID: {PAC_unit}C{row_child[1][rows]-child_diff[PAC_unit-1]+1}-{ID}")
                    child_relation_ID(f"{PAC_unit}C{row_child[1][rows]}",row_child[0][rows])
                    if window[f"-FASTENER_{rows}-"].get() == '':
                        sg.popup_error("You have to choose if the child is a fastener, then click Check PAC ID again")
                        error[PAC_unit - 1] += 1
                        continue
                    elif window[f"-FASTENER_{rows}-"].get() == "No":
                        child_class(f'{PAC_unit}C{row_child[1][rows]-child_diff[PAC_unit-1]+1}-{ID}', row_child[0][rows])
                    else:
                        child_class(f'{PAC_unit}c{row_child[1][rows]-child_diff[PAC_unit-1]+1}-{ID}', row_child[0][rows])
            for rows in row_parent_DF[0]:
                if row_parent_DF[2][rows] == 1 and row_parent_DF[3][rows] == PAC_unit:
                    relation = window[f"-PARENT_ORIGIN_{rows}-"].get().split("-")[0]
                    if relation == "Origin here":
                        window[f"-PARENT_DF_ID_{rows}-"].update(f"Parent DF ID: {PAC_unit}P1-{relation}-{000}-{PAC_unit}D{row_parent_DF[1][rows]}")
                    else:
                        window[f"-PARENT_DF_ID_{rows}-"].update(f"Parent DF ID: {PAC_unit}P1-{relation}-{relation}-{PAC_unit}D{row_parent_DF[1][rows]}")
                    parent_DF_class(f"{PAC_unit}P1-{relation}-{relation}-{PAC_unit}D{row_parent_DF[1][rows]}", rows)
            for rows in row_action_DF[0]:
                if row_action_DF[2][rows] == 1 and row_action_DF[3][rows] == PAC_unit:
                    action_ID_for_DF = values[f"-ACTION_ID_FOR_DF_{row_action_DF[0][rows]}-"]
                    if action_ID_for_DF == "":  # Checks if the DF has been correctly set to a specific action
                        sg.popup_error("Remember to fill out what action is affected by the disassembly failure")
                        error[PAC_unit - 1] += 1
                        continue
                    if window[f"-ACTION_ORIGIN_{rows}-"].get() == "Origin here":
                        relation_child = window["-PARENT_PAC_ID-"].get().split("-")[1]
                        window[f"-ACTION_DF_ID_{row_action_DF[0][rows]}-"].update(f"Action DF ID: {PAC_unit}A{row_action_DF[1][rows]}-{relation_child}-000-{PAC_unit}D{row_action_DF[1][rows]}")
                        action_DF_class(f"{PAC_unit}A{row_action_DF[1][rows]}-{relation_child}-000-{PAC_unit}D{row_action_DF[1][rows]}", rows)
                    else:
                        relation_DF = window[f"-ACTION_ORIGIN_{rows}-"].get().split("-")[0]
                        relation_child = window["-PARENT_PAC_ID-"].get().split("-")[1]
                        window[f"-ACTION_DF_ID_{row_action_DF[0][rows]}-"].update(f"Action DF ID: {PAC_unit}A{row_action_DF[1][rows]}-{relation_child}-{relation_DF}-{PAC_unit}D{row_action_DF[1][rows]}")
                        action_DF_class(f"{PAC_unit}A{row_action_DF[1][rows]}-{relation_child}-{relation_DF}-{PAC_unit}D{row_action_DF[1][rows]}", rows)
            for rows in row_child_DF[0]:
                if row_child_DF[2][rows] == 1 and row_child_DF[3][rows] == PAC_unit:
                    child_ID_for_DF = values[f"-CHILD_ID_FOR_DF_{row_child_DF[0][rows]}-"]
                    print(child_ID_for_DF)
                    if child_ID_for_DF == "":  # Checks if the DF has been correctly set to a specific child
                        sg.popup_error("Remember to fill out what child is affected by the disassembly")
                        error[PAC_unit - 1] += 1
                        continue
                    related_child = window[f"-CHILD_ID_FOR_DF_{rows}-"].get()
                    if window[f"-CHILD_ORIGIN_{rows}-"].get() == "Origin here":
                        relation_parent = window["-PARENT_PAC_ID-"].get().split("-")[1]
                        window[f"-CHILD_DF_ID_{rows}-"].update(f"Child DF ID: {PAC_unit}C{related_child}-{relation_parent}-000-{PAC_unit}D{row_child_DF[1][rows]}")
                        child_DF_class(f"{PAC_unit}C{related_child}-{relation_parent}-000-{PAC_unit}D{row_child_DF[1][rows]}", rows)
                        window[f"-CHILD_DF_ID_{rows}-"].update(f"Child DF ID: {PAC_unit}C{related_child}-{relation_parent}-000-{PAC_unit}D{row_child_DF[1][rows]}")
                    else:
                        relation = window[f"-CHILD_ORIGIN_{rows}-"].get().split("-")[0]
                        relation_parent = window["-PARENT_PAC_ID-"].get().split("-")[1]
                        window[f"-CHILD_DF_ID_{rows}-"].update(f"Child DF ID: {PAC_unit}C{related_child}-{relation_parent}-{relation}-{PAC_unit}D{row_child_DF[1][rows]}")
                        child_DF_class(f"{PAC_unit}C{related_child}-{relation_parent}-{relation}-{PAC_unit}D{row_child_DF[1][rows]}", rows)
                        window[f"-CHILD_DF_ID_{rows}-"].update(f"Child DF ID: {PAC_unit}C{related_child}-{relation_parent}-{relation}-{PAC_unit}D{row_child_DF[1][rows]}")
                    if related_child == 1:
                        if window["-FASTENER-"].get() == "No":
                            if window[f"-CHILD_ORIGIN_{rows}-"].get() == "Origin here":
                                relation_parent = window["-PARENT_PAC_ID-"].get().split("-")[1]
                                origin_global.append(f"{PAC_unit}C{related_child}-{relation_parent}-000-{PAC_unit}D{row_child_DF[1][rows]}")
                            else:
                                relation = window[f"-CHILD_ORIGIN_{rows}-"].get().split("-")[0]
                                relation_parent = window["-PARENT_PAC_ID-"].get().split("-")[1]
                                origin_global.append(f"{PAC_unit}C{related_child}-{relation_parent}-{relation}-{PAC_unit}D{row_child_DF[1][rows]}")
                    else:
                        for rows in row_child[0]:
                            if row_child[1][rows] == related_child and row_child[2][rows] == 1 and row_child[3][rows] == PAC_unit:
                                row_value = row_child[0][rows]
                        if window[f"-FASTENER_{row_value}-"].get() == "No":
                            if window[f"-CHILD_ORIGIN_{rows}-"].get() == "Origin here":
                                relation_parent = window["-PARENT_PAC_ID-"].get().split("-")[1]
                                origin_global.append(f"{PAC_unit}C{related_child}-{relation_parent}-000-{PAC_unit}D{row_child_DF[1][rows]}")
                            else:
                                relation = window[f"-CHILD_ORIGIN_{rows}-"].get().split("-")[0]
                                relation_parent = window["-PARENT_PAC_ID-"].get().split("-")[1]
                                origin_global.append(f"{PAC_unit}C{related_child}-{relation_parent}-{relation}-{PAC_unit}D{row_child_DF[1][rows]}")

        AllPACUnits = [PACUnit(i) for i in range(1, check_PAC_ID[-1] + 1)]
        PACUnitInsert(AllParents, AllPACUnits)
        PACUnitInsert(AllChildren, AllPACUnits)
        PACUnitInsert(AllActions, AllPACUnits)

    if event == "-NEXT_PAC_UNIT-":
        #  Update the names in the BOM list
        names_quant = []
        if isinstance(AllPACUnits[PAC_unit - 1].Children, list):
            for children in AllPACUnits[PAC_unit - 1].Children:
                names_quant.append([children.Desc, children.Number])
        else:
            names_quant = [[AllPACUnits[PAC_unit - 1].Children.Desc, AllPACUnits[PAC_unit - 1].Children.Number]]
        BOM_array_disp = BOM_quant_left(names_quant, BOM_array_disp)


        if PAC_unit not in check_PAC_ID:
            sg.popup_error("You have to check the PAC ID before going to the next PAC Unit")
            continue
        PAC_unit += 1
        origin_PAC_unit.append(["Origin here"])
        origin_number_parent_DF.append([])
        origin_number_action_DF.append([])
        error.append(0)
        window["-PAC_UNIT-"].update(f"PAC Unit: {PAC_unit}")
        if PAC_unit > 1:
            window["-PREVIOUS_PAC_UNIT-"].update(visible=True)
            window["-DELETE_PAC_UNIT-"].update(visible=True)

        #Making it so that the parent is named after previous children
        window["-PARENT_NAME_COMBO-"].update(values=children_name_ID[0])
        window["-PARENT_NAME-"].update(visible=False)
        window["-PARENT_NAME_COMBO-"].update(visible=True)
        print(check_PAC_ID)
        print(PAC_unit)
        if PAC_unit not in check_PAC_ID:
            #The part that clear the PAC information
            window["-PARENT_NAME-"].update('')
            window["-PARENT_PAC_ID-"].update('')
            window["-ACTION_TYPE-"].update('')
            window["-ACTION_PAC_ID-"].update('')
            window["-ACTION_DESCRIPTION-"].update('')
            window["-ACTION_TIMES_NUMBER-"].update('')
            window["-ACTION_TOOL_TYPE-"].update('')
            window["-CHILD_NAME-"].update('')
            window["-CHILD_PAC_ID-"].update('')
            window["-CHILD_QUANTITY-"].update('')
            window["-EoL-"].update('')
            window["-FASTENER-"].update('')

            #Removing all visible windows of children and actions
            parent_DF_diff.append(row_parent_DF[1][-1]+parent_DF_diff[-1])
            for rows in row_parent_DF[0]:
                window[('-ROW_PARENT_DF-', rows)].update(visible=False)
            action_diff.append(row_action[1][-1] + action_diff[-1])
            for rows in row_action[0]:
                window[('-ROW_ACTION-', rows)].update(visible=False)
            child_diff.append(row_child[1][-1] + child_diff[-1])
            for rows in range(1,len(row_child[0])):
                window[('-ROW_CHILD-', rows)].update(visible=False)
            action_DF_diff.append(row_action_DF[1][-1] + action_DF_diff[-1])
            for rows in row_action_DF[0]:
                window[('-ROW_ACTION_DF-', rows)].update(visible=False)
            child_DF_diff.append(row_child_DF[1][-1] + child_DF_diff[-1])
            for rows in row_child_DF[0]:
                window[('-ROW_CHILD_DF-', rows)].update(visible=False)
        else:
            # Updating Parent
            if PAC_unit == 1:
                window["-PARENT_NAME-"].update(AllPACUnits[PAC_unit - 1].Parent.Desc)
                window["-PARENT_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Parent.ID)
            else:
                window["-PARENT_NAME_COMBO-"].update(AllPACUnits[PAC_unit - 1].Parent.Desc)
                window[f"-PARENT_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Parent.ID)

            # Updating Parent DF's
            for rows in range(1, len(row_parent_DF[1])):
                if row_parent_DF[2][rows] == 1 and row_parent_DF[3][rows] == PAC_unit:
                    window[('-ROW_PARENT_DF-', rows)].update(visible=True)

            # Updating Actions

            if "&" in AllPACUnits[PAC_unit - 1].Action.Desc:
                window["-ACTION_TYPE-"].update(
                    AllPACUnits[PAC_unit - 1].Action.Desc[:AllPACUnits[PAC_unit - 1].Action.Desc.index('&') - 1])
                window["-ACTION_TIMES_NUMBER-"].update(
                    AllPACUnits[PAC_unit - 1].Action.Times[:AllPACUnits[PAC_unit - 1].Action.Times.index('&') - 1])
                window["-ACTION_TOOL_TYPE-"].update(
                    AllPACUnits[PAC_unit - 1].Action.Tool[:AllPACUnits[PAC_unit - 1].Action.Tool.index('&') - 1])
                window["-ACTION_DESCRIPTION-"].update(AllPACUnits[PAC_unit - 1].Action.DescDetail)
                window["-ACTION_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Action.ID)
            else:
                window["-ACTION_TYPE-"].update(AllPACUnits[PAC_unit - 1].Action.Desc)
                window["-ACTION_TIMES_NUMBER-"].update(AllPACUnits[PAC_unit - 1].Action.Times)
                window["-ACTION_TOOL_TYPE-"].update(AllPACUnits[PAC_unit - 1].Action.Tool)
                window["-ACTION_DESCRIPTION-"].update(AllPACUnits[PAC_unit - 1].Action.DescDetail)
                window["-ACTION_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Action.ID)

            for rows in range(1, len(row_action[1])):
                if row_action[2][rows] == 1 and row_action[3][rows] == PAC_unit:
                    window[('-ROW_ACTION-', rows)].update(visible=True)

            # Updating Action DF's
            for rows in range(1, len(row_action_DF[1])):
                if row_action_DF[2][rows] == 1 and row_action_DF[3][rows] == PAC_unit:
                    window[('-ROW_ACTION_DF-', rows)].update(visible=True)

            # Updating Children
            counter = 0
            for rows in row_child[1]:
                if row_child[2][rows - 1] == 1 and row_child[3][rows - 1] == PAC_unit:
                    counter += 1
            if counter == 0:
                window["-CHILD_NAME-"].update(AllPACUnits[PAC_unit - 1].Children.Desc)
                window["-CHILD_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Children.ID)
                window["-EoL-"].update(AllPACUnits[PAC_unit - 1].Children.EoL)
                window["-CHILD_QUANTITY-"].update(AllPACUnits[PAC_unit - 1].Children.Number)
                IDAsLetters = " ".join(re.split("[^a-zA-Z]*", AllPACUnits[PAC_unit - 1].Children.ID)).strip()
                if IDAsLetters[0] == 'c':
                    window["-FASTENER-"].update("Yes")
                else:
                    window["-FASTENER-"].update("No")

            else:
                window["-CHILD_NAME-"].update(AllPACUnits[PAC_unit - 1].Children[0].Desc)
                window["-CHILD_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Children[0].ID)
                window["-EoL-"].update(AllPACUnits[PAC_unit - 1].Children[0].EoL)
                window["-CHILD_QUANTITY-"].update(AllPACUnits[PAC_unit - 1].Children[0].Number)
                IDAsLetters = " ".join(re.split("[^a-zA-Z]*", AllPACUnits[PAC_unit - 1].Children[0].ID)).strip()
                if IDAsLetters[0] == 'c':
                    window["-FASTENER-"].update("Yes")
                else:
                    window["-FASTENER-"].update("No")

                for rows in range(1, len(row_child[1])):
                    if row_child[2][rows] == 1 and row_child[3][rows] == PAC_unit:
                        window[('-ROW_CHILD-', rows)].update(visible=True)

            # Updating Child DF's
            for rows in range(1, len(row_child_DF[1])):
                if row_child_DF[2][rows] == 1 and row_child_DF[3][rows] == PAC_unit:
                    window[('-ROW_CHILD_DF-', rows)].update(visible=True)

        window.refresh()
        window["-CHILD_SCROLL-"].contents_changed()
        window["-ACTION_SCROLL-"].contents_changed()
        window["-PARENT_SCROLL-"].contents_changed()

    if event == "-DELETE_PAC_UNIT-":
        if PAC_unit < check_PAC_ID[-1]:
            sg.popup_error("Start by deleting the last PAC unit")
            continue

        #The part that removes all parents, actions and children from AllClasses for the given PAC unit

        #The part that clears the current PAC unit window and moves back to the previous.

    if event == "-PREVIOUS_PAC_UNIT-":
        PAC_unit -= 1
        window["-PAC_UNIT-"].update(f"PAC Unit: {PAC_unit}")
        if PAC_unit == 1:
            window["-PARENT_NAME_COMBO-"].update(values=children_name_ID[0])
            window["-PARENT_NAME-"].update(visible=True)
            window["-PARENT_NAME_COMBO-"].update(visible=False)
            window["-PREVIOUS_PAC_UNIT-"].update(visible=False)
            window["-DELETE_PAC_UNIT-"].update(visible=False)


        #Updating Parent
        if PAC_unit == 1:
            window["-PARENT_NAME-"].update(AllPACUnits[PAC_unit-1].Parent.Desc)
            window["-PARENT_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Parent.ID)
        else:
            window["-PARENT_NAME_COMBO-"].update(AllPACUnits[PAC_unit-1].Parent.Desc)
            window[f"-PARENT_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Parent.ID)

        #Updating Parent DF's
        for rows in range(1, len(row_parent_DF[1])):
            if row_parent_DF[2][rows] == 1 and row_parent_DF[3][rows] == PAC_unit:
                window[('-ROW_PARENT_DF-', rows)].update(visible=True)

        #Updating Actions

        if "&" in AllPACUnits[PAC_unit-1].Action.Desc:
            window["-ACTION_TYPE-"].update(AllPACUnits[PAC_unit-1].Action.Desc[:AllPACUnits[PAC_unit-1].Action.Desc.index('&')-1])
            window["-ACTION_TIMES_NUMBER-"].update(AllPACUnits[PAC_unit-1].Action.Times[:AllPACUnits[PAC_unit-1].Action.Times.index('&')-1])
            window["-ACTION_TOOL_TYPE-"].update(AllPACUnits[PAC_unit-1].Action.Tool[:AllPACUnits[PAC_unit-1].Action.Tool.index('&')-1])
            window["-ACTION_DESCRIPTION-"].update(AllPACUnits[PAC_unit-1].Action.DescDetail)
            window["-ACTION_PAC_ID-"].update(AllPACUnits[PAC_unit-1].Action.ID)
        else:
            window["-ACTION_TYPE-"].update(AllPACUnits[PAC_unit - 1].Action.Desc)
            window["-ACTION_TIMES_NUMBER-"].update(AllPACUnits[PAC_unit - 1].Action.Times)
            window["-ACTION_TOOL_TYPE-"].update(AllPACUnits[PAC_unit - 1].Action.Tool)
            window["-ACTION_DESCRIPTION-"].update(AllPACUnits[PAC_unit - 1].Action.DescDetail)
            window["-ACTION_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Action.ID)

        for rows in range(1, len(row_action[1])):
            if row_action[2][rows] == 1 and row_action[3][rows] == PAC_unit:
                window[('-ROW_ACTION-', rows)].update(visible=True)

        # Updating Action DF's
        for rows in range(1, len(row_action_DF[1])):
            if row_action_DF[2][rows] == 1 and row_action_DF[3][rows] == PAC_unit:
                window[('-ROW_ACTION_DF-', rows)].update(visible=True)


        #Updating Children
        counter = 0
        for rows in row_child[1]:
            if row_child[2][rows-1] == 1 and row_child[3][rows-1] == PAC_unit:
                counter += 1
        if counter == 0:
            window["-CHILD_NAME-"].update(AllPACUnits[PAC_unit-1].Children.Desc)
            window["-CHILD_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Children.ID)
            window["-EoL-"].update(AllPACUnits[PAC_unit - 1].Children.EoL)
            window["-CHILD_QUANTITY-"].update(AllPACUnits[PAC_unit - 1].Children.Number)
            IDAsLetters = " ".join(re.split("[^a-zA-Z]*", AllPACUnits[PAC_unit - 1].Children.ID)).strip()
            if IDAsLetters[0] == 'c':
                window["-FASTENER-"].update("Yes")
            else:
                window["-FASTENER-"].update("No")

        else:
            window["-CHILD_NAME-"].update(AllPACUnits[PAC_unit - 1].Children[0].Desc)
            window["-CHILD_PAC_ID-"].update(AllPACUnits[PAC_unit - 1].Children[0].ID)
            window["-EoL-"].update(AllPACUnits[PAC_unit - 1].Children[0].EoL)
            window["-CHILD_QUANTITY-"].update(AllPACUnits[PAC_unit - 1].Children[0].Number)
            IDAsLetters = " ".join(re.split("[^a-zA-Z]*", AllPACUnits[PAC_unit - 1].Children[0].ID)).strip()
            if IDAsLetters[0] == 'c':
                window["-FASTENER-"].update("Yes")
            else:
                window["-FASTENER-"].update("No")

            for rows in range(1, len(row_child[1])):
                if row_child[2][rows] == 1 and row_child[3][rows] == PAC_unit:
                    window[('-ROW_CHILD-', rows)].update(visible=True)

        # Updating Child DF's
        for rows in range(1, len(row_child_DF[1])):
            if row_child_DF[2][rows] == 1 and row_child_DF[3][rows] == PAC_unit:
                window[('-ROW_CHILD_DF-', rows)].update(visible=True)

        window.refresh()
        window["-CHILD_SCROLL-"].contents_changed()
        window["-ACTION_SCROLL-"].contents_changed()
        window["-PARENT_SCROLL-"].contents_changed()

    update_parent_DF()
    update_action_DF()
    window["-CHILD_NAME-"].update(values=get_BOM_names())
window.close()



if "t1" in locals():
    t2 = time.perf_counter()
    time_elapsed = t2-t1
    print(round(time_elapsed, 2))