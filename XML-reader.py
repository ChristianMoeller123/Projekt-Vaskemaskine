# -*- coding: utf-8 -*-
"""
XML reader

Reads a XML file, which has been exported from the standard .xlsx
Document. To see this document go to....
Sorts the data from the XML file into classes. 3 classes are used; Parent
Action and Child. All the data from the XML file is kept in the instances.
"""
# Importing libraries
import xml.etree.ElementTree as ET #XML
import re # Library for handling strings
import pickle # object read/write

from PAC_Classes import Parent, Action, Child, Disassembly, PACUnit # Import PAC Classes

def disassemblyInstance(ID, DFEffect, DAType, DATool, DType, DFID): # A Disassembly instance
    instance = Disassembly(ID, DFEffect, DAType, DATool, DType, DFID)
    AllDisassemblies.append(instance)

def ObjFromAttrib(attribute, value, obj_list): #finds all objects with a macthing value in the obj list given
    matching_list = []
    for obj in obj_list:
        if getattr(obj, attribute) == value:
            matching_list.append(obj)
    return matching_list


# XML data handling
# Load the XML file
tree = ET.parse('Disassembly-PAC-sheet.xml')

# Get the root element
root = tree.getroot()

# Get all rows in the XML document
rows = root.findall('.//{urn:schemas-microsoft-com:office:spreadsheet}Row');
cells = [[] for i in range(len(rows))]
#Empty list for cell data in excel sheet:
for i in range(len(rows)): #iterate over all rows
    for child in rows[i].findall('.//{urn:schemas-microsoft-com:office:spreadsheet}Data'): # Get cell data from the row
        cells[i].append(child.text) #Put all row data in a row in the list

# Only keep the data values in the relevant cells, the rest is put in desc list
desc = cells[0:5]
del cells[0:5]

# Creating empty lists for P/A/C instances:   
AllParents = []
AllActions = []
AllChildren = []
AllDisassemblies = []

highestPACID = 0
# Sort the data and insert in instances with the data
for row in range(len(cells)):

    #Get the letters in the ID
    IDAsLetters = " ".join(re.split("[^a-zA-Z]*", cells[row][0])).strip() #Keeps the letters, strip removes spaces

    #Find the index for the first letter (P/A/C)
    lowest_index = len(cells[row][0])
    for char in "PACc":
        index = cells[row][0].find(char)
        if index != -1 and index < lowest_index: #Bliver -1 hvis bogstavet ikke findes i stringen
            lowest_index = index
    #Find PAC ID
    PACID = cells[row][0][:lowest_index]
    PACID = int(PACID)
    #Gem højeste
    if PACID > highestPACID:
        highestPACID = PACID

    # Sorts the different IDs for Parents, actions, children and disassemblies
    if IDAsLetters[0] == 'P': # A parent
        instance = Parent(cells[row][0], cells[row][1])
        AllParents.append(instance)
        if len(cells[row]) == 7:
            disassemblyInstance(cells[row][2], cells[row][3], cells[row][4],\
                                cells[row][5], cells[row][6], cells[row][0])
    elif IDAsLetters[0] == 'A': # An action
        instance = Action(cells[row][0], cells[row][1], cells[row][2], cells[row][3],\
        cells[row][4], cells[row][5])
        AllActions.append(instance)
        if len(cells[row]) == 11:
            disassemblyInstance(cells[row][6], cells[row][7], cells[row][8],\
                                cells[row][9], cells[row][10], cells[row][0])
    elif IDAsLetters[0] == 'C' or IDAsLetters[1] == 'c': # A child
        instance = Child(cells[row][0], cells[row][1], cells[row][2], cells[row][3])
        AllChildren.append(instance)
        if len(cells[row]) == 9:
            disassemblyInstance(cells[row][4], cells[row][5], cells[row][6],\
                                cells[row][7], cells[row][8], cells[row][0])


#Kan håndtere PAC input i enhver rækkefølge!

#Lav tom liste afhængig af højeste ID.
AllPACUnits = [PACUnit(i) for i in range(1,highestPACID+1)]

for row in range(len(cells)):
    #Find unit ID for current unit and for its parent
    current_unit_index = len(cells[row][0])
    parent_index = 0
    for char in "PACc":
        index = cells[row][0].find(char)
        if index != -1 and index < current_unit_index: #Bliver -1 hvis bogstavet ikke findes i stringen
            current_unit_index = index
        if index != -1 and index > parent_index:
            parent_index = index
    #Find PAC ID
    UnitID = cells[row][0][:lowest_index-1]
    UnitID = int(UnitID)
    if parent_index != current_unit_index: #If it's not a root node
        Parent_ID = cells[row][0][cells[row][0].index('-')+1:parent_index]
        Parent_ID = int(Parent_ID)
        AllPACUnits[Parent_ID-1].addTreeChildren(AllPACUnits[PACID-1])  # PACUNIT nummer parent
    #Find objekter med current PACID og sæt dem ind i PAC Uniten
    AllPACUnits[PACID-1].Parent = ObjFromAttrib('PACID', UnitID, AllParents) #UnitID i den her funktion er det samme som PACID attrib i PACUnit
    AllPACUnits[PACID-1].Action = ObjFromAttrib('PACID', UnitID, AllActions)
    AllPACUnits[PACID-1].Children = ObjFromAttrib('PACID', UnitID, AllChildren)
# Find PACID og CHILDID, placer PACs
# Opret children på bagkant. Kan gøres fordi! Child er aldrig højere end PAC ID.

#Unit nummeringen SKAL ikke være DFS!!!!, det er det defineret som her. Er det?
#Find ud af at tildele P/A/Cs
"""
    #find the digits in the string
    digits_list = re.findall(r'\d+', Data[row]) 
    # concatenates the numbers into a single integer if there are numbers    
    if len(digits_list) > 0:
        digits_str = ''.join(digits_list) 
        digits_int = int(digits_str) 
        
    IDAsList = list(cells[row][0])    
    IDAsNumbers = " ".join(re.split("[^0-9-]*", cells[row][0])).strip() #Keeps the numbers and "-", strip removes spaces
    IDForCurrent = cells[row][0][:cells[row][0].index('-')] #Finds the index of - and returns the strin UP TO "-"
    IDForParent = cells[row][0][cells[row][0].index('-')+1:] #Finds the index of - and returns string FROM "-"
"""
# Overvej om disassembly action overhovedet har det korrekte formål!


# Create a dictionary with the lists in:
objects = {"Parents": AllParents, "Actions": AllActions, "Children": AllChildren, "Disassemblies": AllDisassemblies, "PACUnits": AllPACUnits}
# Deserializes the objects (find et link?)
with open('objects.pickle', 'wb') as f:
    pickle.dump(objects, f)
    
        
