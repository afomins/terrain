################################################################################
import math
from common import *
from canvas import *

from geom_vertex import *
from geom_line import *

################################################################################
class CBorder:
    #---------------------------------------------------------------------------
    TYPE_INNER = 0
    TYPE_OUTER = 1

    #---------------------------------------------------------------------------
    cnt = 0

    #---------------------------------------------------------------------------
    def __init__(self):
        self.id = CBorder.cnt
        CBorder.cnt += 1

        self.Reset()

    #---------------------------------------------------------------------------
    def Reset(self):
        self.lines = []
        self.type = CBorder.TYPE_OUTER
        self.in_new_mesh = 0
        self.v_src = CVertex()

    #---------------------------------------------------------------------------
    def AddLine(self, l):
        self.lines.append(l)

    #---------------------------------------------------------------------------
    def GetCrossCount(self, l_src, v_src):
        # Iterate border lines and calculate how many times
        # source-line intersects border
        cross_cnt = 0
        cross_offset = 0
        for l in self.lines:
            # Don't compare with source-line
            if l == l_src:
                continue

            # Line attributes
            l_dir = l.data.dir

            # Ignore horizontal line
            if l.vector[l_dir].unit.y == 0:
                continue

            # Ignore border-line if it is located below/under source-line
            if (v_src.y < l.bounding_box.min.y or
                v_src.y > l.bounding_box.max.y):
                continue

            # Ignore border-line if it is located before source-vertex
            if v_src.x >= l.bounding_box.max.x:
                continue

            # Get vertex attributes
            v = l.GetVertices(l_dir)

            # Calculate x-coordinate of cross point
            eq = CLinearEquasion(v[0], v[1])
            if eq.a == 0:
                cross_x = v[0].x
            else:
                cross_x = (v_src.y - eq.b) / eq.a

            # Cross point should be located after source-vertex
            if cross_x <= v_src.x:
                continue

            # We've got a hit
            cross_cnt += 1

            # Handle special case when source-line crosses endpoint of the line. 
            if (v_src.y == l.bounding_box.min.y) or (v_src.y == l.bounding_box.max.y):
                if cross_offset == 0:
                    # First crossing - get offset of first vertex  in first line
                    cross_offset = SIGN(v_src.y - v[0].y)
                    ASSERT(cross_offset, "Invalid cross offset in first line")
                else:
                    # Second crossing - get offset of second vertex in second line
                    offset = SIGN(v_src.y - v[1].y)
                    ASSERT(offset, "Invalid border offset in second line")

                    # If offsets lie on the different sides from the source-line
                    # then we should ignore this crossing
                    if cross_offset != offset:
                        cross_cnt -= 1

                    # Reset crossing offset
                    cross_offset = 0

        return cross_cnt

    #---------------------------------------------------------------------------
    def GetSourceLine(self):
        # Find first non-horizontal line with normal-vector facing
        # positive x-axis
        for l in self.lines:
            l_dir = l.data.dir

            if l.vector[l_dir].unit.y == 0:
                # Line is horizontal
                continue

            if l.normal[l_dir].unit.x <= 0:
                # Normal is pointing negative x-axis
                continue

            # Found source-line
            l_src = l
            v_src = l.center
            self.v_src = v_src
            break

        return [l_src, v_src]

    #---------------------------------------------------------------------------
    def GetType(self):
        # Get source line and vertex as [line, vertex] pair
        rc = self.GetSourceLine()

        # If source line crosses border odd times then border type is INNER
        # otherwise - OUTER
        if self.GetCrossCount(rc[0], rc[1]) % 2:
            self.type = CBorder.TYPE_INNER
        else:
            self.type = CBorder.TYPE_OUTER

        return self.type

    #---------------------------------------------------------------------------
    def Draw(self, is_selected, n_len, n_col, n_width):
        if is_selected:
            default_color = CCanvas.COLOR_RED
        elif self.type == CBorder.TYPE_OUTER:
            default_color = CCanvas.COLOR_BLACK
        else:
            default_color = CCanvas.COLOR_BLUE

        # Source-line
#        glob.canvas.DrawLine(self.v_src.x, self.v_src.y, self.v_src.x + glob.INFINITE, self.v_src.y, CCanvas.COLOR_YELLOW, 2)

        for l in self.lines:
            # Line attributes
            l_dir = l.data.dir

            # Set border color
            color = default_color
            if l.data.IsCrossed():
                color = CCanvas.COLOR_RED
            else:
                color = default_color

            # Draw line
            v = l.vertices[CLine.DIR_FORW]
            glob.canvas.DrawLine(v[0].x, v[0].y, v[1].x, v[1].y, color, 2)

            # Draw normal
            if n_width:
                norm = l.GetNormal(l_dir)
                glob.canvas.DrawLine(
                    l.center.x, l.center.y,
                    l.center.x + n_len * norm.unit.x,
                    l.center.y + n_len * norm.unit.y, n_col)
