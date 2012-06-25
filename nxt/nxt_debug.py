DEBUGLEVEL = 3

def dbg_print(element, dbglevel=0):
    if dbglevel == 0:
        print(element)
        return
    if dbglevel < DEBUGLEVEL:
        print('---DEBUG.level '+str(dbglevel)+': '+str(element))