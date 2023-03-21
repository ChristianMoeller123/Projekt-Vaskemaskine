import PySimpleGUI as sg  # pip install pysimplegui
from pathlib import Path  # core python module
import time
import numpy as np


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
headings = ['Part name', 'Quantity']
disassembly_action_type = ["Destructive", "Semi-Destructive", "Non destructive"]
tool_type = ["Hand", "Drill", "Hammer", "Screwdriver"]
action_type = ["Separate", "Remove", "Unscrew", "Disconnect"]
EoL = ["Recyclable", "Non Recyclable"]
yes_no = ["Yes", "No"]

i = -1
j = 0

check_PAC_ID = []
PAC_unit = 1

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



#This function creates the row of the parent disassembly failure, it does so by the program calling a defined row when starting
# and then being able to add similar rows to that.
def create_parent_DF(row_counter, row_number_view):
    if row_counter == 0:
        row = [sg.pin(
            sg.Column(
                [[
                    sg.Button("X", key=('-DEL_PARENT_DF-', row_counter)),
                    sg.T("Failure description:"), sg.I(key=f"-PARENT_FAILURE_DESCRIPTION_{row_counter}-", s=25),
                    sg.T("Disassembly type:"),
                    sg.Combo(disassembly_action_type, key=f"-PARENT_DISASSEMBLY_TYPE_{row_counter}-"), sg.T("Tool:"),
                    sg.Combo(tool_type, key=f"-PARENT_TOOL_TYPE_{row_counter}-"),
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
              sg.Combo(disassembly_action_type, key=f"-PARENT_DISASSEMBlY_TYPE_{row_counter}-"), sg.T("Tool:"),
              sg.Combo(tool_type, key=f"-PARENT_TOOL_TYPE_{row_counter}-"), sg.T(f"DF ID: {row_number_view}", key=f"-PARENT_DF_ID_{row_counter}-")]],
            justification="center", key=('-ROW_PARENT_DF-', row_counter)
        ))]
        return row


#Comboen for action_ID_for_DF virker, men skal opdateres løbende under tilføjning af ny action
def create_action_DF(row_counter, row_number_view):
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
              sg.Combo(tool_type, key=f"-ACTION_TOOL_TYPE_{row_counter}-"), sg.T(f"DF ID: {row_number_view}", key=f"-ACTION_DF_ID_{row_counter}-")]],
            justification="center", key=('-ROW_ACTION_DF-', row_counter)
        ))]
        return row

def create_child_DF(row_counter, row_number_view):
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
              sg.Combo(tool_type, key=f"-CHILD_TOOL_TYPE_{row_counter}-"), sg.T(f"DF ID: {row_number_view}", key=f"-CHILD_DF_ID_{row_counter}-")]],
            justification="center", key=('-ROW_CHILD_DF-', row_counter)
        ))]
        return row

def create_action(row_counter, row_number_view):
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
              sg.T("Action name:"), sg.Combo(action_type, key=f"-ACTION_TYPE_{row_counter}-", s=25), sg.T("Action description:"),
              sg.I(key=f"-ACTION_DESCRIPTION_{row_counter}-", s=25), sg.T("Action times:"), sg.I(key=f"-ACTION_TIMES_NUMBER_{row_counter}-", s=5),
              sg.T("Tool:"), sg.Combo(tool_type, key=f"-ACTION_TOOL_TYPE_{row_counter}-"), sg.T(f"Action PAC ID: {row_number_view}", key=f"-ACTION_PAC_ID_{row_counter}-")]],
            justification="center", key=('-ROW_ACTION-', row_counter)
        ))]
        return row

