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

mci = MCI(1, 2, 4, 1, 5, 5, 5)
