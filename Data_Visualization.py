import math
import pickle  # Read/write objects
import re  # Library for handling strings
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button
#import openpyxl
#import sys

def ObjFromAttrib(attribute, value, obj_list):  #  finds all objects with a macthing value in the obj list given
    matching_list = []
    for obj in obj_list:
        if getattr(obj, attribute) == value:
            matching_list.append(obj)
    if len(matching_list) == 1:
        return matching_list[0]
    return matching_list

#Save all the data from the 4 WM files
iter = [0,1,2,3]
filenames = ['WM1.pickle','WM2.pickle','WM3.pickle','WM4.pickle']
CI = []
DEI = []
Actiontime = []
DFamount = []
for i in iter:
    CIsum = []
    DEIsum = []
    Actiontimesum = []
    DFamountnum = 0
    with open(filenames[i], 'rb') as f:
        x = pickle.load(f)
        AllParents = x['Parents']
        AllChildren = x['Children']
        AllActions = x['Actions']
        AllDisassemblies = x['Disassemblies']
        AllPACUnits = x['PACUnits']
    for child in AllChildren:
        if child.isLeaf:
            if child.EoLval == 'N/A':
                print('Child: '+child.ID +'is N/A, and is ignored')
            else:
                CIsum.append(child.EoLval)
    for action in AllActions:
        DEIsum.append(action.ActionDEI)
        Actiontimesum.append(action.ActionTime)
    for diss in AllDisassemblies:
        DFamountnum += 1
    CI.append(CIsum)
    DEI.append(DEIsum)
    Actiontime.append(Actiontimesum)
    DFamount.append(DFamountnum)

# Function to create a figure with four bar charts as subplots
def create_bar_chart_subplots():
    categories = ['WM1', 'WM2', 'WM3', 'WM4']

    fig, axs = plt.subplots(2, 2, figsize=(10, 8))

    # Bar width
    bar_width = 0.35
    bar_positions = np.arange(len(categories))

    CImean = []
    DEIsum = []
    Actiontimesum = []
    for i in range(len(CI)):
        CImean.append(np.mean(CI[i]))
        DEIsum.append(np.sum(DEI[i]))
        Actiontimesum.append(np.sum(Actiontime[i]))


    # Plot bars for each metric in subplots
    metrics = [CImean, DEIsum, Actiontimesum, DFamount]
    labels = ['Average CI', 'Total DEI', 'Total Action time', 'Amount of DFs']

    for i in range(4):
        row, col = divmod(i, 2)
        axs[row, col].bar(bar_positions, metrics[i], width=bar_width)
        axs[row, col].set_xticks(bar_positions)
        axs[row, col].set_xticklabels(categories)
        #axs[row, col].legend()
        axs[row, col].set_title(labels[i])

    # Adjust layout for better appearance
    plt.tight_layout()
    plt.suptitle('Product family analysis')
    plt.show()


# Function to create the second figure with multiple subplots
def create_subplots_figure():
    # Set a seed for reproducibility
    np.random.seed(42)

    # Number of disassemblies
    num_disassemblies = 1000

    # Number of PAC units
    num_pac_units = 14

    # Disassembly failure data
    failure_prob = 0.05
    disassembly_failures = np.random.choice([0, 1], size=(num_disassemblies, num_pac_units),
                                            p=[1 - failure_prob, failure_prob])

    # Disassembly Effort Index (DEI) data
    dei_mean = 267.84
    dei_std = 50
    dei_values = np.random.normal(dei_mean, dei_std, size=num_disassemblies)

    # Circularity index data
    circularity_mean = 0.5642857142857143
    circularity_std = 0.1
    circularity_values = np.random.normal(circularity_mean, circularity_std, size=num_disassemblies)

    # Create subplots for DEI and Circularity Index
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))

    # Plot histogram for DEI
    ax1.hist(dei_values, bins=30, density=True, alpha=0.7, color='blue', label='DEI Histogram')
    xmin, xmax = ax1.get_xlim()
    x = np.linspace(xmin, xmax, 100)
    p = np.exp(-(x - dei_mean) ** 2 / (2 * dei_std ** 2)) / (np.sqrt(2 * np.pi) * dei_std)
    ax1.plot(x, p, 'k', linewidth=2, label='Normal Distribution')
    ax1.set_title('Disassembly Effort Index (DEI) Histogram with Overlay')
    ax1.set_xlabel('DEI Values')
    ax1.set_ylabel('Frequency')
    ax1.legend()

    # Plot histogram for Circularity Index
    ax2.hist(circularity_values, bins=30, density=True, alpha=0.7, color='green', label='Circularity Index Histogram')
    xmin, xmax = ax2.get_xlim()
    x = np.linspace(xmin, xmax, 100)
    p = np.exp(-(x - circularity_mean) ** 2 / (2 * circularity_std ** 2)) / (np.sqrt(2 * np.pi) * circularity_std)
    ax2.plot(x, p, 'k', linewidth=2, label='Normal Distribution')
    ax2.set_title('Circularity Index Histogram with Overlay')
    ax2.set_xlabel('Circularity Index Values')
    ax2.set_ylabel('Frequency')
    ax2.legend()

    # Bar chart for disassembly failures for each PAC unit
    failures_per_pac = np.sum(disassembly_failures, axis=0)
    pac_units = np.arange(num_pac_units)
    ax3.bar(pac_units, failures_per_pac, color='red', alpha=0.7)
    ax3.set_title('Disassembly Failures per PAC Unit')
    ax3.set_xlabel('PAC Unit')
    ax3.set_ylabel('Number of Failures')

    plt.tight_layout()
    plt.show()
    return fig

