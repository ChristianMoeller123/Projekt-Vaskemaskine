# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 08:11:17 2023

@author: chris
"""
import igraph as ig # Graphical Tree
from igraph import Graph, EdgeSeq # Graphical tree
import plotly.graph_objects as go
import plotly.express as px
import math
import pickle # Read/write objects
from PAC_Classes import Parent, Action, Child, Disassembly, PACUnit # Import PAC Classes
import PySimpleGUI as sg
import re # Library for handling strings
import time

with open('objects.pickle', 'rb') as f:
    x = pickle.load(f)
    AllParents = x['Parents']
    AllChildren = x['Children']
    AllActions = x['Actions']
    AllDisassemblies = x['Disassemblies']
    AllPACUnits = x['PACUnits']

#Draw square function. Input: P/A/C obj, center pos
#Output: Square element
    sizeX = 150
    sizeY = 60
def drawSquare(posx, posy, obj):
    # parent = blue, action = gray, children = yellow.
    # 150x x 60y
    IDAsLetters = " ".join(re.split("[^a-zA-Z]*", obj.ID)).strip()
    if IDAsLetters[0] == 'P':
        graph.draw_rectangle((posx - sizeX/2, posy + sizeY/2),\
                       (posx + sizeX/2, posy - sizeY/2)\
                       ,fill_color = 'green', line_color = 'green', line_width = 2)
    elif IDAsLetters[0] == 'A':
        graph.draw_rectangle((posx - sizeX/2, posy + sizeY/2),\
                       (posx + sizeX/2, posy - sizeY/2)\
                       ,fill_color = 'gray', line_color = 'gray', line_width = 2)
    elif IDAsLetters[0] == 'C' or IDAsLetters[0] ==  'c':
        graph.draw_rectangle((posx - sizeX/2, posy + sizeY/2),\
                       (posx + sizeX/2, posy - sizeY/2)\
                       ,fill_color = 'yellow', line_color = 'yellow', line_width = 2)
    graph.draw_text(obj.ID, (posx, posy)) #50 should be manipulated regarding to ID sizes!
    obj.pos = (posx, posy)
def drawLine(cposL, cposR):
    # draws a line from one element to another
    #cposL is the position coordinates of L as cposL = (x, y)
    graph.draw_line((cposL[0] + sizeX/2, cposL[1]), (cposR[0] - sizeX/2, cposR[1]))
#Initial distances between elements
xSpace = 200
ySpace = 90
maxChildren = 8 #An assumption of maximum allowable children in each PAC unit
# Define the graph layout
canvX = 750*len(AllPACUnits)

maxHeight = 0

#TO DO: Find new function to find max height!
for Unit in AllPACUnits:
    if len(Unit.TreeChildren)/2 > maxHeight:
        maxHeight = len(Unit.TreeChildren)/2
canvY = 3*maxChildren*ySpace
graph_layout = [
    [sg.Graph(
        canvas_size=(canvX, canvY),
        graph_bottom_left=(0, -canvY/2),
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
window = sg.Window("Graph Window", layout, finalize=True)


graph = window["-GRAPH-"]

# Add the tree from the AllPACUnits list
def drawTree(layer, posX):
    nextLayer = []
    for i in range(len(layer)): #Draw all PACUnits in same layer
        posY = ((math.floor(len(layer)/2))-i)*maxChildren*ySpace
        #Draw line from previous child

        #Draw Parent
        drawSquare(posX, posY, layer[i].Parent)

        #Draw Action
        drawSquare(posX + xSpace, posY, layer[i].Action)
        drawLine((posX, posY), (posX + xSpace, posY)) #Line from parent to action
        #Draw Children
        for j in range(len(layer[i].Children)):
            posYchild = posY + (math.floor(len(layer[i].Children)/2) - j)*ySpace
            drawSquare(posX + 2*xSpace, posYchild, layer[i].Children[j])
            drawLine((posX + xSpace, posY), (posX + 2*xSpace, posYchild)) #Line from action to children


        #Update number of units in next layer
        if len(layer[i].TreeChildren) != 0:
            for k in range(len(layer[i].TreeChildren)):
                nextLayer.append(layer[i].TreeChildren[k]) #Appends one unit at a time to get good list of next layer

    posX = posX + 3.5*xSpace
    if nextLayer:#Recursive call with the next layer, if it exists
        drawTree(nextLayer, posX)
    elif nextLayer == 0: #Otherwise stop
        return
#Starting position:
posX = 75
drawTree([AllPACUnits[0]], posX) #Draw the tree from the root

#Draw lines between pac units
#This is done by comparing all children IDs with all Parent IDs, if any matches, a line is drawn between them
for unit in AllPACUnits:
    for child in unit.Children:
        for root in unit.TreeChildren:
            if child.ID[:child.ID.index('-')] == root.Parent.ID[root.Parent.ID.index('-')+1:]:
                drawLine(child.pos, root.Parent.pos)
"""
graph.draw_image(filename = 'img1.png', location = ((150,0)))
graph.draw_image(filename = 'img2.png', location = ((450,0)))
graph.draw_image(filename = 'img3.png', location = ((750,0)))
graph.draw_image(filename = 'img4.png', location = ((1050,0)))
"""
# Run the event loop
while True:
    event, values = window.read()
    if event == "-GRAPH-": #If a click happens
        x, y = values["-GRAPH-"] #Record the location
        for i in range(x-math.floor(sizeX/2), x+math.floor(sizeX/2)): #Check if the mouse was in ANY rectangle (this is stupid)
            for j in range(y-math.floor(sizeY/2), y+math.floor(sizeY/2)):
                elem = AllPACUnits[0].DFSNonRecursive('Children', 'pos', (i, j)) #Find obj at location
                if elem: #If an object at the click position is found:
                    if elem.imgDisp: #Delete image if image already exists
                        graph.DeleteFigure(elem.img)
                        elem.imgDisp = False
                    else: #Else draw
                        elem.img = graph.draw_image(filename=elem.imgFile, location=(x, y))  # Draw image at location
                        elem.imgDisp = True
    #HVIS KLIKKET IKKE ER KORT NOK, SKER DER FEJL!
    # Exit the program if the window is closed
    if event == sg.WINDOW_CLOSED:
        break
"""        
maybe add this to determine when mouse button is released?
while not event.endswith('+UP'):
    pass
"""
# Close the PySimpleGUI window
window.close()