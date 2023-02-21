# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 08:11:17 2023

@author: chris
"""

import pickle
from PAC_Classes import Parent, Action, Child, Disassembly # Import PAC Classes

# Read the objects from the file
with open("objects.pickle", "rb") as f:
    objects = pickle.load(f)
    Parents = objects["Parents"]
    Actions = objects["Actions"]
    Children = objects["Children"]
    Disassemblies = objects["Disassemblies"]
