################################################################################
import math

from common import *
from canvas import *

from geom_vector import *
from geom_bounding_box import *

################################################################################
class CLineDesc:
    #---------------------------------------------------------------------------
    def __init__(self, l, dir):
        self.l = l          # Line
        self.dir = dir      # Direction

################################################################################
class CLineData:
    #---------------------------------------------------------------------------
    def __init__(self):
        self.Reset()

    #---------------------------------------------------------------------------
    def Reset(self):
        self.dir = CLine.DIR_NONE           # Direction in which this line has been processed
        self.circle_cross = []              # Points where circle crosses line
        self.new_vertices = []              # New vertices that were created during normalization
        self.middle = CVertex()             # Point that lies between 2 cross-points
        self.cross = CVertex()              # Central cross-point
        self.perpendicular = CVector()      # Perpendicular vector from circle-center to central cross-point
        self.first = CVector()              # Vector from circle-center to first-vertex
        self.in_new_mesh = 0                # True if line is moved to new mesh

    #---------------------------------------------------------------------------
    def AddCross(self, v, append):
        if append:
            self.circle_cross.append(v)    # append
        else:
            self.circle_cross.insert(0, v) # prepend

    #---------------------------------------------------------------------------
    def IsCrossed(self):
        if len(self.circle_cross):
            return 1
        else:
            return 0

    #---------------------------------------------------------------------------
    def GetCross(self, dir):
        if len(self.circle_cross) < 2:
            return self.circle_cross

        # Cross-vertex that is closer to beginning of the line should be first
        if dir == CLine.DIR_FORW:
            return [self.circle_cross[0], self.circle_cross[1]]
        else:
            return [self.circle_cross[1], self.circle_cross[0]]

################################################################################
class CLine:
    #---------------------------------------------------------------------------
    DIR_NONE = -1
    DIR_REV = 0
    DIR_FORW = 1
    DIR_BOTH = 2

    #---------------------------------------------------------------------------
    cnt = 0

    #---------------------------------------------------------------------------
    def __init__(self, v0, v1):
        # Vertices [reversed, forward]
        self.vertices = [[v1, v0], [v0, v1]]

        # Vector [reversed, forward]
        self.vector = [CVector(v1, v0), CVector(v0, v1)]

        # Normal [reversed, forward]
        self.normal = [
            self.vector[CLine.DIR_REV].GetNormal(),
            self.vector[CLine.DIR_FORW].GetNormal()]

        # Misc
        self.center = CVertex((v0.x + v1.x) / 2, (v0.y + v1.y) / 2)
        self.bounding_box = CBoundingBox([v0, v1])

        # Processing data
        self.data = CLineData()

        # Id
        self.id = CLine.cnt
        CLine.cnt += 1

        # Adjacent triangles - will be populated in CMesh::AddTriangle
        self.triangles = []

    #---------------------------------------------------------------------------
    def GetVertices(self, dir):
        return self.vertices[dir]

    #---------------------------------------------------------------------------
    def GetVector(self, dir):
        return self.vector[dir]

    #---------------------------------------------------------------------------
    def GetNormal(self, dir):
        return self.normal[dir]

    #---------------------------------------------------------------------------
    def GetAdjacentTriangle(self, t):
        if len(self.triangles) == 2:
            t0 = self.triangles[0]
            t1 = self.triangles[1]
            if t0 == t:
                return [1, t1]
            elif t1 == t:
                return [1, t0]

        return [0, 0]

################################################################################
class CLinearEquasion:
    #---------------------------------------------------------------------------
    def __init__(self, v0, v1):
        # y = a * x + b
        self.vect = CVertex(v1.x - v0.x, v1.y - v0.y)
        self.is_vertical = 1
        self.a = 0
        self.b = 0

        if self.vect.x:
            # Line is not vertical
            self.is_vertical = 0
            self.a = self.vect.y / self.vect.x
            self.b = v0.y - self.a * v0.x
