def RR(M_rec, M_collEoL):
    return M_rec/M_collEoL
def RE(M_res, M_collEoL):
    return M_res/M_collEoL
def MCI(V, W, M_c, Wf, Wc, L, Lav):
# Notations:
# V   = Element Virgin mass
# W   = Overall amount of unrecoverable waste
# M_c = Child mass
# Wf  = Waste generated to produce feedstock
# Wc  = Waste generated in the recycling process
# L   = Actual realised lifetime
# Lav = Product design life based on market average
    LFI = (V+W)/(2*M_c+(Wf-Wc)/2)
    X = L/Lav
    mci = 1-LFI*(0.9/X)
    return mci

def CI(**kwargs):
    #  Call the function with a key:
    #  RR = CI(M_rec = 194, M_collEoL = 19)
    #  Input variables has to match the needed variables of output (CREATE ERROR FUNCTION!)
    returnList = []
    inputList = []
    for key in kwargs.items():
        inputList.append(key[0])
    if 'M_rec' in inputList:
        RR = kwargs['M_rec']/kwargs['M_collEoL']
        returnList.append(RR)
    if 'M_res' in inputList:
        RE = kwargs['M_res']/kwargs['M_collEoL']
        returnList.append(RE)
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
        returnList.append(MCI)

    return returnList #  Returns RR, RE, MCI accoring to input
RR = CI(M_rec = 194, M_collEoL = 19)
RE = CI(M_res = 10, M_collEoL = 1)
MCI = CI(V = 1, W = 3, M_c = 14, Wf = 4, Wc = 34, L = 5, Lav = 5)
print('RR: '+str(RR)+' RE: '+str(RE)+' MCI: '+str(MCI))
