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

from PAC_Classes import Parent, Action, Child, Disassembly # Import PAC Classes

def disassemblyInstance(ID, DFEffect, DAType, DATool, DType, DFID): # A Disassembly instance
    instance = Disassembly(ID, DFEffect, DAType, DATool, DType, DFID)
    Disassemblies.append(instance)
    print('fandt en disassembly action!')



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
Parents = []
Actions = []
Children = []
Disassemblies = []
   
# Sort the data and insert instances with the data
for row in range(len(cells)):
    # Sorts the different IDs for Parents, actions, children and disassemblies
    IDAsList = list(cells[row][0])
    IDAsLetters = " ".join(re.split("[^a-zA-Z]*", cells[row][0])).strip() #Keeps the letters, strip removes spaces
    IDAsNumbers = " ".join(re.split("[^0-9-]*", cells[row][0])).strip() #Keeps the numbers and "-", strip removes spaces
    IDForCurrent = cells[row][0][:cells[row][0].index('-')] #Finds the index of - and returns the strin UP TO "-"
    IDForParent = cells[row][0][cells[row][0].index('-')+1:] #Finds the index of - and returns string FROM "-"
    if IDAsLetters[0] == 'P': # A parent
        instance = Parent(cells[row][0], cells[row][1])
        Parents.append(instance)
        if len(cells[row]) == 7:
            disassemblyInstance(cells[row][2], cells[row][3], cells[row][4],\
                                cells[row][5], cells[row][6], cells[row][0])
        print('fandt en Parent!')
    elif IDAsLetters[0] == 'A': # An action
        instance = Action(cells[row][0], cells[row][1], cells[row][2], cells[row][3],\
        cells[row][4], cells[row][5])
        Actions.append(instance)
        if len(cells[row]) == 11:
            disassemblyInstance(cells[row][6], cells[row][7], cells[row][8],\
                                cells[row][9], cells[row][10], cells[row][0])
        print('fandt en Action!')
    elif IDAsLetters[0] == 'C' or IDAsLetters[1] == 'c': # A child
        instance = Child(cells[row][0], cells[row][1], cells[row][2], cells[row][3])
        Children.append(instance)
        if len(cells[row]) == 9:
            disassemblyInstance(cells[row][4], cells[row][5], cells[row][6],\
                                cells[row][7], cells[row][8], cells[row][0])
        print('fandt en Child/fastener!')


"""
    #find the digits in the string
    digits_list = re.findall(r'\d+', Data[row]) 
    # concatenates the numbers into a single integer if there are numbers    
    if len(digits_list) > 0:
        digits_str = ''.join(digits_list) 
        digits_int = int(digits_str) 
"""
# Overvej om disassembly action overhovedet har det korrekte formål!

# Create a dictionary with the lists in:
objects = {"Parents": Parents, "Actions": Actions, "Children": Children, "Disassemblies": Disassemblies}
# Deserializes the objects (find et link?)
with open('objects.pickle', 'wb') as f:
    pickle.dump(objects, f)
    
        
