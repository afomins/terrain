################################################################################
import math
import time

from common import *
from canvas import *

from geom_border import *
from geom_line import *
from geom_mesh import *
from geom_triangle import *
from geom_vector import * 
from geom_vertex import *

################################################################################
class CEngine(IEventHandler):
    #---------------------------------------------------------------------------
    def __init__(self):
        # Build map
        self.meshes = []

#        m = CMesh()
#        v0 = m.AddVertex(CVertex(150, 70))  # 0
#        v1 = m.AddVertex(CVertex(310, 270)) # 1
#        v2 = m.AddVertex(CVertex(130, 210)) # 2
#        v3 = m.AddVertex(CVertex(400, 30))  # 3
#        m.AddTriangle(CTriangle(v0, v1, v2), m.triangles)
#        m.AddTriangle(CTriangle(v0, v3, v1), m.triangles)
#        self.meshes.append(m)

#        m = CMesh()
#        v0 = m.AddVertex(CVertex(10, 30))    # 0
#        v1 = m.AddVertex(CVertex(100, 100))  # 1
#        v2 = m.AddVertex(CVertex(150, 65))   # 2
##        v3 = m.AddVertex(CVertex(250, 200))  # 3
#        v3 = m.AddVertex(CVertex(300, 10))  # 3
#        v4 = m.AddVertex(CVertex(30, 200))   # 4
#        m.AddTriangle(CTriangle(v0, v1, v4), m.triangles)
#        m.AddTriangle(CTriangle(v1, v2, v3), m.triangles)
#        m.AddTriangle(CTriangle(v4, v1, v3), m.triangles)
#        self.meshes.append(m)

        self.BuildGridMesh(CVertex(70, 10), CVertex(10, 8), 40)

        # Circle
        self.circle_radius = 20
        self.circle_pos = CVertex(-100, -100)

        # Finalize mesh
        for m in self.meshes:
            m.Finalize([], [])

    #---------------------------------------------------------------------------
    def BuildGridMesh(self, offset, size, dist):
        m = CMesh()
        v_ptr = []

        for y in range(size.y):
            for x in range(size.x):
                v_ptr.append(
                    m.AddVertex(CVertex(offset.x + x * dist, offset.y + y * dist)))

        for i in range((size.x - 1) * (size.y - 1)):
            row = i / (size.x - 1)
            v = [
                v_ptr[i + row], 
                v_ptr[i + row + 1], 
                v_ptr[i + row + size.x + 1], 
                v_ptr[i + row + size.x]]
            m.AddTriangle(CTriangle(v[0], v[1], v[3]), m.triangles)
            m.AddTriangle(CTriangle(v[1], v[2], v[3]), m.triangles)

        self.meshes.append(m)

    #---------------------------------------------------------------------------
    def OnRedrawEvent(self):
        # Draw meshes
        for m in self.meshes:
            m.Draw(self.circle_pos, self.circle_radius)

        # Draw circle
        glob.canvas.DrawCircle(self.circle_pos.x, self.circle_pos.y, 
            self.circle_radius)

    #---------------------------------------------------------------------------
    def OnMouseMoveEvent(self, x, y):
        if (self.circle_pos.x != x or self.circle_pos.y != y):
            self.circle_pos.x = x
            self.circle_pos.y = y
#            print "move :: x = %d | y = %d | r = %d" % (
#                self.circle_pos.x, self.circle_pos.y, self.circle_radius)
            return 1
        else:
            return 0

    #---------------------------------------------------------------------------
    def OnMousePressEvent(self):
        new_meshes = []
        old_meshes = []

        # Cut circle from meshes
        for m in self.meshes:
            t = time.clock()
            m.CutCircle(new_meshes, old_meshes, self.circle_pos, self.circle_radius)

        # Create boundary box of new meshes
        for m in new_meshes:
#            m.bounding_box.Build(m.vertices)
            m.bounding_box.BuildFromLinkedList(m.vertices)

        # Add new meshes
        self.meshes.extend(new_meshes)

        # Delete old meshes
        for m in old_meshes:
            self.meshes.remove(m)

        # Debug
        print "press :: x = %d | y = %d | r = %d" % (
            self.circle_pos.x, self.circle_pos.y, self.circle_radius)

        total_t = 0
        for m in self.meshes:
            print "m_id = %d | t = %d | b = %d | v = %d | l = %d" % (
                m.id, len(m.triangles), len(m.borders), m.vertices.GetSize(), m.lines.GetSize())
            total_t += len(m.triangles)

        print "Total triangles = %d" % (total_t)
        print "Total meshes = %d" % (len(self.meshes))
        return 1

    #---------------------------------------------------------------------------
    def OnMouseWheelEvent(self, delta):
        self.circle_radius += delta

        # Minimum
        if self.circle_radius < 8:
            self.circle_radius = 8

        # Maximum
        if self.circle_radius > 200:
            self.circle_radius = 200

        return 1
