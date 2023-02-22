# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 08:16:48 2023

@author: chris

Parent, Action, Child and Disassembly classes with the respective attributes
"""

# Class definitions. Parents, children and actions has their own classes
class Parent:
    def __init__(self, ID, Desc):
        self.ID = ID
        self.Desc = Desc
class Action:
    def __init__(self, ID, ActionID, Desc, DescDetail, Times, Tool):
        self.ID = ID
        self.ActionID = ActionID
        self.Desc = Desc
        self.DescDetail = DescDetail #Detailed description of action
        self.Times = Times #Amount of times action is repeated
        self.Tool = Tool #Tool needed to perform action
class Child:
    def __init__(self, ID, Desc, Number, EoL):
        self.ID = ID
        self.Desc = Desc
        self.Number = Number #Number of children
        self.EoL = EoL #End of Life for child
class Disassembly:
    def __init__(self, ID, DFEffect, DAType, DATool, DType, DFID): #DA is Disassembly action, which is the action needed to perform due to the DF
        self.ID = ID
        self.DFEffect = DFEffect #DA effect on action
        self.DAType = DAType #Destructive, semi-destructive or non destructive
        self.DATool = DATool #Extra tool needed
        self.DType = DType #DF1, DF2 or DF3 with relation!
        self.DFID = DFID #Which Parent/Action/Child ID is connected to the DF