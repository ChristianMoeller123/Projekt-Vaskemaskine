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
                       ,fill_color = 'gray', line_color = 'gray', line_width = 2)
    elif IDAsLetters[0] == 'C' or IDAsLetters[0] ==  'c':
        graph.draw_rectangle((posx - sizeX/2, posy + sizeY/2),
                       (posx + sizeX/2, posy - sizeY/2)
                       ,fill_color = 'yellow', line_color = 'yellow', line_width = 2)
    graph.draw_text(obj.ID, (posx, posy))
    obj.pos = (posx, posy)

def drawLine(cposL, cposR):
    # draws a line from one element to another
    # cposL is the position coordinates of L as cposL = (x, y)
    graph.draw_line((cposL[0] + sizeX/2, cposL[1]), (cposR[0] - sizeX/2, cposR[1]))

def drawDashedLine(start, end):
    # start = (startX, startY)
    # end = (endX, endY)
    # Calculate the distance between the start and end points
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = (dx ** 2 + dy ** 2) ** 0.5

    # Calculate the number of dashes needed to cover the distance
    dash_length = 5  # Length of each dash in pixels
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
        graph.draw_line((dash[0], dash[1]), (dash[2], dash[3]))

def drawUnitLine(start, end, n):
    turn = (int(unitSpace/3) - xSpace) + 20*n
    drawDashedLine(start, (start[0] + turn, start[1]))
    drawDashedLine((start[0] + turn, start[1]), (start[0] + turn, end[1]))
    drawDashedLine((start[0] + turn, end[1]), end)

# Function to find DEI for a given path:
def pathDEI(ID):
    elem, path = AllPACUnits[0].DFSNonRecursive('Action', 'ID', ID)
    pathDEI = 0
    leafNodeIndices = []
    # Delete elements not in the direct path to the desired action
    for i in range(len(path)):
        if not path[i].TreeChildren: # If it's a leaf node
            leafNodeIndices.append(path.index(path[i]))
    for leaf in leafNodeIndices: # Go back and delete
        j = 0
        # While there are no tree children or only 1
        while path[leaf-j] and len(path[leaf - j].TreeChildren) < 2:
            path[leaf - j] = 0
            j = j + 1

    # sum DEIs in path
    for unit in path:
         if unit:
             pathDEI = pathDEI + unit.Action.DEI
    pathDEI = pathDEI + elem.DEI
    return pathDEI


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

# Define the graph layout
canvX = 750*len(AllPACUnits)


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

graph_layout = [
    [sg.Graph(
        canvas_size=(canvX, canvY),
        graph_bottom_left=(0, math.floor(-canvY/2)),
        graph_top_right=(canvX, canvY/2),
        background_color="white",
        key="-GRAPH-",
        drag_submits=True,
        enable_events=True
    )]
]

# Define the PySimpleGUI layout
layout = [
    [sg.Column(graph_layout, scrollable=True, size=(1200, 800))]
]

# Create the PySimpleGUI window
window = sg.Window("Graph Window", layout, finalize=True, resizable=True)


graph = window["-GRAPH-"]

# Add the tree from the AllPACUnits list
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

# FIX HOW THE LINES ARE DRAWN?
for unit in AllPACUnits:
    if isinstance(unit.Children, list):  # If there are more than 1 child in the PAC unit
        for child in unit.Children:
            for root in unit.TreeChildren:
                if child.ID[:child.ID.index('-')] == root.Parent.ID[root.Parent.ID.index('-') + 1:]:
                    drawUnitLine((child.pos[0] + sizeX/2, child.pos[1]), (root.Parent.pos[0] - sizeX/2, root.Parent.pos[1]), child.numRoots)
                    child.numRoots = child.numRoots + 1
                    # print('from '+str(child.PACID) +' to ' +str(root.Parent.PACID))
    else:  # If there is only 1 child in the PAC unit
        for root in unit.TreeChildren:
            if unit.Children.ID[:unit.Children.ID.index('-')] == root.Parent.ID[root.Parent.ID.index('-')+1:]:
                # draw a line from the right side of child element to the left side of parent element
                drawUnitLine((unit.Children.pos[0] + sizeX/2, unit.Children.pos[1]), (root.Parent.pos[0] - sizeX/2, root.Parent.pos[1]), unit.Children.numRoots)
                unit.Children.numRoots = unit.Children.numRoots + 1
                # print('from ' + str(unit.Children.PACID) + ' to ' + str(root.Parent.PACID))
"""
graph.draw_image(filename = 'img1.png', location = ((150,0)))
graph.draw_image(filename = 'img2.png', location = ((450,0)))
graph.draw_image(filename = 'img3.png', location = ((750,0)))
graph.draw_image(filename = 'img4.png', location = ((1050,0)))
"""

# path DEI test
print('pathDEI to 14A1-13C2 is supposed to be 4, and is: '+str(pathDEI('14A1-13C2')))
print('pathDEI to 2A1-1C1 is supposed to be 2, and is: '+str(pathDEI('2A1-1C1')))
print('pathDEI to 10A1-9C4 is supposed to be 9, and is: '+str(pathDEI('10A1-9C4')))

# Run the event loop
while True:
    event, values = window.read()
    if event == "-GRAPH-":  # If a click happens
        x, y = values["-GRAPH-"]  # Record the location
        for i in range(x-math.floor(sizeX/2), x+math.floor(sizeX/2)):  # Check if the mouse was in ANY rectangle (this is stupid)
            for j in range(y-math.floor(sizeY/2), y+math.floor(sizeY/2)):
                elem = AllPACUnits[0].DFSNonRecursive('Children', 'pos', (i, j))  # Find obj at location
                if elem:  # If an object at the click position is found:
                    if elem[0].imgDisp:  # Delete image if image already exists
                        graph.DeleteFigure(elem[0].img)
                        elem[0].imgDisp = False
                    else:  # Else draw
                        elem[0].img = graph.draw_image(filename=elem[0].imgFile, location=(x, y))  # Draw image at location
                        elem[0].imgDisp = True
    # HVIS KLIKKET IKKE ER KORT NOK, SKER DER FEJL!
    # Exit the program if the window is closed
    if event == sg.WINDOW_CLOSED:
        break
# Loop elements, compare cpos with +- space of click. Give every element a +- space attribute


"""        
maybe add this to determine when mouse button is released?
while not event.endswith('+UP'):
    pass
"""
# Close the PySimpleGUI window
window.close()