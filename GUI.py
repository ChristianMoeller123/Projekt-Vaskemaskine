import PySimpleGUI as sg  # pip install pysimplegui
from pathlib import Path  # core python module
import time
import numpy as np



setup_type = ["Rectangular setup","Circular setup","Table setup"]
BOM_array = []
headings = ['Part name', 'Quantity']
disassembly_action_type = ["Destructive", "Semi-Destructive", "Non destructive"]
tool_type = ["Hand", "Drill", "Hammer", "Screwdriver"]
action_type = ["Separate", "Remove", "Unscrew", "Disconnect"]


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



MOST_layout = [[sg.T("Disassembly setup:"), sg.Combo(setup_type, key="Disassembly setup"),sg.B("Display")],
               [sg.Column([[sg.Image('',key="Disassembly image")]], justification='center')]
               ]


BOM_layout = [[sg.T("Input BOM from file:"), sg.I(key="BOM names file", s=35), sg.FileBrowse(file_types=())],
              [sg.T("Input BOM names and quantity:"), sg.I(key="BOM names", s=20), sg.I(key="BOM quantity", s=6), sg.B("Add")],
              [sg.Table(values=BOM_array, headings=headings, display_row_numbers=True, num_rows=10, key='-TABLE-', enable_events=True, enable_click_events=True, expand_x=True, justification="center", expand_y=False, auto_size_columns=True)]
]


#ændrer navnene på alle de her, de kan ikke have samme navne som den første tab
PAC_layout = [
              [sg.Column([[sg.T("Input PAC from file:"), sg.I(key="BOM names file", s=35), sg.FileBrowse(file_types=())]], justification="center")],
              [sg.HSeparator()],
              [sg.Column([[sg.T("PAC Unit: 1", key="PAC Unit")]], justification="center")],
              [sg.HSeparator()],
              [sg.Column([[sg.T("Parent")]], justification="center")],
              [sg.Column([[sg.T("Parent name:"), sg.I(key="Parent name", s=25), sg.T("Parent PAC ID:")]], justification="center")],
              [sg.Column([[sg.T("Disassembly failure parent")]], justification="center")],
              [sg.Column([[sg.T("Failure description:"), sg.I(key="Parent failure description", s=25), sg.T("Disassembly type:"), sg.Combo(disassembly_action_type, key="Parent disassembly type"), sg.T("Tool:"), sg.Combo(tool_type, key="Parent tool type"), sg.T("DF ID:", key="Parent DF ID")]], justification="center")],
              [sg.HSeparator()],
              [sg.Column([[sg.T("Action")]], justification="center")],
              [sg.Column([[sg.T("Action name:"), sg.Combo(action_type, key="Action type", s=25), sg.T("Action description:"), sg.I(key="Action description", s=25), sg.T("Action times:"), sg.I(key="Action times number", s=5), sg.T("Tool:"), sg.Combo(tool_type,key="Action tool type"), sg.T("Action PAC ID:")]], justification="center")],
              [sg.HSeparator()],
              [sg.Column([[sg.T("Children")]], justification="center")],
              [sg.Column([[sg.B("Check PAC ID"), sg.B("Next PAC unit")]], justification="right")]
]

tab_group = [
    [sg.TabGroup(
        [[
            sg.Tab('MOST', MOST_layout),
            sg.Tab('BOM', BOM_layout),
            sg.Tab('PAC', PAC_layout)]],

        tab_location='topleft',title_color='White', tab_background_color='Gray', selected_title_color='Black',
        selected_background_color='White', border_width=5),
        sg.B("Start timer"), sg.B("Finish PAC model")
    ]
]



window = sg.Window("Initial GUI", tab_group)

i = -1
j = 0
while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break
    if event == "Next":
        sg.popup_error("Not yet implemented")
    if event == "Finish PAC model":
        sg.popup_error("Not yet implemented")
    if event == "Start timer":
        if "t1" in locals():
            sg.popup_error("The timer has already been started. Close the program to see the final time")
            continue
        else:
            t1 = time.perf_counter()
    if event == "Add":
        if is_valid_name(values["BOM names"], BOM_array, i) & is_valid_quantity(values["BOM quantity"], i):
            j = j+1
            BOM_array.append([values["BOM names"], values["BOM quantity"]])
            window["-TABLE-"].update(values=BOM_array)
            window["BOM names"].update('')
            window["BOM quantity"].update('')
    if "+CLICKED+" in event or 0:
        if None in event[2] or event[2][0] == -1:
            continue
        ch =sg.popup_ok_cancel("Press OK to remove part", "Press Cancel to go back", title="OKCancel")
        if ch == "OK":
            BOM_array.remove([BOM_array[event[2][0]][0], BOM_array[event[2][0]][1]])
            window["-TABLE-"].update(values=BOM_array)
    if "Display" in event:
        if values["Disassembly setup"] == "Rectangular setup":
            window["Disassembly image"].update(filename="Rectangular setup.png", size=(200,200))
        if values["Disassembly setup"] == "Circular setup":
            window["Disassembly image"].update(filename="Circular setup.png")
        if values["Disassembly setup"] == "Table setup":
            window["Disassembly image"].update(filename="Table setup.png")

window.close()



if "t1" in locals():
    t2 = time.perf_counter()
    time_elapsed = t2-t1
    print(round(time_elapsed, 2))
