# -*- coding: utf-8 -*-
"""
XML reader

Input:
Reads an XML file, which has been exported from the standard .xlsx
Document. To see this document go to....

Function:
Sorts the data from the XML file into classes. 5 classes are used; Parent
Action, Child, Disassemblies and PACUnit. To see more about the classes go to PAC_classes.py
All the data from the XML file is kept in the instances of the classes.
Further, it sorts the PAC units in a tree structure, which is saved within the PACUnit instances.
Works with any input order of the PAC information, however correct notation of PAC IDs is needed.

Output:
The output is a list of all instances of Parent, Action, Child, Disassembly and PACUnit classes.
All given information from the .xlsx file is saved within these classes
And a tree structure is added to PACUnit instances.
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
    if len(matching_list) == 1:
        return matching_list[0]
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

highestPACID = 0 #Variable to find amount of PACUnits needed

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
    #Save highest PAC ID
    if PACID > highestPACID:
        highestPACID = PACID

    # Sorts the different IDs for Parents, actions, children and disassemblies, and creates instances
    # The information put into the instances is based on the information given in the excel. There is a standard
    # format for each class
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
    elif IDAsLetters[0] == 'C' or IDAsLetters[0] == 'c': # A child
        instance = Child(cells[row][0], cells[row][1], cells[row][2], cells[row][3])
        AllChildren.append(instance)
        if len(cells[row]) == 9:
            disassemblyInstance(cells[row][4], cells[row][5], cells[row][6],\
                                cells[row][7], cells[row][8], cells[row][0])



#Creates empty PACUnits according to maximum amount of PAC units
AllPACUnits = [PACUnit(i) for i in range(1,highestPACID+1)]

# This loop iterates over the cells again to assign the tree structure as well as Parents, Action and Children
# to each PACUnit
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

    #Find PAC ID by finding numbers before P/A/C/c, and converting this into int
    UnitID = re.search(r"[\d]+(?=[PACc])", cells[row][0])
    UnitID = int(UnitID.group(0))

    #If it's not a root node and it's a parent
    if parent_index != current_unit_index and cells[row][0][current_unit_index] == 'P':
        # Find the parent ID
        ParentID = cells[row][0][cells[row][0].index('-')+1:parent_index]
        ParentID = int(ParentID)
        AllPACUnits[ParentID-1].addTreeChildren(AllPACUnits[UnitID-1])  #Add the unit as a child to its parent
    #Find objekter med current PACID og sæt dem ind i PAC Uniten
    AllPACUnits[UnitID-1].Parent = ObjFromAttrib('PACID', UnitID, AllParents) #UnitID i den her funktion er det samme som PACID attrib i PACUnit
    AllPACUnits[UnitID-1].Action = ObjFromAttrib('PACID', UnitID, AllActions)
    AllPACUnits[UnitID-1].Children = ObjFromAttrib('PACID', UnitID, AllChildren)

"""
    Extra commands (ignore!)
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
    
    Serach function call:
    DesiredPAC = AllPACUnits[0].DFSNonRecursive('Parent', 'ID', '5P1-4C4')
"""

DesiredPAC = AllPACUnits[0].DFSNonRecursive('Parent', 'ID', '5P1-4C4')
# Create a dictionary with the lists in:
objects = {"Parents": AllParents, "Actions": AllActions, "Children": AllChildren, "Disassemblies": AllDisassemblies, "PACUnits": AllPACUnits}
# Deserializes the objects (find et link?)
with open('objects.pickle', 'wb') as f:
    pickle.dump(objects, f)
    
        
