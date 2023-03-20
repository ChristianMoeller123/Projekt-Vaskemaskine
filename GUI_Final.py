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
                             ,fill_color = 'green', line_color = 'green', line_width = 2)
    elif IDAsLetters[0] == 'A':
        graph.draw_rectangle((posx - sizeX/2, posy + sizeY/2),
                             (posx + sizeX/2, posy - sizeY/2)
                             ,fill_color = 'teal', line_color = 'teal', line_width = 2)
    elif IDAsLetters[0] == 'C' or IDAsLetters[0] ==  'c':
        graph.draw_rectangle((posx - sizeX/2, posy + sizeY/2),
                             (posx + sizeX/2, posy - sizeY/2)
                             ,fill_color = 'sky blue', line_color = 'sky blue', line_width = 2)
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
             pathDEI = pathDEI + unit.Action.DEI
    return pathDEI


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


canvX = (3*xSpace+sizeX)*len(AllPACUnits)


# Function to find max height
def largestLayer(layer, maxBreadth):
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
        maxBreadth = largestLayer(nextLayer, maxBreadth)
    elif nextLayer == 0:  # Otherwise stop
        return maxBreadth
    return maxBreadth

maxBreadth = largestLayer([AllPACUnits[0]], 0)
canvY = (maxBreadth+1)*maxChildren*ySpace



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

    # Define the PySimpleGUI layout
    layout = [
        [sg.Button('Options'), sg.Button('Exit')],
        [sg.Column(graph_layout, scrollable=True, size=(1200, 800))]
    ]
    return sg.Window("Graph Window", layout, finalize=True, resizable=True, use_custom_titlebar=True)
def make_winP(obj):
    layout = [
              [sg.Table([['ID', obj.ID],
                         ['Description', obj.Desc]],
                         ['Attribute', 'Value'], num_rows=2)],
              [sg.Button('Add DF'), sg.Button('Exit')]]
    return sg.Window('Parent '+obj.ID, layout, finalize=True, resizable=True)
def make_winA(obj):
    layout = [
              [sg.Table([['ID', obj.ID],
                         ['ActionID', obj.ActionID],
                         ['Description', obj.Desc],
                         ['Detailed description', obj.DescDetail],
                         ['Number of times repeated', obj.Times],
                         ['Tool', obj.Tool],
                         ['DEI for Action', obj.DEI],
                         ['Path DEI to Action', pathDEI(obj.ID)]],
                        ['Attribute', 'Value'], num_rows=8)],
              [sg.Button('Add DF'), sg.Button('Exit')]]
    return sg.Window('Action '+obj.ID, layout, finalize=True, resizable=True)
def make_winC(obj):
    layout = [[sg.Table([['ID', obj.ID],
                         ['Description', obj.Desc],
                         ['Amount', obj.Number],
                         ['End of Life', obj.EoL]],
                        ['Attribute', 'Value'], num_rows=8)],
              [sg.Button('Add DF'), sg.Button('Exit')],
              [sg.Text('Graphical display of Child')],
              [sg.Image(obj.imgFile, size=(400, 400))]]
    return sg.Window('Child '+obj.ID, layout, finalize=True, resizable=True)

# start off with main window open only
window1, windowP, windowA, windowC = make_win1(), None, None, None

graph = window1["-GRAPH-"]

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


# Draw lines between pac units
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
    else:  # If there is only 1 child in the PAC unit
        for root in unit.TreeChildren:
            if unit.Children.ID[:unit.Children.ID.index('-')] == root.Parent.ID[root.Parent.ID.index('-')+1:]:
                # draw a line from the right side of child element to the left side of parent element
                drawUnitLine((unit.Children.pos[0] + sizeX/2, unit.Children.pos[1]), (root.Parent.pos[0] - sizeX/2, root.Parent.pos[1]), unit.RootsDrawn)
                unit.RootsDrawn = unit.RootsDrawn + 1
                # print('from ' + str(unit.Children.PACID) + ' to ' + str(root.Parent.PACID))
"""
graph.draw_image(filename = 'img1.png', location = ((150,0)))
graph.draw_image(filename = 'img2.png', location = ((450,0)))
graph.draw_image(filename = 'img3.png', location = ((750,0)))
graph.draw_image(filename = 'img4.png', location = ((1050,0)))
"""

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
            elif unit.Action.pos[0] - sizeX / 2 <= x <= unit.Action.pos[0] + sizeX / 2 and\
                        unit.Action.pos[1] - sizeY / 2 <= y <= unit.Action.pos[1] + sizeY / 2:
                windowA = make_winA(unit.Action)
            elif isinstance(unit.Children, list):  # If there are more than 1 child in the PAC unit
                for child in unit.Children:
                    if child.pos[0] - sizeX / 2 <= x <= child.pos[0] + sizeX / 2 and\
                        child.pos[1] - sizeY / 2 <= y <= child.pos[1] + sizeY / 2:
                        #  Create child window
                        windowC = make_winC(child)  # Open the information window
            elif unit.Children.pos[0] - sizeX / 2 <= x <= unit.Children.pos[0] + sizeX / 2 and\
                        unit.Children.pos[1] - sizeY / 2 <= y <= unit.Children.pos[1] + sizeY / 2:  # If there is only 1 child in the PAC unit
                windowC = make_winC(unit.Children)  # Open the information window

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