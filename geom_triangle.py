################################################################################
import math

from common import *
from canvas import *

from geom_vertex import *
from geom_bounding_box import *

################################################################################
class CTriangleData:
    #---------------------------------------------------------------------------
    def __init__(self):
        self.Reset()

    #---------------------------------------------------------------------------
    def Reset(self):
        self.cross_type = CTriangle.CROSS_TYPE_NONE
        self.is_inside = 0      # True if circle center is inside the triangle
        self.is_outside = 0     # True if circle absorbes the triangle
        self.in_new_mesh = 0    # True if triangle is moved to new mesh
        self.in_move_stack = 0  # True if triangle is placed in move-stack

################################################################################
class CTriangleLineDesc:
    #---------------------------------------------------------------------------
    def __init__(self, base, next, prev):
        self.base = base
        self.next = next
        self.prev = prev

################################################################################
class CTriangle:
    #---------------------------------------------------------------------------
    opposite_vertex_idx = [2, 0, 1]
    next_line_idx = [1, 2, 0]
    prev_line_idx = [2, 0, 1]

    #---------------------------------------------------------------------------
    CROSS_TYPE_NONE = -1    # Does not cross
    CROSS_TYPE_NORMAL = 0   # Intersects one angle
    CROSS_TYPE1 = 1         # Intersects one line (1)
    CROSS_TYPE2 = 2         # Intersects one line (2)
    CROSS_TYPE3 = 3         # Intersects two lines
    CROSS_TYPE4 = 4         # Intersects three lines
    CROSS_TYPE_HOLE = 5     # Cuts hole
    CROSS_TYPE_ABSORB = 6   # Absorbes whole triangle

    #---------------------------------------------------------------------------
    cnt = 0

    #---------------------------------------------------------------------------
    def __init__(self, v0, v1, v2):
        # Set vertices
        self.vertices = [v0, v1, v2]

        # Set center of triangle
        self.center = CVertex(
            (v0.x + v1.x + v2.x) / 3,
            (v0.y + v1.y + v2.y) / 3)

        # Set bounding box
        self.bounding_box = CBoundingBox(self.vertices)

        # Line descriptors will be set in CMesh::AddTriangle
        self.line_desc = []

        # Processing data
        self.data = CTriangleData()

        # Id
        self.id = CTriangle.cnt
        CTriangle.cnt += 1

    #---------------------------------------------------------------------------
    def GetLineIdx(self, l):
        if self.line_desc[0].l == l:
            return 0
        elif self.line_desc[1].l == l:
            return 1
        elif self.line_desc[2].l == l:
            return 2
        else:
            return -1

    #---------------------------------------------------------------------------
    def GetOppositeVertex(self, base_idx):
        idx = CTriangle.opposite_vertex_idx[base_idx]
        return self.vertices[idx]

    #---------------------------------------------------------------------------
    def GetBaseLineDesc(self, idx):
        return self.line_desc[idx]

    #---------------------------------------------------------------------------
    def GetNextLineDesc(self, base_idx):
        idx = CTriangle.next_line_idx[base_idx]
        return self.line_desc[idx]

    #---------------------------------------------------------------------------
    def GetPrevLineDesc(self, base_idx):
        idx = CTriangle.prev_line_idx[base_idx]
        return self.line_desc[idx]
