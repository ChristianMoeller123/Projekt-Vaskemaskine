import math
import pickle  # Read/write objects
import re  # Library for handling strings
import os

with open('objects.pickle', 'rb') as f:
    x = pickle.load(f)
    AllParents = x['Parents']
    AllChildren = x['Children']
    AllActions = x['Actions']
    AllDisassemblies = x['Disassemblies']
    AllPACUnits = x['PACUnits']

#  Function to return star.
def GaFun(Tool):
    # Small tools
    if Tool in ['Screwdriver', 'Hand', 'Hands', 'Plectrum', 'Wrench', 'Hammer', 'Cross-Head Screwdriver', 'Cross-head screwdriver', 'Socket Wrench', 'Plectrum', 'Tri-Wing Screwdriver', 'Flat head screwdriver']:
        Ga = 10

    # Big tools
    elif Tool in ['Electric Screwdriver', 'Drill']:
        Ga = 30
    else:
        print('Given tool: '+Tool+' is not in our definitions')
        return
    return Ga

def StarFun(Tool, ActionName):
    if Tool in ['Screwdriver', 'Tri-Wing Screwdriver', 'Flat head screwdriver', 'Cross-Head Screwdriver', 'Cross-head screwdriver']:  # Assume 9 turns with screwdriver
        Star = 160
    elif Tool in ['Hand', 'hand', 'Hands', 'Plectrum']:  #  Hand depends on action name
        if ActionName in ['Remove', 'Disconnect']:
            Star = 60  # two hands one turn
        elif ActionName == 'Separate':
            Star = 160  #  2-hands 3 turns
    elif Tool in ['Electric Screwdriver', 'Angle Grinder']:  #  Power tools
        Star = 30  #  Assume screw diam. of 6mm
    elif Tool in ['Socket Wrench', 'Wrench']: # Assume 5 turns with wrench
        Star = 100
    elif Tool == 'Hammer':
        Star = 60  #  Assume 3 strikes or 6 taps with hammer
    else:
        print('Given tool: ' + Tool + ' is not in our definitions')
        return
    return Star

# Variables for MOST
Ab = 30 # Distance from disassembly to desk 2. INDEX!

#  INDEX TO S function. Takes index, gives seconds
def indexSeqToS(Sequence):
    time = sum(Sequence)*0.036  #TMU*0.036 = 1 second
    return time
# Base MOST for Action tools (and times)

def DEIAction(tool, times, ActionName):
    Ga = GaFun(tool)
    Star = StarFun(tool, ActionName)

    #Once:
    Sequence = [Ab, Ga, Ab, 10, 30, Star, Ab, 10, 10]
    #  Repeated for action times:
    if int(times) > 1:
        for i in range(1, int(times)):
            Sequence.extend([10, 30, Star, 10, 10])
    time = indexSeqToS(Sequence)
    return round(time, 2)

for action in AllActions:
    action.DEI = DEIAction(action.Tool, action.Times, action.Desc)
# TAGER IKKE HØJDE FOR N/A

objects = {"Parents": AllParents, "Actions": AllActions, "Children": AllChildren, "Disassemblies": AllDisassemblies, "PACUnits": AllPACUnits}
# Deserializes the objects (find et link?)
with open('objects.pickle', 'wb') as f:
    pickle.dump(objects, f)

#Run GUI Final
os.system('python GUI_Final.py')