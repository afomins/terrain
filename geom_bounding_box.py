################################################################################
import math

from common import *
from canvas import *

from geom_vertex import *
from geom_common import *

################################################################################
class CBoundingBox:
    #---------------------------------------------------------------------------
    def __init__(self, v_list = []):
        self.Build(v_list)

    #---------------------------------------------------------------------------
    def Build(self, v_list):
        if len(v_list):
            # Set initial coordinates
            self.Reset()

            # Set min/max coordinates
            for v in v_list:
                if self.min.x > v.x: self.min.x = v.x # min
                if self.min.y > v.y: self.min.y = v.y

                if self.max.x < v.x: self.max.x = v.x # max
                if self.max.y < v.y: self.max.y = v.y
        else:
            self.min = CVertex()
            self.max = CVertex()

        self.width = self.max.x - self.min.x
        self.height = self.max.y - self.min.y

    #---------------------------------------------------------------------------
    def BuildFromLinkedList(self, l):
        if l.GetSize():
            # Set initial coordinates
            self.Reset()

            # Set min/max coordinates
            def set_min_max_coord(i, n):
                v = n.val

                if self.min.x > v.x: self.min.x = v.x # min
                if self.min.y > v.y: self.min.y = v.y

                if self.max.x < v.x: self.max.x = v.x # max
                if self.max.y < v.y: self.max.y = v.y

            l.Iterate(set_min_max_coord)
        else:
            self.min = CVertex()
            self.max = CVertex()

        self.width = self.max.x - self.min.x
        self.height = self.max.y - self.min.y

    #---------------------------------------------------------------------------
    def BuildFromLineList(self, l_list):
        if len(l_list):
            # Set initial coordinates
            self.Reset()

            # Set min/max coordinates
            for l in l_list:
                b = l.bounding_box
                if self.min.x > b.min.x: self.min.x = b.min.x # min
                if self.min.y > b.min.y: self.min.y = b.min.y

                if self.max.x < b.max.x: self.max.x = b.max.x # max
                if self.max.y < b.max.y: self.max.y = b.max.y
        else:
            self.min = CVertex()
            self.max = CVertex()

    #---------------------------------------------------------------------------
    def Reset(self):
        self.min = CVertex(+glob.INFINITE, +glob.INFINITE)
        self.max = CVertex(-glob.INFINITE, -glob.INFINITE)

    #---------------------------------------------------------------------------
    def Test(self, v):
        coord = [   [self.min.x, self.max.x, v.x],
                    [self.min.y, self.max.y, v.y] ]

        for c in coord:
            min = c[0]; max = c[1]; src = c[2]
            if min == max:
                if max != src:
                    return 0
            else:
                if src >= min and src < max:
                    pass
                else:
                    return 0

        return 1
    #---------------------------------------------------------------------------
    def GetRect(self):
        return CRect(
              self.min.x, 
              self.min.y, 
              self.max.x - self.min.x, 
              self.max.y - self.min.y)

    #---------------------------------------------------------------------------
    def Draw(self, color = CCanvas.COLOR_GRAY):
        glob.canvas.DrawLine(self.min.x, self.min.y, self.max.x, self.min.y, color)
        glob.canvas.DrawLine(self.max.x, self.min.y, self.max.x, self.max.y, color)
        glob.canvas.DrawLine(self.max.x, self.max.y, self.min.x, self.max.y, color)
        glob.canvas.DrawLine(self.min.x, self.max.y, self.min.x, self.min.y, color)
