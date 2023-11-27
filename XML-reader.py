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
import math
import pickle  # Read/write objects
import re  # Library for handling strings
import os
# Importing libraries
import xml.etree.ElementTree as ET #XML
import re  # Library for handling strings
import pickle  # object read/write
import os

from PAC_Classes import Parent, Action, Child, Disassembly, PACUnit  # Import PAC Classes


# import openpyxl
# import sys


# m-MOST
def mMOST(filename):
    with open(filename, 'rb') as f:
        x = pickle.load(f)
        AllParents = x['Parents']
        AllChildren = x['Children']
        AllActions = x['Actions']
        AllDisassemblies = x['Disassemblies']
        AllPACUnits = x['PACUnits']
        '''
    with open('testdf3.pickle', 'rb') as f:
        x = pickle.load(f)
        AllParents = x['Parents']
        AllChildren = x['Children']
        AllActions = x['Actions']
        AllDisassemblies = x['Disassemblies']
        AllPACUnits = x['PACUnits']
    '''
    #  Distances
    try:
        Atemp = int(os.environ['A'])
        if Atemp in [1,2]:
            A = 30
        elif Atemp in [3,4]:
            A = 60
        elif Atemp in [5,6,7]:
            A = 100
        elif Atemp in [8,9,10]:
            A = 160
        else:
            print("Consider putting you tables closer to the setup!")
    except:
        A = 30
    Ab = A  # Distance from disassembly to desk 2. INDEX!
    Aa = Ab
    Ac = Ab
    Ad = Ab
    Ai = math.sqrt(Ab^2 + Ad^2)
    Ae = 2*Ai
    Ah = Ai
    Af =  100  #  GET INFORMATION FROM USER!!! From desk1 to storage
    Ag =  100  #  GET INFORMATION FROM USER!!! from strage to cross
    #  Idea: Regression from table --> function between meters and index --> input meters get index
    Wa = 5000 #  Rough asumption about the time it takes to input in excel/input gui




    #  Function to return star.
    def GaFun(ToolInput):
        # Takes care if there are more tools represented
        #  Split each tool in the string
        Tools = re.split(r'&', ToolInput)
        #  Strip for white spaces
        Tools = [Tool.strip() for Tool in Tools]
        #  Remove empty strings from the list
        Tools = list(filter(None, Tools))

        Ga = 0
        for Tool in Tools:
            Tool = Tool.lower()
            # Small tools
            if Tool in ['screwdriver', 'hand', 'hands', 'plectrum', 'wrench', 'hammer', 'cross-head screwdriver', 'socket wrench', 'tri-wing screwdriver', 'flat head screwdriver', 'flathead screwdriver', 'wirecutter']:
                Ga += 10

            # Big tools
            elif Tool in ['electric screwdriver', 'drill', 'electric screwdriver']:
                Ga += 30
            else:
                print('Given tool: '+Tool+' is not in our definitions (GA)')
                return
        return Ga

    def StarFun(ToolInput, ActionNameInput):
        # Takes care if there are more tools represented
        #  Split each tool in the string
        Tools = re.split(r'&'r','r'.', ToolInput)
        #  Strip for white spaces
        Tools = [Tool.strip() for Tool in Tools]
        #  Remove empty strings from the list
        Tools = list(filter(None, Tools))

        #  Same for action name
        ActionNames = re.split(r',|&', ActionNameInput)
        ActionNames = [actionname.strip() for actionname in ActionNames]
        ActionNames = list(filter(None, ActionNames))

        Star = 0
        for Tool in Tools:
            Tool = Tool.lower()
            if Tool in ['screwdriver', 'tri-wing screwdriver', 'flat head screwdriver', 'cross-head screwdriver', 'wirecutter', 'flathead screwdriver']:  # Assume 9 turns with screwdriver
                Star += 160
            elif Tool in ['hand', 'hands', 'plectrum']:  #  Hand depends on action name
                #  Loop over all action names. This could definetly be improved regarding assumptions!
                for ActionName in ActionNames:
                    ActionName = ActionName.lower()
                    if ActionName in ['remove', 'disconnect']:
                        Star += 60  # two hands one turn
                    elif ActionName == 'separate':
                        Star += 160  #  2-hands 3 turns
            elif Tool in ['electric screwdriver', 'angle grinder', 'electric screwdriver', 'drill']:  #  Power tools
                Star += 30  #  Assume screw diam. of 6mm
            elif Tool in ['socket wrench', 'wrench']: # Assume 5 turns with wrench
                Star += 100
            elif Tool == 'hammer':
                Star += 60  #  Assume 3 strikes or 6 taps with hammer
            else:
                print('Given tool: ' + Tool + ' is not in our definitions (Star)')
                return
        return Star



    #  INDEX TO S function. Takes index, gives seconds
    def indexSeqToS(Sequence):
        time = sum(Sequence)*0.036  #TMU*0.036 = 1 second
        time = float(time)
        return round(time, 2)




    # Base MOST for Action tools (and times)
    def DEIAction(action, AllPACUnits):
        tool = action.Tool
        times = action.Times
        ActionName = action.Desc
        #  Variables for MOST
        ActionTime = []
        InformationInput = []
        action.DEISteps = []


        #  Steps 1-2
        Sequence = [Aa, 50, 10, 30, 50, 10]
        action.DEISteps.append(indexSeqToS(Sequence))
        action.ThinkingTime = indexSeqToS(Sequence)
        #  Steps 3-5
        try:
            times = int(times)
            Ga = GaFun(tool)
            Star = StarFun(tool, ActionName)
            # Repeat the sequence the specified number of times
            Sequence = [Ab, Ga, Ab, 10, 30, Star, Ab, 10, 10]
            if times > 1:
                for i in range(1, times):
                    Sequence.extend([10, 30, Star, 10, 10])
        except:
            # Parse the string and generate the corresponding sequence for each action
            steps = times.split('.')
            for i in range(0, len(steps)):
                split_steps = steps[i].split()
                tool_times = int(split_steps[0])
                tool_desc = split_steps[1].lower()
                if tool_desc == "remove":
                    actionname = "hands"
                elif tool_desc == "cut":
                    actionname = "wirecutter"
                elif tool_desc == "unscrew":
                    actionname = "electric screwdriver"
                Star = StarFun(actionname, tool_desc) # i switched actioname and tool_desc here,  so actionname is actually the tool
                Ga = GaFun(actionname)
                times = int(tool_times)
                Sequence = [Ab, Ga, Ab, 10, 30, Star, Ab, 10, 10]
                if times > 1:
                    for i in range(1, times):
                        Sequence.extend([10, 30, Star, 10, 10])
        ActionTime.append(indexSeqToS(Sequence))
        action.DEISteps.append(indexSeqToS(Sequence))
        #  Step 6 More than 1 non-leaf, add somthing
        # Find children, and determine amount of non-leaf children:
        nLeafNodes = 0
        children = AllPACUnits[action.PACID-1].Children if isinstance(AllPACUnits[action.PACID-1].Children, list) else [AllPACUnits[action.PACID-1].Children]
        for j in range(len(children)):
            if children[j].isLeaf:
                nLeafNodes += 1
        Sequence = [Ab, 10, 10, Ac, 10, 10]
        if nLeafNodes > 1:
            Sequence.extend([Ac, 10, 30, Ad, 10, 10, Ae])
        action.DEISteps.append(indexSeqToS(Sequence))
        ActionTime.append(indexSeqToS(Sequence))
        action.ActionTime = round(sum(ActionTime), 2)
        #  Step 7
        #  Remember very rough asumption here about input time!!!
        Sequence = [10, 10, Wa]
        action.DEISteps.append(indexSeqToS(Sequence))
        InformationInput.append(indexSeqToS(Sequence))
        #  Step 8
        Sequence = [0]
        for i in range(0, nLeafNodes):
            Sequence.extend([10, 30, 10, 30, 160, 10, 30, 10, 10, 10, 30, 30, 10, 10])
            #Sequence.extend([10, 10, 10, 30, 10, 10, 10]) old sequence
        action.DEISteps.append(indexSeqToS(Sequence))
        InformationInput.append(indexSeqToS(Sequence))

        #  Steps 9-10
        Sequence = [10, 10, Af, 10, 10, Ag]
        action.DEISteps.append(indexSeqToS(Sequence))
        InformationInput.append(indexSeqToS(Sequence))

        action.InformationInput = round(sum(InformationInput), 2)
        '''
        If conditionen på steps 11-19  giver ikke mening
        #  Step 11-19 if there were more than 1 non leaf....
        #  continue this until only leaf children, but only do this for subassemblies --> WE NEED INPUT
        if nLeafNodes > 1:
            #  Step 11
            Sequence = [Ah, 50]
            action.DEISteps.append(indexSeqToS(Sequence))
    
            #  Steps 12-14
            Sequence = [Ai, Ga, Ai, 10, 30, Star, 10, 10]
            action.DEISteps.append(indexSeqToS(Sequence))
    
            #  Step 15
            Sequence = [Ai, 10, Ae, 10]
            action.DEISteps.append(indexSeqToS(Sequence))
            # SKER IKKE I GORENJE. TAG STILLING TIL HVIS DET SKER SENERE
            # DF For subassembly in this loop is different than prev. DF!
    
            # MANGLER STEPS 16-19!!!
    
    
        #  Start assumption: If DF then it's a big tool and only once
        #  From DF input, call steps 16-19
        '''

        DEItotal = sum(action.DEISteps)
        return round(DEItotal, 2)



    for action in AllActions:
        # FIND DFs IN ACTION
        # Add them to the DEIAction call.
        #  Eller gør alt det inde i DEIAction???
        action.ActionDEI = DEIAction(action, AllPACUnits)
    # TAGER IKKE HØJDE FOR N/A

    # Loop over DFs and make that a different time parameter
    # A final time parameter which is the sum of action and DF time.
    for diss in AllDisassemblies:
        #  DFID definitions are different from XML and initial GUI!
        #  Initial GUI:
        origin = diss.DType.split("-")[0]

        #  XML:
        #origin = diss.DFID

        #  Only DFs on actions will have a DEI calculation:
        for char in origin:
            if char == 'A':
                index = origin.find('A')
                PACID = origin[:index]
                PACID = int(PACID)
                # DEI for DF in main disassembly (vaskemaskinen). Assume 1 action time, heavy tool
                Sequence = [Ab, 30, Ab, 10, 30, 30, Ab, 10, 10]
                #  Assume screw diam. of 6mm, and big electric tool for the star value.
                #  Assume big power tool for Ga.

                #  Assign the DEI to the action
                AllPACUnits[PACID-1].Action.DFDEI = indexSeqToS(Sequence)



    #  Print MOST calculations to an excel sheet
    '''
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    
    worksheet.append(["Action ID", "Steps 1-2", "Steps 3-5", "Step 6", "Step 7", "Step 8", "Steps 9-10", "Step 11", "Steps 12-14", "Step 15", "Steps 16-19", "DF"])
    
    
    
    for i in range(len(AllActions)):
        worksheet.cell(row=i + 2, column=1, value=AllActions[i].ID)
        for j in range(len(AllActions[i].DEISteps)):
            worksheet.cell(row=i+2, column=j+2, value=AllActions[i].DEISteps[j])
            if AllActions[i].DFDEI:
                worksheet.cell(row=i + 2, column=12, value=AllActions[i].DFDEI)
    workbook.save("GORENJE3_MOST_DATA.xlsx")
    
    '''

    objects = {"Parents": AllParents, "Actions": AllActions, "Children": AllChildren, "Disassemblies": AllDisassemblies, "PACUnits": AllPACUnits}
    # Deserializes the objects (find et link?)
    with open(filename, 'wb') as f:
        pickle.dump(objects, f)
    return

