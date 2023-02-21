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
import re #Digits in strings
import pickle # object read/write

from PAC_Classes import Parent, Action, Child, Disassembly # Import PAC Classes



# XML data handling
# Load the XML file
tree = ET.parse('Disassembly-PAC-sheet.xml')

# Get the root element
root = tree.getroot()

# Get all cell data in the XML document
Data = root.findall('.//{urn:schemas-microsoft-com:office:spreadsheet}Data');

# Delete the introduction lines
del Data[0:68];

# Only keep the data values in the relevant cells
for i in range(len(Data)):
   Data[i] = Data[i].text

# Creating empty lists for P/A/C instances:   
Parents = []
Actions = []
Children = []
Disassemblies = []
   
# Sort the data and insert instances with the data
for row in range(len(Data)):
    #Get a list of every single character in the current Data[row]
    cell_data = list(Data[row]);
    #find the digits in the string
    digits_list = re.findall(r'\d+', Data[row]) 
    # concatenates the numbers into a single integer if there are numbers    
    if len(digits_list) > 0:
        digits_str = ''.join(digits_list) 
        digits_int = int(digits_str) 
    # Sorts the different IDs for Parents, actions, children and disassemblies    
    if len(cell_data)>3:
        if cell_data[1] == 'P' and cell_data[3] == '-': # A parent
            instance = Parent(Data[row], Data[row+1])
            Parents.append(instance)
            print('fandt en Parent!')
        elif cell_data[1] == 'A' and cell_data[3] == '-': # An action
            instance = Action(Data[row], Data[row+1], Data[row+2],\
            Data[row+3], Data[row+4], Data[row+5])
            Actions.append(instance)
            print('fandt en Action!')
        elif cell_data[1] == 'C' or cell_data[1] == 'c' and\
            cell_data[3] == '-': # A child
            instance = Child(Data[row], Data[row+1], Data[row+2], Data[row+3])
            Children.append(instance)
            print('fandt en Child/fastener!')
    elif len(cell_data) <= 3 and isinstance(cell_data[0], str) and\
        digits_int <= 2 and not list(Data[row-1])[3] == '-' and not\
        cell_data[1] == 'F': # A Disassembly
        instance = Disassembly(Data[row], Data[row+1], Data[row+2], Data[row+3], Data[row+4])
        Disassemblies.append(instance)
        print('fandt en disassembly action!')

       
# Overvej om disassembly action overhovedet har det korrekte formål!
# Deserializes the objects (find et link?)
# Create a dictionary with the lists in:
objects = {"Parents": Parents, "Actions": Actions, "Children": Children, "Disassemblies": Disassemblies}
with open('objects.pickle', 'wb') as f:
    pickle.dump(objects, f)
    
        
