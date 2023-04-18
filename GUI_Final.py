# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 08:11:17 2023

@author: chris
"""

import math
import pickle  # Read/write objects
import PySimpleGUI as sg
import re  # Library for handling strings

with open('objects.pickle', 'rb') as f:
    x = pickle.load(f)
    AllParents = x['Parents']
    AllChildren = x['Children']
    AllActions = x['Actions']
    AllDisassemblies = x['Disassemblies']
    AllPACUnits = x['PACUnits']

    # --- Define functions ---

    # Element size of the squares in PAC model
    sizeX = 150
    sizeY = 60
# RUN MOST

colors = ['green', 'teal', 'sky blue', 'lime']

def drawSquare(posx, posy, obj):
    # Draw square function. Input: P/A/C obj, center pos
    # Output: Square element
    # parent = blue, action = gray, children = yellow.
    # 150x x 60y
    # assign the element to the object?
    IDAsLetters = " ".join(re.split("[^a-zA-Z]*", obj.ID)).strip()
    if IDAsLetters[0] == 'P':
        graph.draw_rectangle((posx - sizeX/2, posy + sizeY/2),
                             (posx + sizeX/2, posy - sizeY/2)
                             ,fill_color = colors[0], line_color = colors[0], line_width = 2)
    elif IDAsLetters[0] == 'A':
        graph.draw_rectangle((posx - sizeX/2, posy + sizeY/2),
                             (posx + sizeX/2, posy - sizeY/2)
                             ,fill_color = colors[1], line_color = colors[1], line_width = 2)
    elif IDAsLetters[0] == 'C':
        graph.draw_rectangle((posx - sizeX/2, posy + sizeY/2),
                             (posx + sizeX/2, posy - sizeY/2)
                             ,fill_color = colors[2], line_color = colors[2], line_width = 2)
    elif IDAsLetters[0] ==  'c': #  Fasteners
        graph.draw_rectangle((posx - sizeX/2, posy + sizeY/2),
                             (posx + sizeX/2, posy - sizeY/2)
                             ,fill_color = colors[3], line_color = colors[3], line_width = 2)
    graph.draw_text(obj.ID, (posx, posy))
    obj.pos = (posx, posy)


def drawLine(cposL, cposR):
    # draws a line from one element to another
    # cposL is the position coordinates of L as cposL = (x, y)
    graph.draw_line((cposL[0] + sizeX/2, cposL[1]), (cposR[0] - sizeX/2, cposR[1]))

# Dashed lines
def drawDashedLine(start, end, col):
    # start = (startX, startY)
    # end = (endX, endY)
    # Calculate the distance between the start and end points
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = (dx ** 2 + dy ** 2) ** 0.5

    # Calculate the number of dashes needed to cover the distance
    dash_length = 10  # Length of each dash in pixels
    num_dashes = math.ceil(distance / dash_length / 2)

    # Calculate the coordinates of each dash
    dash_coords = []
    for i in range(num_dashes):
        x1 = start[0] + i * dash_length * 2 * dx / distance
        y1 = start[1] + i * dash_length * 2 * dy / distance
        x2 = start[0] + (i * dash_length * 2 + dash_length) * dx / distance
        y2 = start[1] + (i * dash_length * 2 + dash_length) * dy / distance
        dash_coords.append((x1, y1, x2, y2))

    # Draw the dashes on the graph
    for dash in dash_coords:
        graph.draw_line((dash[0], dash[1]), (dash[2], dash[3]), color = col, width=2)

# Draws "square" lines between PAC units
def drawUnitLine(start, end, n):
    colorlist = ['black', 'orange', 'magenta', 'green', 'brown']
    turn = (int(unitSpace/3) - xSpace) + n*20
    drawDashedLine(start, (start[0] + turn, start[1]), colorlist[n])
    drawDashedLine((start[0] + turn, start[1]), (start[0] + turn, end[1]), colorlist[n])
    drawDashedLine((start[0] + turn, end[1]), end, colorlist[n])
# Color code lines for each layer

#  Function to draw unit elements in the tree graph
def draw_unit(posX, posY, unit):
    graphTree.draw_circle((posX, posY), 10)
    graphTree.draw_text(str(unit.PACID), (posX,posY))

#  Function to draw lines between tree elements
def draw_unitLine(posXu, posYu, posXc, posYc):
    graphTree.draw_line((posXu+10, posYu), (posXc-10, posYc))


#  Draw Disassembly square
def drawDisassemblySquare(posx, posy):
    graph.draw_rectangle((posx - (sizeX / 2 + 2), posy + (sizeY / 2 + 2)),
                         (posx + (sizeX / 2 + 2), posy - (sizeY / 2 + 2))
                         , line_color='red', line_width=2)

# Function to find DEI for a given path:
def pathDEI(ID):
    elem, path = AllPACUnits[0].DFSNonRecursive('Action', 'ID', ID)
    pathDEI = 0
    # Reconstruct the path from the element to the root node. There is only one way from element to root!
    pathReconstruct = []

    # First PAC unit is appended
    for unit in AllPACUnits:
        if unit.Action == elem:
            pathReconstruct.append(unit)
            break
    # Finding the rest of PAC units until at root node
    while pathReconstruct[-1] != AllPACUnits[0]:
        for unit in AllPACUnits:
            if pathReconstruct[-1] in unit.TreeChildren:
                pathReconstruct.append(unit)

    # sum DEIs in path
    for unit in pathReconstruct:
         if unit:
             pathDEI = pathDEI + unit.Action.ActionDEI + unit.Action.DFDEI
    return round(pathDEI, 2)


def ObjFromAttrib(attribute, value, obj_list):  #  finds all objects with a macthing value in the obj list given
    matching_list = []
    for obj in obj_list:
        if getattr(obj, attribute) == value:
            matching_list.append(obj)
    if len(matching_list) == 1:
        return matching_list[0]
    return matching_list

#  CI calculator function
def CI(**kwargs):
    #  Call the function with a key:
    #  RR = CI(M_rec = 194, M_collEoL = 19)
    #  Input variables has to match the needed variables of output (CREATE ERROR FUNCTION!)
    #returnList = []
    inputList = []
    for key in kwargs.items():
        inputList.append(key[0])
    if 'M_rec' in inputList:
        RR = kwargs['M_rec']/kwargs['M_collEoL']
        return round(RR, 2)
        #returnList.append(RR)
    if 'M_res' in inputList:
        RE = kwargs['M_res']/kwargs['M_collEoL']
        return round(RE, 2)
        #returnList.append(RE)
    #  MCI
    # V   = Element Virgin mass
    # W   = Overall amount of unrecoverable waste
    # M_c = Child mass
    # Wf  = Waste generated to produce feedstock
    # Wc  = Waste generated in the recycling process
    # L   = Actual realised lifetime
    # Lav = Product design life based on market average
    if 'V' in inputList:
        LFI = (kwargs['V']+kwargs['W'])/(2*kwargs['M_c']+(kwargs['Wf']-kwargs['Wc'])/2)
        X = kwargs['L']/kwargs['Lav']
        MCI = 1-LFI*(0.9/X)
        #returnList.append(MCI)
        return round(MCI, 2)

    return #  ???

#  --- Find information about components and fasteners ---
totalComponents = 0  #  Total components without fasteners
Fasteners = [[0], [0]] # list of fasteners. Fasteners[0] = names, Fasteners[1] = amount

for unit in AllPACUnits:
    if isinstance(unit.Children, list):
        for children in unit.Children:
            IDAsLetters = " ".join(re.split("[^a-zA-Z]*", children.ID)).strip()
            if IDAsLetters[0] == 'C':
                totalComponents += int(children.Number)
            elif IDAsLetters[0] == 'c':
                #  Check if fastener already exists
                if children.Desc in Fasteners[1]:
                    #  Find the row where it is
                    row = Fasteners[1].index(children.Desc)
                    #  Add to amount
                    Fasteners[0][row] += int(children.Number)
                else: #  If it doesn't exist
                    if not Fasteners[1][0]: #  If it's the first element
                        Fasteners[1][0] = children.Desc
                        Fasteners[0][0] = int(children.Number)
                    else:  #  Otherwise just append
                        Fasteners[1].append(children.Desc)
                        Fasteners[0].append(int(children.Number))
    else:
        IDAsLetters = " ".join(re.split("[^a-zA-Z]*", unit.Children.ID)).strip()
        if IDAsLetters[0] == 'C':
            totalComponents += int(unit.Children.Number)
        elif IDAsLetters[0] == 'c':
            #  Check if fastener already exists
            if unit.Children.Desc in Fasteners[1]:
                #  Find the row where it is
                row = Fasteners[1].index(unit.Children.Desc)
                #  Add to amount
                Fasteners[0][row] += int(unit.Children.Number)
            else:
                if not Fasteners[1][0]:  # If it's the first element
                    Fasteners[1][0] = unit.Children.Desc
                    Fasteners[0][0] = int(unit.Children.Number)
                else:  # Otherwise just append
                    Fasteners[1].append(unit.Children.Desc)
                    Fasteners[0].append(int(unit.Children.Number))
#  Make fasteners array compatible with the table element
FastenersNew = []
if Fasteners[0][1]:
    for i in range(len(Fasteners[1])):
        FastenersNew.append([Fasteners[1][i], Fasteners[0][i]])
    Fasteners = FastenersNew

#   --- Add CI for all leaf children ---
CIRR = []
CIRE = []
CIMCI = []
for unit in AllPACUnits:
    if isinstance(unit.Children, list):
        for children in unit.Children:
            if children.isLeaf:
                if children.M_res:
                    CIRE.append(CI(M_res=children.M_res, M_collEoL=children.M_collEoL))
                if children.M_rec:
                    CIRR.append(CI(M_rec=children.M_rec, M_collEoL=children.M_collEoL))
                if children.V:
                    CIMCI.append(CI(V=children.V, W=children.W, M_c=children.M_c, Wf=children.Wf, Wc=children.Wc, L=children.L, Lav=children.Lav))
    else:
        if unit.Children.isLeaf:
            if unit.Children.M_res:
                CIRE.append(CI(M_res=unit.Children.M_res, M_collEoL=unit.Children.M_collEoL))
            if unit.Children.M_rec:
                CIRR.append(CI(M_res=unit.Children.M_rec, M_collEoL=unit.Children.M_collEoL))
            if unit.Children.V:
                CIMCI.append(CI(V=unit.Children.V, W=unit.Children.W, M_c=unit.Children.M_c, Wf=unit.Children.Wf, Wc=unit.Children.Wc, L=unit.Children.L, Lav=unit.Children.Lav))
#  Find the averages if of CI's if they exist
if CIRE:
    CIRE = sum(CIRE) / len(CIRE)
    CIRE = str(CIRE)
elif not CIRE:
    CIRE = 'N/A'
if CIRR:
    CIRR = sum(CIRR) / len(CIRE)
    CIRR = str(CIRR)
elif not CIRR:
    CIRR = 'N/A'
if CIMCI:
    CIMCI = sum(CIMCI) / len(CIMCI)
    CIMCI = str(CIMCI)
elif not CIMCI:
    CIMCI = 'N/A'


# # --- Define the graph layout ---

# Initial distances between elements
xSpace = 200
ySpace = 90
unitSpace = 3.5*xSpace
maxChildren = 1
# Finds the maximum children in the PAC tree.
for unit in AllPACUnits:
    if isinstance(unit.Children, list):
        if len(unit.Children) > maxChildren:
            maxChildren = len(unit.Children)


# Function to find max height and length
def largestLayer(layer, maxBreadth, maxLength):
    nextLayer = []
    for i in range(len(layer)):  # Draw all PACUnits in same layer
        # Update number of units in next layer
        if len(layer[i].TreeChildren) != 0:
            for k in range(len(layer[i].TreeChildren)):
                nextLayer.append(layer[i].TreeChildren[k])  # Appends one unit at a time to get good list of next layer
    # Update largest layer:
    if len(layer) > maxBreadth:
        maxBreadth = len(layer)

    if nextLayer:  # Recursive call with the next layer, if it exists
        maxLength += 1
        maxBreadth, maxLength = largestLayer(nextLayer, maxBreadth, maxLength)
    elif nextLayer == 0:  # Otherwise stop
        return maxBreadth, maxLength
    return maxBreadth, maxLength

maxBreadth, maxLength = largestLayer([AllPACUnits[0]], 2, 0)
canvY = (maxBreadth+2)*maxChildren*ySpace
canvX = (unitSpace)*(maxLength+1)

canvYT = (maxBreadth+1)*40
canvXT = (maxLength+1)*40
# --- Create the PySimpleGUI windows ---

def make_win1():
    graph_layout = [
        [sg.Graph(
            canvas_size=(canvX, canvY),
            graph_bottom_left=(0, math.floor(-canvY / 2)),
            graph_top_right=(canvX, canvY / 2),
            background_color="white",
            key="-GRAPH-",
            drag_submits=True,
            enable_events=True
        )]
    ]
    graph_tree_layout = [
        [sg.Graph(
            canvas_size=(canvXT, canvYT),
            graph_bottom_left=(0, math.floor(-canvYT / 2)),
            graph_top_right=(canvXT, canvYT / 2),
            background_color="white",
            key="-GRAPH_TREE-",
            drag_submits=True,
            enable_events=True
        )]
    ]
    row_number = 1
    if Fasteners[1][0]:
        row_number = len(Fasteners[1])
    # Define the PySimpleGUI layout
    layout = [
        [sg.Button('Options'), sg.Button('Exit')],
        [sg.T('Total amount of components without fasteners: '+str(totalComponents)), sg.T('RR: '+CIRR+' RE: '+CIRE+' MCI: '+CIMCI)],
        [sg.Column(graph_layout, scrollable=True, size=(1800, 600)), [sg.Column(graph_tree_layout, scrollable=True, size=(400,200)),
         sg.Table(values=Fasteners, headings=['Fastener', 'Amount'],
                   auto_size_columns=True,
                   display_row_numbers=True,
                   justification='center',
                   num_rows=row_number,
                   expand_x=False,
                   expand_y=True,)]]
    ]
    return sg.Window("Graph Window", layout, finalize=True, resizable=True, use_custom_titlebar=True)
def make_winP(obj):
    layout = [[sg.Text('Parent element with ID: '+obj.ID)],
              [sg.Text('Description: ' + obj.Desc)],
              [sg.Frame('DFs', [[sg.T('Information about DFs')]], key='-FRAME-')],
              [sg.Button('Add DF'), sg.Button('Exit')]]
    return sg.Window('Parent '+obj.ID, layout, finalize=True, resizable=True)
def make_winA(obj):
    layout = [[sg.Text('Action element with ID: ' + obj.ID)],
              [sg.Text('ActionID: ' + obj.ActionID)],
              [sg.Text('Description: ' + obj.Desc)],
              [sg.Text('Detailed description: ' + obj.DescDetail)],
              [sg.Text('Number of times repeated: ' + obj.Times)],
              [sg.Text('Tool: ' + obj.Tool)],
              [sg.Text('DEI for Action: ' + str(obj.ActionDEI))],
              [sg.Text('DEI for DF: ' + str(obj.DFDEI))],
              [sg.Text('Path DEI to Action: ' + str(pathDEI(obj.ID)))],
              [sg.Frame('DFs',[[sg.T('Information about DFs')]], key='-FRAME-')],
              [sg.Button('Add DF'), sg.Button('Exit')]]
    return sg.Window('Action '+obj.ID, layout, finalize=True, resizable=True)
def make_winC(obj):
    layout = [[sg.Text('Child element with ID: '+obj.ID)],
              [sg.Text('Description: ' + obj.Desc)],
              [sg.Text('Amount: ' + str(obj.Number))],
              [sg.Text('End of Life: ' + obj.EoL)],
              [sg.Button('Add DF'), sg.Button('Exit'), sg.Button('Add image')],
              [sg.Frame('DFs', [[sg.T('Information about DFs')]], key='-FRAME-')],
              [sg.Text('Graphical display of Child')],
              [sg.Image(obj.imgFile, size=(400, 400))]]
    return sg.Window('Child '+obj.ID, layout, finalize=True, resizable=True)
# start off with main window open only
window1, windowP, windowA, windowC = make_win1(), None, None, None

graph = window1["-GRAPH-"]
graphTree = window1["-GRAPH_TREE-"]

# --- DRAW THE PAC MODEL IN THE GRAPH ----

# Add the tree from the AllPACUnits list to the graph
def drawTree(layer, posX):
    nextLayer = []
    for i in range(len(layer)):  # Draw all PACUnits in same layer
        posY = ((math.floor(len(layer)/2))-i)*maxChildren*ySpace

        # Draw Parent
        drawSquare(posX, posY, layer[i].Parent)

        # Draw Action
        drawSquare(posX + xSpace, posY, layer[i].Action)
        drawLine((posX, posY), (posX + xSpace, posY))  # Line from parent to action

        # Draw Children
        children = layer[i].Children if isinstance(layer[i].Children, list) else [layer[i].Children]
        posYchildList = []
        for j in range(len(children)):
            posYchild = posY + (math.floor(len(children)/2) - j)*ySpace
            # save posYchild
            posYchildList.append(posYchild)
            drawSquare(posX + 2*xSpace, posYchild, children[j])
            drawLine((posX + xSpace, posY), (posX + 2*xSpace, posYchild))  # Line from action to children

        maxposYchild = max(posYchildList)
        minposYchild = min(posYchildList)
        # Draw box around the PAC unit
        # use posYchild max and min
        graph.draw_rectangle((posX - 20 - sizeX/2, maxposYchild + sizeY/2 + 20),
                             (posX + 2*xSpace + sizeX / 2 + 20, minposYchild - sizeY/2 - 20)
                             , line_color='black', line_width=1)
        # Draw the name
        graph.draw_text(layer[i].Name, (posX + xSpace, maxposYchild + sizeY/2 + 30))

        # Update number of units in next layer
        if len(layer[i].TreeChildren) != 0:
            for k in range(len(layer[i].TreeChildren)):
                nextLayer.append(layer[i].TreeChildren[k]) # Appends one unit at a time to get good list of next layer

    posX = posX + unitSpace

    if nextLayer:  # Recursive call with the next layer, if it exists
        drawTree(nextLayer, posX)
    elif nextLayer == 0:  # Otherwise stop
        return
    return
# Starting position:
posX = 100
drawTree([AllPACUnits[0]], posX)  # Draw the tree from the root

'''
#  Draw info squares
posYInfo = (len(AllPACUnits[0].Children)+4)*ySpace
graph.draw_rectangle((posX-sizeX/2, posYInfo + sizeY/2), (posX + sizeX/2, posYInfo - sizeY/2), fill_color = colors[0])
graph.draw_text('Parent', (posX, posYInfo))

graph.draw_rectangle(((posX+xSpace)-sizeX/2, posYInfo + sizeY/2), ((posX+xSpace) + sizeX/2, posYInfo - sizeY/2), fill_color = colors[1])
graph.draw_text('Action', ((posX+xSpace), posYInfo))

graph.draw_rectangle(((posX+2*xSpace)-sizeX/2, posYInfo + sizeY/2), ((posX+2*xSpace) + sizeX/2, posYInfo - sizeY/2), fill_color = colors[2])
graph.draw_text('Component child', ((posX+2*xSpace), posYInfo))

graph.draw_rectangle(((posX+(2*xSpace))-sizeX/2, posYInfo+ySpace + sizeY/2), ((posX+(2*xSpace)) + sizeX/2, posYInfo+ySpace - sizeY/2), fill_color = colors[3])
graph.draw_text('Fastener child', ((posX+(2*xSpace), posYInfo+ySpace)))
'''

# Draw lines between pac units and define leaf nodes in PAC model
# This is done by comparing all children IDs with all Parent IDs, if any matches, a line is drawn between them
# If there only is one child in the PAC unit, then it does not iterate over all children, and if it's a list,
# It iterates over all of them.
for unit in AllPACUnits:
    if isinstance(unit.Children, list):  # If there are more than 1 child in the PAC unit
        for child in unit.Children:
            for root in unit.TreeChildren:
                if child.ID[:child.ID.index('-')] == root.Parent.ID[root.Parent.ID.index('-') + 1:]:
                    drawUnitLine((child.pos[0] + sizeX/2, child.pos[1]), (root.Parent.pos[0] - sizeX/2, root.Parent.pos[1]), unit.RootsDrawn)
                    unit.RootsDrawn = unit.RootsDrawn + 1
                    # print('from '+str(child.PACID) +' to ' +str(root.Parent.PACID))
                    #  Define child as not a leaf node
                    child.isLeaf = False
    else:  # If there is only 1 child in the PAC unit
        for root in unit.TreeChildren:
            if unit.Children.ID[:unit.Children.ID.index('-')] == root.Parent.ID[root.Parent.ID.index('-')+1:]:
                # draw a line from the right side of child element to the left side of parent element
                drawUnitLine((unit.Children.pos[0] + sizeX/2, unit.Children.pos[1]), (root.Parent.pos[0] - sizeX/2, root.Parent.pos[1]), unit.RootsDrawn)
                unit.RootsDrawn = unit.RootsDrawn + 1
                # print('from ' + str(unit.Children.PACID) + ' to ' + str(root.Parent.PACID))
                #  Define child as not a leaf node
                unit.Children.isLeaf = False

#  --- DRAW THE GRAPH TREE ---
ySpaceTree = 40
xSpaceTree = 40
def drawGraphTree(layer, posX):
    nextLayer = []
    for i in range(len(layer)):  # Draw all PACUnits in same layer
        posY = ((math.floor(len(layer)/2))-i)*ySpaceTree

        # Draw Parent
        draw_unit(posX, posY, layer[i])
        layer[i].pos = (posX, posY)


        # Update number of units in next layer
        if len(layer[i].TreeChildren) != 0:
            for k in range(len(layer[i].TreeChildren)):
                nextLayer.append(layer[i].TreeChildren[k]) # Appends one unit at a time to get good list of next layer

    posX = posX + xSpaceTree

    if nextLayer:  # Recursive call with the next layer, if it exists
        drawGraphTree(nextLayer, posX)
    elif nextLayer == 0:  # Otherwise stop
        return
    return
#  Draw the graph tree
drawGraphTree([AllPACUnits[0]], 10)  # Draw the tree from the root

#  Draw lines between elements
for unit in AllPACUnits:
    for tree in unit.TreeChildren:
        draw_unitLine(unit.pos[0], unit.pos[1], tree.pos[0], tree.pos[1])
"""
graph.draw_image(filename = 'img1.png', location = ((150,0)))
graph.draw_image(filename = 'img2.png', location = ((450,0)))
graph.draw_image(filename = 'img3.png', location = ((750,0)))
graph.draw_image(filename = 'img4.png', location = ((1050,0)))
"""

# ID DEFINITION:  PACUNIT D N/A - ELEMENT AFFECTED - ELEMENT ORIGIN

#  DF Display
for dis in AllDisassemblies:
    IDorigin = dis.DFID #PROBLEM HER! Forskel mellem XML reader og initial GUI i DFID definition
    IDAsLetters = " ".join(re.split("[^a-zA-Z]*", IDorigin)).strip()  # Keeps the letters, strip removes spaces
    if IDAsLetters[0] == 'P':
        Origin = AllPACUnits[0].DFSNonRecursive('Parent', 'ID', IDorigin)
        drawDisassemblySquare(Origin[0].pos[0], Origin[0].pos[1])
    if IDAsLetters[0] == 'A':
        Origin = AllPACUnits[0].DFSNonRecursive('Action', 'ID', IDorigin)
        drawDisassemblySquare(Origin[0].pos[0], Origin[0].pos[1])
    if IDAsLetters[0] == 'C' or IDAsLetters[0] == 'c':
        Origin = AllPACUnits[0].DFSNonRecursive('Children', 'ID', IDorigin)
        drawDisassemblySquare(Origin[0].pos[0], Origin[0].pos[1])

#  DF propagate

#  DF create

'''
  --- DF PROBLEMS ---
Propagation: when does it stop? If it does

What if two children are welded together as a consequence of a DF?

ID: number after D should be the number of DFs on current element, not type. Type is already implicit in ID (P/A/C)
'''
# path DEI test
#print('pathDEI to 14A1-13C2 is supposed to be 4, and is: '+str(pathDEI('14A1-13C2')))
#print('pathDEI to 2A1-1C1 is supposed to be 2, and is: '+str(pathDEI('2A1-1C1')))
#print('pathDEI to 10A1-9C4 is supposed to be 9, and is: '+str(pathDEI('10A1-9C4')))

# --- Run the event loop ---
while True:
    window, event, values = sg.read_all_windows()
    # Exit the program or close windows
    if event == sg.WIN_CLOSED or event == 'Exit':
        # WIN_CLOSED Doesn't work for window1
        window.close()
        if window == windowP:  # if closing win 2, mark as closed
            windowP = None
        elif window == windowA:  # if closing win 2, mark as closed
            windowA = None
        elif window == windowC:  # if closing win 2, mark as closed
            windowC = None
        elif window == window1:  # if closing win 1, exit program
            break
    #  event, values = window1.read()
    print(window.Title, event, values)
    if window == window1 and event.endswith('+UP'):  # If a click happens
        x, y = values["-GRAPH-"]  # Record the location
        for unit in AllPACUnits:
            if unit.Parent.pos[0] - sizeX / 2 <= x <= unit.Parent.pos[0] + sizeX / 2 and\
                        unit.Parent.pos[1] - sizeY / 2 <= y <= unit.Parent.pos[1] + sizeY / 2:
                #  Create Parent window
                windowP = make_winP(unit.Parent)
                #  Extend layout according to DFs
                matching_list = ObjFromAttrib('DFID', unit.Parent.ID,
                                              AllDisassemblies)  # DFID kommer ikke til at passe med initial GUI
                if isinstance(matching_list, list):
                    for dis in matching_list:
                        window.extend_layout(windowP['-FRAME-'], [
                            [sg.HSeparator()],
                            [sg.T("DF ID: " + dis.ID)],
                            [sg.T("DF effect: " + dis.DFEffect)],
                            [sg.T("Disassembly Type: " + dis.DAType)],
                            [sg.T("Disassembly Tool: " + dis.DATool)],
                            [sg.T("DF Type: " + dis.DType)],
                            [sg.T("Affected element: " + dis.DFID)]])
                else:
                    window.extend_layout(windowP['-FRAME-'], [
                        [sg.HSeparator()],
                        [sg.T("DF ID: " + matching_list.ID)],
                        [sg.T("DF effect: " + matching_list.DFEffect)],
                        [sg.T("Disassembly Type: " + matching_list.DAType)],
                        [sg.T("Disassembly Tool: " + matching_list.DATool)],
                        [sg.T("DF Type: " + matching_list.DType)],
                        [sg.T("Affected element: " + matching_list.DFID)]])
            elif unit.Action.pos[0] - sizeX / 2 <= x <= unit.Action.pos[0] + sizeX / 2 and\
                        unit.Action.pos[1] - sizeY / 2 <= y <= unit.Action.pos[1] + sizeY / 2:
                windowA = make_winA(unit.Action)
                #  Extend layout according to DFs
                matching_list = ObjFromAttrib('DFID', unit.Action.ID, AllDisassemblies) # DFID kommer ikke til at passe med initial GUI
                if isinstance(matching_list, list):
                    for dis in matching_list:
                        window.extend_layout(windowA['-FRAME-'],[
                        [sg.HSeparator()],
                        [sg.T("DF ID: "+dis.ID)],
                        [sg.T("DF effect: "+dis.DFEffect)],
                        [sg.T("Disassembly Type: "+dis.DAType)],
                        [sg.T("Disassembly Tool: "+dis.DATool)],
                        [sg.T("DF Type: "+dis.DType)],
                        [sg.T("Affected element: "+dis.DFID)]])
                else:
                    window.extend_layout(windowA['-FRAME-'], [
                        [sg.HSeparator()],
                        [sg.T("DF ID: " + matching_list.ID)],
                        [sg.T("DF effect: " + matching_list.DFEffect)],
                        [sg.T("Disassembly Type: " + matching_list.DAType)],
                        [sg.T("Disassembly Tool: " + matching_list.DATool)],
                        [sg.T("DF Type: " + matching_list.DType)],
                        [sg.T("Affected element: " + matching_list.DFID)]])
            elif isinstance(unit.Children, list):  # If there are more than 1 child in the PAC unit
                for child in unit.Children:
                    if child.pos[0] - sizeX / 2 <= x <= child.pos[0] + sizeX / 2 and\
                        child.pos[1] - sizeY / 2 <= y <= child.pos[1] + sizeY / 2:
                        #  Create child window
                        windowC = make_winC(child)  # Open the information window
                        #  Extend layout according to DFs
                        matching_list = ObjFromAttrib('DFID', child.ID,
                                                      AllDisassemblies)  # DFID kommer ikke til at passe med initial GUI
                        if isinstance(matching_list, list):
                            for dis in matching_list:
                                window.extend_layout(windowC['-FRAME-'], [
                                    [sg.HSeparator()],
                                    [sg.T("DF ID: " + dis.ID)],
                                    [sg.T("DF effect: " + dis.DFEffect)],
                                    [sg.T("Disassembly Type: " + dis.DAType)],
                                    [sg.T("Disassembly Tool: " + dis.DATool)],
                                    [sg.T("DF Type: " + dis.DType)],
                                    [sg.T("Affected element: " + dis.DFID)]])
                        else:
                            window.extend_layout(windowC['-FRAME-'], [
                                [sg.HSeparator()],
                                [sg.T("DF ID: " + matching_list.ID)],
                                [sg.T("DF effect: " + matching_list.DFEffect)],
                                [sg.T("Disassembly Type: " + matching_list.DAType)],
                                [sg.T("Disassembly Tool: " + matching_list.DATool)],
                                [sg.T("DF Type: " + matching_list.DType)],
                                [sg.T("Affected element: " + matching_list.DFID)]])
            elif unit.Children.pos[0] - sizeX / 2 <= x <= unit.Children.pos[0] + sizeX / 2 and\
                        unit.Children.pos[1] - sizeY / 2 <= y <= unit.Children.pos[1] + sizeY / 2:  # If there is only 1 child in the PAC unit
                windowC = make_winC(unit.Children)  # Open the information window
                #  Extend layout according to DFs
                matching_list = ObjFromAttrib('DFID', unit.Children.ID,
                                              AllDisassemblies)  # DFID kommer ikke til at passe med initial GUI
                if isinstance(matching_list, list):
                    for dis in matching_list:
                        window.extend_layout(windowC['-FRAME-'], [
                            [sg.HSeparator()],
                            [sg.T("DF ID: " + dis.ID)],
                            [sg.T("DF effect: " + dis.DFEffect)],
                            [sg.T("Disassembly Type: " + dis.DAType)],
                            [sg.T("Disassembly Tool: " + dis.DATool)],
                            [sg.T("DF Type: " + dis.DType)],
                            [sg.T("Affected element: " + dis.DFID)]])
                else:
                    window.extend_layout(windowC['-FRAME-'], [
                        [sg.HSeparator()],
                        [sg.T("DF ID: " + matching_list.ID)],
                        [sg.T("DF effect: " + matching_list.DFEffect)],
                        [sg.T("Disassembly Type: " + matching_list.DAType)],
                        [sg.T("Disassembly Tool: " + matching_list.DATool)],
                        [sg.T("DF Type: " + matching_list.DType)],
                        [sg.T("Affected element: " + matching_list.DFID)]])

'''
Old method to display images
                        if child.imgDisp:  # Delete image if image already exists
                            graph.DeleteFigure(child.img)
                            child.imgDisp = False
                        elif not child.imgDisp:  # Else draw
                            child.img = graph.draw_image(filename=child.imgFile,
                                                           location=(x, y))  # Draw image at location
                            child.imgDisp = True
'''

#Change colors of PAC model as options?

# Close the PySimpleGUI window
window1.close()