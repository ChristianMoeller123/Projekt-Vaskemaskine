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
from PAC_Classes import Parent, Action, Child, Disassembly # Import PAC Classes
import PySimpleGUI as sg
import re # Library for handling strings

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
                       ,fill_color = 'blue', line_color = 'blue', line_width = 2)
    elif IDAsLetters[0] == 'A':
        graph.draw_rectangle((posx - sizeX/2, posy + sizeY/2),\
                       (posx + sizeX/2, posy - sizeY/2)\
                       ,fill_color = 'gray', line_color = 'gray', line_width = 2)
    elif IDAsLetters[0] == 'C' or IDAsLetters[0] ==  'c':
        graph.draw_rectangle((posx - sizeX/2, posy + sizeY/2),\
                       (posx + sizeX/2, posy - sizeY/2)\
                       ,fill_color = 'yellow', line_color = 'yellow', line_width = 2)
    graph.draw_text(obj.ID, (posx, posy)) #50 should be manipulated regarding to ID sizes!
    obj.posX = posx
    obj.posY = posy
def drawLine(cposXL, cposYL, cposXR, cposYR):
    # draws a line from one element to another
    graph.draw_line((cposXL + sizeX/2, cposYL), (cposXR - sizeX/2, cposYR))
#Initial distances between elements
xSpace = 200
ySpace = 90
maxChildren = 8 #An assumption of maximum allowable children in each PAC unit
# Define the graph layout
canvX = 750*len(AllPACUnits)

maxHeight = 0
#Find new function to find max height!
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
    )]
]

# Define the PySimpleGUI layout
layout = [
    [sg.Column(graph_layout, scrollable=True, size=(1200, 1000))]
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
        drawLine(posX, posY, posX + xSpace, posY) #Line from parent to action
        #Draw Children
        for j in range(len(layer[i].Children)):
            posYchild = posY + (math.floor(len(layer[i].Children)/2) - j)*ySpace
            drawSquare(posX + 2*xSpace, posYchild, layer[i].Children[j])
            drawLine(posX + xSpace, posY, posX + 2*xSpace, posYchild) #Line from action to children


        #Update number of units in next layer
        if len(layer[i].TreeChildren) != 0:
            for k in range(len(layer[i].TreeChildren)):
                nextLayer.append(layer[i].TreeChildren[k]) #Appends one unit at a time to get good list of next layer

    posX = posX + 3*xSpace
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
                drawLine(child.posX, child.posY, root.Parent.posX, root.Parent.posY)

# Run the event loop
while True:
    event, values = window.read()

    # Exit the program if the window is closed
    if event == sg.WINDOW_CLOSED:
        break

# Close the PySimpleGUI window
window.close()