def ObjFromAttrib(attribute, value, obj_list):  #  finds all objects with a macthing value in the obj list given
    matching_list = []
    for obj in obj_list:
        if getattr(obj, attribute) == value:
            matching_list.append(obj)
    if len(matching_list) == 1:
        return matching_list[0]
    return matching_list


# XML data handling
# Load the XML files
files = [1, 2, 3, 4] #1,2,3 = gorenje 1,2,3. 4 = bosch
filenames = ['Disassembly-PAC-sheet-gorenje-1.xml','Disassembly PAC sheet gorenje 2 model W47443.xml','Disassembly PAC sheet gorenje 3 model W48543.xml','Disassembly-PAC-sheet-bosch.xml']
for file in files:
    #tree = ET.parse('Disassembly-PAC-sheet-bosch.xml')
    #tree = ET.parse('Disassembly-PAC-sheet-gorenje-1.xml')
    #tree = ET.parse('Disassembly PAC sheet gorenje 2 model W47443.xml')
    #tree = ET.parse('Disassembly PAC sheet gorenje 3 model W48543.xml')
    #tree = ET.parse('Disassembly-PAC-sheet.xml')
    #tree = ET.parse('Disassembly-PAC-sheet-kettle.xml')
    # Get the root element
    tree = ET.parse(filenames[file-1])
    root = tree.getroot()

    # Get all rows in the XML document
    rows = root.findall('.//{urn:schemas-microsoft-com:office:spreadsheet}Row');
    cells = [[] for i in range(len(rows))]
    #Empty list for cell data in excel sheet:
    for i in range(len(rows)): #iterate over all rows
        for child in rows[i].findall('.//{urn:schemas-microsoft-com:office:spreadsheet}Data'): # Get cell data from the row
            cells[i].append(child.text) #Put all row data in a row in the list

    # Only keep the data values in the relevant cells, the rest is put in desc list

    '''
    desc = cells[0:5] #for Kettle
    del cells[0:5]
    
    '''

    desc = cells[0:4] #for bosch and gorenje?
    del cells[0:4]


    # Creating empty lists for P/A/C instances:
    AllParents = []
    AllActions = []
    AllChildren = []
    AllDisassemblies = []

    highestPACID = 0 #Variable to find amount of PACUnits needed

    # Sort the data and insert in instances with the data
    i = 1 #for images
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
            instance = Parent(cells[row][0])
            if cells[row][1]:
                instance.Desc = cells[row][1]
            AllParents.append(instance)

            if len(cells[row]) == 7:
                DisInstance = Disassembly(cells[row][2])
                DisInstance.DFEffect = cells[row][3]
                DisInstance.DAType = cells[row][4]
                DisInstance.DATool = cells[row][5]
                DisInstance.DType = cells[row][6]
                DisInstance.DFID = cells[row][0]
                DisInstance.LongDFID = False
                AllDisassemblies.append(DisInstance)

        elif IDAsLetters[0] == 'A': # An action
            instance = Action(cells[row][0])
            instance.ActionID = cells[row][1]
            instance.Desc = cells[row][2]
            instance.DescDetail = cells[row][3]
            instance.Times = cells[row][4]
            instance.Tool = cells[row][5]

            AllActions.append(instance)
            if len(cells[row]) == 11:
                DisInstance = Disassembly(cells[row][6])
                DisInstance.DFEffect = cells[row][7]
                DisInstance.DAType = cells[row][8]
                DisInstance.DATool = cells[row][9]
                DisInstance.DType = cells[row][10]
                DisInstance.DFID = cells[row][0]
                DisInstance.LongDFID = False

                AllDisassemblies.append(DisInstance)
        elif IDAsLetters[0] == 'C' or IDAsLetters[0] == 'c': # A child
            instance = Child(cells[row][0])
            instance.Desc = cells[row][1]
            instance.Number = cells[row][2]
            instance.EoL = cells[row][3]
            instance.update_EoLval()
            AllChildren.append(instance)
            if len(cells[row]) == 9:
                DisInstance = Disassembly(cells[row][4])
                DisInstance.DFEffect = cells[row][5]
                DisInstance.DAType = cells[row][6]
                DisInstance.DATool = cells[row][7]
                DisInstance.DType = cells[row][8]
                DisInstance.DFID = cells[row][0]
                DisInstance.LongDFID = False
                AllDisassemblies.append(DisInstance)



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
        AllPACUnits[UnitID-1].Children = ObjFromAttrib('PACID', UnitID, AllChildren)# test
        #AllPACUnits[UnitID - 1].Children.append(ObjFromAttrib('PACID', UnitID, AllChildren))

    '''
    #  Insert images for demonstration
    #  2c1-1C1
    child = AllPACUnits[0].DFSNonRecursive('Children', 'ID', '2c1-1C1')
    #child[0].M_res = 10  #  Dummy CI values
    #child[0].M_collEoL = 0.5
    child[0].imgFile = 'Cross-Head-Screw.png'
    #  3C2-2C3
    child = AllPACUnits[0].DFSNonRecursive('Children', 'ID', '3C2-2C3')
    #child[0].M_res = 2  #  Dummy CI values
    #child[0].M_collEoL = 15
    child[0].imgFile = 'Kettlebody no metal ring.png'
    '''

    # Define leaf nodes (might be a bit useless here)
    for unit in AllPACUnits:
        if isinstance(unit.Children, list):  # If there are more than 1 child in the PAC unit
            for child in unit.Children:
                for root in unit.TreeChildren:
                    if child.ID[:child.ID.index('-')] == root.Parent.ID[root.Parent.ID.index('-') + 1:]:
                        child.isLeaf = False
        else:  # If there is only 1 child in the PAC unit
            for root in unit.TreeChildren:
                if unit.Children.ID[:unit.Children.ID.index('-')] == root.Parent.ID[root.Parent.ID.index('-')+1:]:
                    unit.Children.isLeaf = False

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

    #DesiredPAC = AllPACUnits[0].DFSNonRecursive('Parent', 'ID', '5P1-4C4')
    # Create a dictionary with the lists in:

    # Reduce CI from DFs on children:
    for diss in AllDisassemblies:
        #  Initial GUI:
        origin = diss.DType.split("-")[0]
        DFtype = diss.DAType #destructive/semi-destructive/non-destructive
        #  XML:
        #origin = diss.DFID
        for char in origin:
            if char == 'C': #add 'c' case, could handle CI differently
                index = origin.find('C')
                PACID = origin[:index]
                PACID = int(PACID)
                Child_num = origin[index+1:]
                Child_num = int(Child_num)
                if DFtype.lower() == 'destructive':
                    AllPACUnits[PACID-1].Children[Child_num-1].DFCI = 0
                elif DFtype.lower() == 'semi-destructive':
                    AllPACUnits[PACID - 1].Children[Child_num - 1].DFCI = float(AllPACUnits[PACID-1].Children[Child_num-1].EoLval)*0.5
                #Non destructive = *1

    objects = {"Parents": AllParents, "Actions": AllActions, "Children": AllChildren, "Disassemblies": AllDisassemblies, "PACUnits": AllPACUnits}
    # Deserializes the objects (find et link?)
    with open(f'WM{file}.pickle', 'wb') as f:
        pickle.dump(objects, f)
    mMOST(f'WM{file}.pickle')

#Run GUI Final
#os.system('python GUI_Final.py')



