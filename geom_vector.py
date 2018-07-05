################################################################################
import math

from common import *
from canvas import *

from geom_vertex import *

################################################################################
class CVector:
    #---------------------------------------------------------------------------
    normal_quater = [3, 0, 1, 2]

    #---------------------------------------------------------------------------
    def __init__(self, v0 = CVertex(), v1 = CVertex()):
        # Set coordinates
        self.coord = CVertex(v1.x - v0.x, v1.y - v0.y)
        x = self.coord.x;
        y = self.coord.y

        # Set length
        self.len = math.sqrt(SQR(x) + SQR(y))

        # Set unit-vector
        if self.len:
            self.unit = CVertex(x / self.len, y / self.len)
        else:
            self.unit = CVertex()

        # Set quater
        if (x > 0 and y >= 0):
            self.quater = 0        # (0..90)
        elif (x <= 0 and y > 0):
            self.quater = 1        # (90..180)
        elif (x < 0 and y <= 0):
            self.quater = 2        # (180..270)
        elif (x >= 0 and y < 0):
            self.quater = 3        # (270..360)
        else:
            self.quater = -1

    #---------------------------------------------------------------------------
    def GetNormal(self):
        norm = CVector()
        norm.len = 1
        norm.unit.x = self.unit.y
        norm.unit.y = -self.unit.x
        if self.quater == -1:
            norm.quater = -1
        else:
            norm.quater = CVector.normal_quater[self.quater]

        return norm

    #---------------------------------------------------------------------------
    def TestQuater(self, v):
        if self.quater == v.quater:
            return 1
        else:
            return 0