def create_child(row_counter, row_number_view):
    if row_counter == 0:
        row = [sg.pin(
            sg.Column(
                [[
                    sg.Button("X", key=('-DEL_CHILD-', row_counter)),
                    sg.T("Child name:"), sg.I(key=f"-CHILD_NAME_{row_counter}-", s=25), sg.T("Quantity:"),
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
                sg.T("Child name:"), sg.I(key=f"-CHILD_NAME_{row_counter}-", s=25), sg.T("Quantity:"),
                sg.I(key=f"-CHILD_QUANTITY_{row_counter}-", s=5),
                sg.T("EoL:"), sg.Combo(EoL, key=f"-EoL_{row_counter}-"), sg.T("Fastener:"), sg.Combo(yes_no, key=f"-FASTENER_{row_counter}-", readonly=True), sg.T(f"Child PAC ID: {row_number_view}", key=f"-CHILD_PAC_ID_{row_counter}-")]],
            justification="center", key=('-ROW_CHILD-', row_counter)
        ))]
        return row

def is_valid_path(filepath):
    if filepath and Path(filepath).exists():
        return True
    sg.popup_error("Filepath not correct")
    return False

def is_valid_name(name,BOM_array,i):
    i = i+1
    if len(name) == i:
        i = i-1
        sg.popup_error("Name not filled in correct")
        return False
    flatten_BOM = np.array(BOM_array)
    if name in flatten_BOM:
        sg.popup_error("Name cannot repeat, consider changing quantity of existing part")
        return False
    return True

def is_valid_quantity(quantity,i):
    i = i + 1
    if len(quantity) == i:
        i = i - 1
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


MOST_layout = [[sg.T("Disassembly setup:"), sg.Combo(setup_type, key="Disassembly setup"),sg.B("Display")],
               [sg.Column([[sg.Image('',key="Disassembly image")]], justification='center')]
               ]


BOM_layout = [[sg.T("Input BOM from file:"), sg.I(key="BOM names file", s=35), sg.FileBrowse(file_types=())],
              [sg.T("Input BOM names and quantity:"), sg.I(key="BOM names", s=20), sg.I(key="BOM quantity", s=6), sg.B("Add")],
              [sg.Table(values=BOM_array, headings=headings, display_row_numbers=True, num_rows=10, key='-TABLE-', enable_events=True, enable_click_events=True, expand_x=True, justification="center", expand_y=False)]
]


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
              ],key="-PARENT_SCROLL-", scrollable=True, vertical_scroll_only=True, size=[1200,150])],

              [sg.HSeparator()],
              [sg.Column([
              [sg.Column([[sg.T("Action")]], justification="center")],
              [sg.Column([[sg.T("Action name:"), sg.Combo(action_type, key="-ACTION_TYPE-", s=25), sg.T("Action description:"), sg.I(key="-ACTION_DESCRIPTION-", s=25), sg.T("Action times:"), sg.I(key="-ACTION_TIMES_NUMBER-", s=5), sg.T("Tool:"), sg.Combo(tool_type,key="-ACTION_TOOL_TYPE-"), sg.T("Action PAC ID:", key="-ACTION_PAC_ID-")]], justification="center")],
              [sg.Column([create_action(0,1)],key='-ACTION_PANEL-', justification="center")],
              [sg.Column([[sg.Button('Add Action',key='-ADD_ITEM_ACTION-')]], justification="center")],
              [sg.Column([[sg.T("Disassembly failure action")]], justification="center")],
              [sg.Column([create_action_DF(0,1)],key='-ACTION_DF_PANEL-', justification="center")],
              [sg.Column([[sg.Button('Add DF',key='-ADD_ITEM_ACTION_DF-')]], justification="center")]],key="-ACTION_SCROLL-", scrollable=True, vertical_scroll_only=True, size=[1200,200])],


              [sg.HSeparator()],

              [sg.Column([
              [sg.Column([[sg.T("Children")]], justification="center")],
              [sg.Column([[sg.T("Child name:"), sg.I(key="-CHILD_NAME-", s=25), sg.T("Quantity:"), sg.I(key="-CHILD_QUANTITY-", s=5), sg.T("EoL:"), sg.Combo(EoL, key="-EoL-"), sg.T("Fastener:"), sg.Combo(yes_no, key="-FASTENER-", readonly=True), sg.T("Child PAC ID:", key="-CHILD_PAC_ID-")]], justification="center")],
              [sg.Column([create_child(0,1)],key='-CHILD_PANEL-', justification="center")],
              [sg.Column([[sg.Button('Add Child',key='-ADD_ITEM_CHILD-')]], justification="center")],
              [sg.Column([[sg.T("Disassembly failure child")]], justification="center")],
              [sg.Column([create_child_DF(0,1)],key='-CHILD_DF_PANEL-', justification="center")],
              [sg.Column([[sg.Button('Add DF',key='-ADD_ITEM_CHILD_DF-')]], justification="center")]], key="-CHILD_SCROLL-", scrollable=True, vertical_scroll_only=True, size=[1200,200])],


              [sg.HSeparator()],
              [sg.Column([[sg.B("Check PAC ID",key="-CHECK_PAC_ID-"), sg.pin(sg.B("Delete PAC unit", key="-DELETE_PAC_UNIT-", visible=False)), sg.pin(sg.B("Previous PAC unit", key="-PREVIOUS_PAC_UNIT-", visible=False)) ,sg.B("Next PAC unit", key="-NEXT_PAC_UNIT-")]], justification="right")]

]

