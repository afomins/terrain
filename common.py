################################################################################
def ASSERT(condition, msg, fatal = 1):
    if condition == 0:
        print "ASSERT :: %s" % (msg)
        if fatal:
            EAT-MY-SHORTS
            exit()

################################################################################
def LOG(msg):
    if glob.logging:
        print msg

################################################################################
def SQR(val):
    return (val * val)

################################################################################
def MIN(v0, v1):
    if v0 < v1:
        return v0
    else:
        return v1

################################################################################
def MAX(v0, v1):
    if v0 > v1:
        return v0
    else:
        return v1

################################################################################
def SIGN(v):
    if v > 0:
        return +1
    elif v < 0:
        return -1
    else:
        return 0

################################################################################
def TEST_ARRAYS(array, val, strict = 1):
    tmp = list(array)
    for v in val:
        if v in tmp:
            if strict:
                tmp.remove(v)
            else:
                return 1
        else:
            if strict:
                return 0

    return strict

################################################################################
class glob: 
    canvas = 0
    controls = 0
    engine = 0
    logging = 1
    INFINITE = 1005000

################################################################################
class IEventHandler:
    #---------------------------------------------------------------------------
    def OnRedrawEvent(self):
        ASSERT(0, "OnRedrawEvent is not implemented")

    #---------------------------------------------------------------------------
    def OnMouseMoveEvent(self, x, y):
        ASSERT(0, "OnMouseMoveEvent is not implemented")

    #---------------------------------------------------------------------------
    def OnMousePressEvent(self):
        ASSERT(0, "OnMousePressEvent is not implemented")

    #---------------------------------------------------------------------------
    def OnMouseWheelEvent(self, delta):
        ASSERT(0, "OnMouseWheelEvent is not implemented")