# Show the first figure
create_bar_chart_subplots()

# Show the second figure
create_subplots_figure()
plt.show()
























#  PREVIOUS PLOTS. USED ON WM3.pickle!
'''
# Plot 1: DF's per element
plt.subplot(2, 3, 1)
x_values1 = []
y_values1 = []
for num in range(len(AllDisassemblies)):
    if AllDisassemblies[num].DFID in x_values1:
        index = x_values1.index(AllDisassemblies[num].DFID)
        y_values1[index] += 1
    else:
        x_values1.append(AllDisassemblies[num].DFID)
        y_values1.append(1)
plt.bar(x_values1, y_values1)
plt.xlabel('Element ID')
plt.ylabel("Amount of DF's")
plt.title("DF's per element")

# Plot 2: DF change in DEI vs change in CI
plt.subplot(2, 3, 2)
x_values2 = []
y_values2 = []
for dis in AllDisassemblies:
    IDAsLetters = " ".join(re.split("[^a-zA-Z]*", dis.DFID)).strip()
    if IDAsLetters[0] == 'C' or IDAsLetters[0] == 'c':
        child = ObjFromAttrib('ID', dis.DFID, AllChildren)
        if child.isLeaf:
            x_values2.append(child.DFCI-float(child.EoLval))
            y_values2.append(0)
        else:
            print("Found a child, which is not a leafchild")
    elif IDAsLetters[0] == 'A':
        action = ObjFromAttrib('ID', dis.DFID, AllActions)
        x_values2.append(0)
        y_values2.append(-action.DFDEI)
    #Do something at parents?
    #Is there a case, where a DF is on both C and A?
plt.scatter(x_values2, y_values2)
plt.xlabel('\Delta CI')
plt.ylabel('\Delta DEI')
plt.title('Change in DEI and CI for each DF')
plt.legend()

# Plot 3: CI for each leaf child
plt.subplot(2, 3, 3)
x_values3 = []
y_values3 = []
for child in AllChildren:
    if child.isLeaf:
        x_values3.append(child.ID)
        if child.DFCI:
            y_values3.append(float(child.DFCI))
        else:
            y_values3.append(float(child.EoLval))
plt.bar(x_values3, y_values3)
plt.xlabel('Leaf child ID')
plt.xticks(x_values3, rotation='vertical')
plt.ylabel('CI')
plt.title('CI for each leaf Child')

# Plot 4: total MOST for each action
plt.subplot(2, 3, 4)
x_values4 = []
y_values4 = []
for action in AllActions:
    x_values4.append(action.ID)
    y_values4.append(action.ActionDEI)
plt.bar(x_values4, y_values4)
plt.xlabel('Action ID')
plt.xticks(x_values4, rotation='vertical')
plt.ylabel('DEI [s]')
plt.title('Total DEI for each action')

# Plot 5: MOST with 3 subgroups
plt.subplot(2, 3, 5)
x_values5 = []
y_values51 = []
y_values52 = []
y_values53 = []
for action in AllActions:
    x_values5.append(action.ID)
    y_values51.append(action.ThinkingTime)
    y_values52.append(action.ActionTime)
    y_values53.append(action.InformationInput)
third_bottom_val = []
for i in range(len(y_values51)):
    third_bottom_val.append(y_values51[i]+y_values52[i])
plt.bar(x_values5, y_values51, label='Thinking time')
plt.bar(x_values5, y_values52, bottom=y_values51, label='Action time')
plt.bar(x_values5, y_values53, bottom=third_bottom_val, label='Information input time')

plt.xlabel('Action ID')
plt.xticks(x_values5, rotation='vertical')
plt.ylabel('DEI [s]')
plt.title('MOST Subgroups for each action')
plt.legend()

# Plot 6: DEI vs CI for each PAC unit.
# dictionary pac
DEIDict = {}
CIDict = {}
for unit in AllPACUnits:
    key = unit.PACID
    DEIval = unit.Action.ActionDEI + unit.Action.DFDEI
    DEIDict[key] = DEIval
    for child in unit.Children:
        if child.isLeaf:
            ChildKey = child.ID
            if child.DFCI != '':
                CIval = child.DFCI
            else:
                CIval = float(child.EoLval)
            CIDict[ChildKey] = CIval
# Extract keys and values from the dictionaries
DEI_keys, DEI_values = list(DEIDict.keys()), list(DEIDict.values())
CI_keys, CI_values = list(CIDict.keys()), list(CIDict.values())

# Extract the corresponding CI values based on DEI keys8 = {float} 265.88
corresponding_CI_values = [[]]
for unit in AllPACUnits:
    childlist = []
    for child in unit.Children:
        if child.isLeaf:
            if child.DFCI != '':
                childlist.append(float(child.DFCI))
            else:
                childlist.append(float(child.EoLval))
    corresponding_CI_values.append(childlist)
corresponding_CI_values.pop(0)

# Initialize lists to store x and y coordinates for the scatter plot
x_values6 = []
y_values6 = []

# Iterate through the 1D array and the corresponding subarrays in the 2D array
for i in range(len(DEI_values)):
    x = DEI_values[i]  # X-coordinate is the value from the 1D array
    subarray = corresponding_CI_values[i]  # Corresponding subarray from the 2D array
    for y in subarray:
        x_values6.append(x)
        y_values6.append(y)

# Create a scatter plot
plt.subplot(2, 3, 6)
#plt.figure(figsize=(10, 6))
plt.scatter(x_values6, y_values6, marker='o', color='blue')

# Add labels without overlapping
savedvals = [[]]
for i in range(len(x_values6)):
    fact = 0.2
    pair = [x_values6[i]+fact,y_values6[i]]
    if pair not in savedvals:
        plt.text(x_values6[i]+fact,y_values6[i], CI_keys[i], fontsize=10, ha='left', va='bottom')
    else:
        plt.text(x_values6[i] + fact, y_values6[i] - fact/5, CI_keys[i], fontsize=10, ha='left', va='bottom')
        pair = [x_values6[i] + fact, y_values6[i] - fact/5]
    savedvals.append(pair)

plt.xlabel('DEI')
plt.ylabel('CI')
plt.title('Scatter Plot of DEI vs CI')
plt.grid()

# Adjust layout to prevent overlapping
plt.tight_layout()

# Display the plots
plt.show()




# Plot 7: MOST subgroups without information input time
x_values5 = []
y_values51 = []
y_values52 = []
for action in AllActions:
    x_values5.append(action.ID)
    y_values51.append(action.ThinkingTime)
    y_values52.append(action.ActionTime)

plt.bar(x_values5, y_values51, label='Thinking time')
plt.bar(x_values5, y_values52, bottom=y_values51, label='Action time')

plt.xlabel('Action ID')
plt.xticks(x_values5, rotation='vertical')
plt.ylabel('DEI [s]')
plt.title('MOST Subgroups for each action')
plt.legend()
plt.tight_layout()
plt.show()


#DF diff in CI and DEI. Not possible for each DF, as a DF doesn't necceraily decrease CI.
for diss in AllDisassemblies:
    ID = diss.DFID[:diss.DFID.index('-')]
    for unit in AllPACUnits:
        if unit.Action.ID[:diss.DFID.index('-')] == ID:

'''