tab_group = [
    [sg.TabGroup(
        [[
            sg.Tab('MOST', MOST_layout),
            sg.Tab('BOM', BOM_layout),
            sg.Tab('PAC', PAC_layout)]],

        tab_location='topleft',title_color='White', tab_background_color='Gray', selected_title_color='Black',
        selected_background_color='White', border_width=5, size=[1200,780]),
        sg.B("Start timer"), sg.B("Finish PAC model", key="-FINISH_PAC_MODEL-")
    ]
]




window = sg.Window("Initial GUI", tab_group, resizable=True)

def child_relation_ID_1(ID):
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
    i = children_name_ID[0].index(Name)
    ID = children_name_ID[1][i]
    return ID

def parent_class_1(ID_Input):
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
        print("Object not found")
        print(instance.ID, instance.Desc)
    else:
        matching_list = ObjFromAttrib('ID', ID_Input, AllParents)
        matching_list.Desc = window["-PARENT_NAME-"].get()
        print("Object found")
        print(matching_list.Desc)

def parent_class(ID_Input):
    if not AllParents:
        ID = ""
    else:
        for parent in AllParents:
            ID = getattr(parent, 'ID')
            if ID == ID_Input:
                continue

    if window["-PARENT_NAME_COMBO}-"].get() == '':
        sg.popup_error("Remember to fill in the parent name, then click Check PAC ID again")
        error[PAC_unit - 1] += 1
        return

    if ID != ID_Input:
        instance = Parent(ID_Input)
        if window["-PARENT_NAME_COMBO-"] != "": instance.Desc = window["-PARENT_NAME_COMBO-"].get()
        AllParents.append(instance)
        print("Object not found")
        print(instance.ID, instance.Desc)
    else:
        matching_list = ObjFromAttrib('ID', ID_Input, AllParents)
        matching_list.Desc = window["-PARENT_NAME_COMBO-"].get()
        print("Object found")
        print(matching_list.Desc)

def action_class_1(ID_Input):
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
        print("Object not found")
        print(instance.ID, instance.Desc)
    else:
        matching_list = ObjFromAttrib('ID', ID_Input, AllActions)
        matching_list.Desc = window["-ACTION_TYPE-"].get()
        matching_list.DescDetail = window["-ACTION_DESCRIPTION-"].get()
        matching_list.Times = window["-ACTION_TIMES_NUMBER-"].get()
        matching_list.Tool = window["-ACTION_TOOL_TYPE-"].get()
        print("Object found")
        print(matching_list.Desc)

