# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 08:16:48 2023

@author: chris

Parent, Action, Child and Disassembly classes with the respective attributes
"""

# Class definitions. Parents, children and actions has their own classes
class Parent:

    def __init__(self, ID):
        self.ID = ID
        self.Desc = 'N/A'
        self.PACID = self.extract_PACID()
        self.pos = ()

    def extract_PACID(self):
        PACindex = len(self.ID)
        for char in "PACc":
            index = self.ID.find(char)
            if index != -1 and index < PACindex:  # Bliver -1 hvis bogstavet ikke findes i stringen
                PACindex = index
        return int(self.ID[:PACindex])
class Action:
    def __init__(self, ID):
        self.ID = ID
        self.ActionID = 'N/A'
        self.Desc = 'N/A'
        self.DescDetail = 'N/A' #Detailed description of action
        self.Times = 0 #Amount of times action is repeated
        self.Tool = 'N/A' #Tool needed to perform action
        self.PACID = self.extract_PACID()
        self.pos = ()
        self.DEI = 1

    def extract_PACID(self):
        PACindex = len(self.ID)
        for char in "PACc":
            index = self.ID.find(char)
            if index != -1 and index < PACindex:  # Bliver -1 hvis bogstavet ikke findes i stringen
                PACindex = index
        return int(self.ID[:PACindex])
class Child:
    def __init__(self, ID): # less to initiate
        self.ID = ID
        self.Desc = 'N/A' #  part names from BOM
        self.Number = 0 #Number of children
        self.EoL = 'N/A' #End of Life for child
        self.PACID = self.extract_PACID()
        self.pos = ()
        self.imgDisp = False
        self.imgFile = ''
        self.img = ''

    def extract_PACID(self):
        PACindex = len(self.ID)
        for char in "PACc":
            index = self.ID.find(char)
            if index != -1 and index < PACindex:  # Bliver -1 hvis bogstavet ikke findes i stringen
                PACindex = index
        return int(self.ID[:PACindex])
class Disassembly:
    def __init__(self, ID): #DA is Disassembly action, which is the action needed to perform due to the DF
        self.ID = ID
        self.DFEffect = 'N/A' #DA effect on action
        self.DAType = 'N/A' #Destructive, semi-destructive or non destructive
        self.DATool = 'N/A' #Extra tool needed
        self.DType = 'N/A' #DF1, DF2 or DF3 with relation!
        self.DFID = 'N/A' #Which Parent/Action/Child ID is connected to the DF
class PACUnit:
    def __init__(self, PACID):
        self.PACID = PACID
        self.Parent = Parent
        self.Children = []
        self.Action = Action #action til liste?
        self.TreeChildren = []  # Empty tree children list
        self.Name = '[Insert very intelligent name for the PAC unit here, so Giovanni will be proud]'
        self.RootsDrawn = 0

    def addTreeChildren(self, obj):  # Function to add children
        self.TreeChildren.append(obj)

    def DFSNonRecursive(self, PAC, attrib, val):
    # This function CAN'T find the PAC unit ID! It has to be an attribute of a P/A/C element in the PAC units.
    # PAC is either Parent, Children or Action. As a string
    # attrib is the attribute of the P/A/C as a string
    # val is the desired value
        path = []
        stack = [self]
        while stack:
            s = stack.pop()
            pac = getattr(s, PAC)
            if PAC == 'Children': #If the desired attribute is in the list of children, then iterate over children
                if isinstance(pac, list): #If it's a list, then iterate the list
                    for child in pac:
                        if getattr(child, attrib) == val:
                            return child, path  # Returns the child and the path as a tuple
                else: #If its not, just check the child object
                    if getattr(pac, attrib) == val:
                        return pac, path

            elif getattr(pac, attrib) == val: #Otherwise just return if the desired value is in the P/A
                return pac, path  # Returns the Parent/action and path as a tuple
            if s not in path:
                path.append(s)
            for children in s.TreeChildren:
                stack.append(children)
        return
