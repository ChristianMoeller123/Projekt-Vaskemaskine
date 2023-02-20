# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import xml.etree.ElementTree as ET


# Load the XML file
tree = ET.parse('Disassembly-PAC-sheet.xml')

# Get the root element
root = tree.getroot()
Data = root.findall('.//{urn:schemas-microsoft-com:office:spreadsheet}Data');

del Data[0:68];

for cell in Data:
   print(cell.text)



#class unit:
#    def __init__(self, ID, Spec)
#        self.ID = ID
#        self.Spec = Spec
        