def action_class(ID_Input, row_counter):
    matching_list = ObjFromAttrib('ID', ID_Input, AllActions)
    matching_list.Desc = matching_list.Desc + " & " + window[f"-ACTION_TYPE_{row_counter}-"].get()
    matching_list.DescDetail = matching_list.DescDetail + " & " + window[f"-ACTION_DESCRIPTION_{row_counter}-"].get()
    matching_list.Times = matching_list.Times + " & " + window["-ACTION_TIMES_NUMBER-"].get()
    matching_list.Tool = matching_list.Tool + " & " + window["-ACTION_TOOL_TYPE-"].get()
    print("Combined Actions")
    print(matching_list.Desc)

def child_class_1(ID_Input):
    if not AllChildren:
        ID = ""
    else:
        for action in AllChildren:
            ID = getattr(action, 'ID')
            if ID == ID_Input:
                continue

    if ID != ID_Input:
        instance = Child(ID_Input)
        if window["-CHILD_NAME-"] != "": instance.Desc = window["-CHILD_NAME-"].get()
        if window["-CHILD_QUANTITY-"] != "": instance.Number = window["-CHILD_QUANTITY-"].get()
        if window["-EoL-"] != "": instance.EoL = window["-EoL-"].get()
        AllChildren.append(instance)
        print("Object not found")
        print(instance.ID, instance.Desc)
    else:
        matching_list = ObjFromAttrib('ID', ID_Input, AllChildren)
        matching_list.Desc = window["-CHILD_NAME-"].get()
        matching_list.Number = window["-CHILD_QUANTITY-"].get()
        matching_list.EoL = window["-EoL-"].get()
        print("Object found")
        print(matching_list.Desc)

def child_class(ID_Input, row_counter):
    if not AllChildren:
        ID = ""
    else:
        for action in AllChildren:
            ID = getattr(action, 'ID')
            if ID == ID_Input:
                continue

    if ID != ID_Input:
        instance = Child(ID_Input)
        if window[f"-CHILD_NAME_{row_counter}-"] != "": instance.Desc = window[f"-CHILD_NAME_{row_counter}-"].get()
        if window[f"-CHILD_QUANTITY_{row_counter}-"] != "": instance.Number = window[f"-CHILD_QUANTITY_{row_counter}-"].get()
        if window[f"-EoL_{row_counter}-"] != "": instance.EoL = window[f"-EoL_{row_counter}-"].get()
        AllChildren.append(instance)
        print("Object not found")
        print(instance.ID, instance.Desc)
    else:
        matching_list = ObjFromAttrib('ID', ID_Input, AllChildren)
        matching_list.Desc = window[f"-CHILD_NAME_{row_counter}-"].get()
        matching_list.Number = window[f"-CHILD_QUANTITY_{row_counter}-"].get()
        matching_list.EoL = window[f"-EoL_{row_counter}-"].get()
        print("Object found")
        print(matching_list.Desc)

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
        if window[f"-PARENT_DISASSEMBlY_TYPE_{row_counter}-"] != "": instance.DAType = window[
            f"-PARENT_DISASSEMBlY_TYPE_{row_counter}-"].get()
        if window[f"-PARENT_TOOL_TYPE_{row_counter}-"] != "": instance.DATool = window[f"-PARENT_TOOL_TYPE_{row_counter}-"].get()

        AllDisassemblies.append(instance)
        print("Object not found")
        print(instance.DFID, instance.DFEffect)
    else:
        matching_list = ObjFromAttrib('DFID', ID_Input, AllDisassemblies)
        matching_list.DFEffect = window[f"-PARENT_FAILURE_DESCRIPTION_{row_counter}-"].get()
        matching_list.DAType = window[f"-PARENT_DISASSEMBlY_TYPE_{row_counter}-"].get()
        matching_list.DATool = window[f"-PARENT_TOOL_TYPE_{row_counter}-"].get()
        print("Object found")
        print(matching_list.DFEffect)

def action_DF_affected_ID(): #Den her virker ikke af en eller anden grund. Drop numpy pga PAC unit problemer
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

def child_DF_affected_ID(): # Den her virker heller ikke Drop numpy pga PAC unit problemer
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


while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break
    if event == "Finish PAC model":
        sg.popup_error("Not yet implemented")
    if event == "Start timer":
        if "t1" in locals():
            sg.popup_error("The timer has already been started. Close the program to see the final time")
            continue
        else:
            t1 = time.perf_counter()

    ##BOM tab
    if event == "Add":
        if is_valid_name(values["BOM names"], BOM_array, i) & is_valid_quantity(values["BOM quantity"], i):
            j = j+1
            BOM_array.append([values["BOM names"], values["BOM quantity"]])
            window["-TABLE-"].update(values=BOM_array)
            window["BOM names"].update('')
            window["BOM quantity"].update('')
    if "+CLICKED+" in event:
        if None in event[2] or -1 == event[2][0]:
            continue
        ch =sg.popup_ok_cancel("Press OK to remove part", "Press Cancel to go back", title="OKCancel", grab_anywhere=True)
        if ch == "OK":
            BOM_array.remove([BOM_array[event[2][0]][0], BOM_array[event[2][0]][1]])
            window["-TABLE-"].update(values=BOM_array)

    #MOST tab
    if "Display" in event:
        if values["Disassembly setup"] == "Rectangular setup":
            window["Disassembly image"].update(filename="Rectangular setup.png", size=(200,200))
        if values["Disassembly setup"] == "Circular setup":
            window["Disassembly image"].update(filename="Circular setup.png")
        if values["Disassembly setup"] == "Table setup":
            window["Disassembly image"].update(filename="Table setup.png")

    #PAC tab
    if event == '-ADD_ITEM_PARENT_DF-':
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
        #Kommer lige an på hvad vi ender med at gøre, men sæt action DF op som child DF så den tjekker at det passer med det rigtige DF til den rigtige action
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
                    window[f"-PARENT_DF_ID_{row_parent_DF[0][rows]}-"].update(f"Parent DF ID: {PAC_unit}D{row_parent_DF[1][rows]}-{PAC_unit}P1-000")
                    parent_DF_class(f"{PAC_unit}D{row_parent_DF[1][rows]}-{PAC_unit}P1-000",rows)
            for rows in row_action_DF[0]:
                if row_action_DF[2][rows] == 1 and row_action_DF[3][rows] == PAC_unit:
                    window[f"-ACTION_DF_ID_{row_action_DF[0][rows]}-"].update(f"Action DF ID: {PAC_unit}D{row_action_DF[1][rows]}-{PAC_unit}A1-000")
            #Det her skal gøres for det child det passer til, det samme skal ske ved action
            for rows in row_child_DF[0]:
                if row_child_DF[2][rows] == 1 and row_child_DF[3][rows] == PAC_unit:
                    child_ID_for_DF = values[f"-CHILD_ID_FOR_DF_{row_child_DF[0][rows]}-"]
                    if child_ID_for_DF == "": #Checks if the DF has been correctly set to a specific child
                        sg.popup_error("Remember to fill out what child is affected by the disassembly")
                        error[PAC_unit - 1] += 1
                        continue
                    window[f"-CHILD_DF_ID_{row_child_DF[0][rows]}-"].update(f"Child DF ID: {PAC_unit}D{row_child_DF[1][rows]}-{PAC_unit}C{child_ID_for_DF}-000")

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
                    window[f"-PARENT_DF_ID_{row_parent_DF[0][rows]}-"].update(f"Parent DF ID: {PAC_unit}D{row_parent_DF[1][rows]-parent_DF_diff[PAC_unit-1]}-{PAC_unit}P1-000")
                    parent_DF_class(f"{PAC_unit}D{row_parent_DF[1][rows]}-{PAC_unit}P1-000", rows)
            for rows in row_action_DF[0]:
                if row_action_DF[2][rows] == 1 and row_action_DF[3][rows] == PAC_unit:
                    window[f"-ACTION_DF_ID_{row_action_DF[0][rows]}-"].update(f"Action DF ID: {PAC_unit}D{row_action_DF[1][rows]-action_DF_diff[PAC_unit-1]}-{PAC_unit}A1-000")
            for rows in row_child_DF[0]:
                if row_child_DF[2][rows] == 1 and row_child_DF[3][rows] == PAC_unit:
                    child_ID_for_DF = values[f"-CHILD_ID_FOR_DF_{row_child_DF[0][rows]}-"]
                    print(child_ID_for_DF)
                    if child_ID_for_DF == "":  # Checks if the DF has been correctly set to a specific child
                        sg.popup_error("Remember to fill out what child is affected by the disassembly")
                        error[PAC_unit - 1] += 1
                        continue
                    window[f"-CHILD_DF_ID_{row_child_DF[0][rows]}-"].update(
                        f"Child DF ID: {PAC_unit}D{row_child_DF[1][rows]-child_DF_diff[PAC_unit-1]}-{PAC_unit}C{child_ID_for_DF}-000")

    if event == "-NEXT_PAC_UNIT-":
        if PAC_unit not in check_PAC_ID:
            sg.popup_error("You have to check the PAC ID before going to the next PAC Unit")
            continue
        PAC_unit += 1
        error.append(0)
        window["-PAC_UNIT-"].update(f"PAC Unit: {PAC_unit}")
        if PAC_unit > 1:
            window["-PREVIOUS_PAC_UNIT-"].update(visible=True)
            window["-DELETE_PAC_UNIT-"].update(visible=True)

        #Making it so that the parent is named after previous children
        window["-PARENT_NAME_COMBO-"].update(values=children_name_ID[0])
        window["-PARENT_NAME-"].update(visible=False)
        window["-PARENT_NAME_COMBO-"].update(visible=True)

        #The part that clear the PAC information
        window["-PARENT_NAME-"].update('')
        window["-ACTION_TYPE-"].update('')
        window["-ACTION_DESCRIPTION-"].update('')
        window["-ACTION_TIMES_NUMBER-"].update('')
        window["-ACTION_TOOL_TYPE-"].update('')
        window["-CHILD_NAME-"].update('')
        window["-CHILD_QUANTITY-"].update('')
        window["-EoL-"].update('')
        window["-FASTENER-"].update('')
        #Husk at fjern visibility ordenligt ved at ændre 3. kolonne i matrixen, samt gem hvilke kolonner der allerede var viste

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

        if PAC_unit == 1:
            matching_list = PAC_search(PAC_unit, AllParents)
            window["-PARENT_NAME-"].update(matching_list.Desc)
            window[f"-PARENT_PAC_ID-"].update(matching_list.ID)
        else:
            matching_list = PAC_search(PAC_unit, AllParents)
            window["-PARENT_NAME_COMBO-"].update(matching_list.Desc)
            window[f"-PARENT_PAC_ID-"].update(matching_list.ID)

        matching_list = PAC_search(PAC_unit, AllActions)




    #Lav en Delete PAC unit knap, så når man kommer til at trykke next ved en fejl og skaber et PAC unit man ikke skal bruge den sletter det
    # så man ikke får fejl når man prøver at bruge finish PAC model. Delete skal også kunne fjerne de givne ID'er som er blevet registreret deri
    # til sidst skal den også også sige at hvis man slettet et PAC unit midtvejs at den ikke kan gøre det fordi der er andre PAC units der afhænger af den og man skal slette dem først
    if event == "-FINISH_PAC_MODEL-":
        print(error)
        for rows in range(0,len(error)):
            if error[rows] > 0:
                sg.popup_error(f"PAC unit {rows} haven't been filled out correctly, return to it and fill it out to finish PAC model")
                continue
        #Dump alle classes til en pickle fil
        continue
window.close()



if "t1" in locals():
    t2 = time.perf_counter()
    time_elapsed = t2-t1
    print(round(time_elapsed, 2))

