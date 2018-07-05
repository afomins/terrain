################################################################################
import math

from common import *
from canvas import *

from geom_vertex import *
from geom_bounding_box import *
from geom_line import *
from geom_border import *
from bsp import *
from geom_triangle import *
from linked_list import *

################################################################################
class CMesh:
    #---------------------------------------------------------------------------
    cnt = 0

    #---------------------------------------------------------------------------
    def __init__(self):
#        self.vertices = []
        self.vertices = CLinkedList()
#        self.lines = []
        self.lines = CLinkedList()
        self.triangles = []
        self.borders = []
        self.main_border = []
        self.bounding_box = CBoundingBox()
        self.ResetModificationData()
        self.is_selected = 0
        self.bsp = 0

        # Id
        self.id = CMesh.cnt
        CMesh.cnt += 1

    #---------------------------------------------------------------------------
    def ResetModificationData(self):
        self.trig_new = []
        self.trig_old = []

    #---------------------------------------------------------------------------
    def AddModificationData(self, v0, v1, v2):
        self.AddTriangle(CTriangle(v0, v1, v2), self.trig_new)

    #---------------------------------------------------------------------------
    def RemoveModificationData(self, t):
        self.trig_old.append(t)

    #---------------------------------------------------------------------------
    def ApplyModificationData(self):
        # Remove old triangles
        for t in self.trig_old:
            self.RemoveTriangle(t)

        # Add new triangles
        self.triangles.extend(self.trig_new)

        # Return code indicates whether geometry has been changed
        if (len(self.trig_new) or len(self.trig_old)):
            return 1
        else:
            return 0

    #---------------------------------------------------------------------------
    def AddVertex(self, v):
#        self.vertices.append(v)
        self.vertices.AppendVal(v)
        LOG("Vertex (%d) | pos = %d:%d" % (v.id, v.x, v.y))
        return v

    #---------------------------------------------------------------------------
    def AddLine(self, l):
#        self.lines.append(l)
        self.lines.AppendVal(l)
        LOG("Line (%d) | v = %d:%d | q = %d u = %.2f:%.2f" % (
            l.id,
            l.vertices[CLine.DIR_FORW][0].id,
            l.vertices[CLine.DIR_FORW][1].id,
            l.vector[CLine.DIR_FORW].quater,
            l.vector[CLine.DIR_FORW].unit.x,
            l.vector[CLine.DIR_FORW].unit.y))
        return l

    #---------------------------------------------------------------------------
    def GetLine(self, v0, v1):
        # Search for existing line
        it = self.lines.GetIterator()
#        for l in self.lines:
        while it.Next():
            l = it.GetVal()
            if (l.vertices[CLine.DIR_FORW][0] == v0 and
                l.vertices[CLine.DIR_FORW][1] == v1):
                return CLineDesc(l, CLine.DIR_FORW)
            elif (l.vertices[CLine.DIR_REV][0] == v0 and
                  l.vertices[CLine.DIR_REV][1] == v1):
                return CLineDesc(l, CLine.DIR_REV)

        # Line not found - create new one
        l = self.AddLine(CLine(v0, v1))
        return CLineDesc(l, CLine.DIR_FORW)

    #---------------------------------------------------------------------------
    def AddTriangle(self, t, dest):
        # Get line descriptors
        l0_desc = self.GetLine(t.vertices[0], t.vertices[1])
        l1_desc = self.GetLine(t.vertices[1], t.vertices[2])
        l2_desc = self.GetLine(t.vertices[2], t.vertices[0])

        # Set line descriptors
        t.line_desc = [l0_desc, l1_desc, l2_desc]

        # Associate line with triangle
        l0_desc.l.triangles.append(t)
        l1_desc.l.triangles.append(t)
        l2_desc.l.triangles.append(t)

        # Append triangle
        dest.append(t)
        LOG("Triangle (%d) | v = %d:%d:%d | l = %d:%d:%d | o = %d:%d:%d" % (
            t.id, t.vertices[0].id, t.vertices[1].id, t.vertices[2].id,
            l0_desc.l.id, l1_desc.l.id, l2_desc.l.id,
            l0_desc.dir, l1_desc.dir, l2_desc.dir))
        return t

    #---------------------------------------------------------------------------
    def RemoveTriangle(self, t):
        # Remove link between line <-> triangle
        for l_desc in t.line_desc:
            l_desc.l.triangles.remove(t)

        # Remove triangle from mesh
        self.triangles.remove(t)

    #---------------------------------------------------------------------------
    def Finalize(self, new_meshes, old_meshes):
        # Build new borders
        self.BuildBorder(new_meshes, old_meshes)

        # Build bounding box
        if len(self.main_border):
            self.bounding_box.BuildFromLineList(self.main_border[0].lines)

        self.bsp = CBspTree(self, 5)

    #---------------------------------------------------------------------------
    def ResetData(self):
        # Reset verted data
        def reset_vertices(i, n):
            n.val.data.Reset()
        self.vertices.Iterate(reset_vertices)

#        for v in self.vertices:
#            v.data.Reset()

        # Reset line data
        it = self.lines.GetIterator()
        while it.Next():
            l = it.GetVal()
#        for l in self.lines:
            l.data.Reset()


        # Reset triangle data
        for t in self.triangles:
            t.data.Reset()

    #---------------------------------------------------------------------------
    def GetCommonVertex(self, l0, l1):
        v0 = l0.GetVertices(CLine.DIR_FORW)
        v1 = l1.GetVertices(CLine.DIR_FORW)

        rc = CVariableVertex()
        if v0[0] == v1[0] or v0[0] == v1[1]:
            # First vertex is common
            rc.present = 1
            rc.v = v0[0]
        elif v0[1] == v1[0] or v0[1] == v1[1]:
            # Second vertex is common
            rc.present = 1
            rc.v = v0[1]
        else:
            rc.present = 0

        return rc

    #---------------------------------------------------------------------------
    def GetCrossedLineIdx(self, t, cnt):
        idx = -1
        for l_desc in t.line_desc:
            idx += 1
            if len(l_desc.l.data.circle_cross) == cnt:
                return idx

        return -1

    #---------------------------------------------------------------------------
    def GetLineDesc(self, t, idx):
        return CTriangleLineDesc(
                    t.GetBaseLineDesc(idx),
                    t.GetNextLineDesc(idx),
                    t.GetPrevLineDesc(idx))

    #---------------------------------------------------------------------------
    def GetCrossVertex(self, v00, v01, v10, v11):
        # Get linear equasion of each line
        eq0 = CLinearEquasion(v00, v01)
        eq1 = CLinearEquasion(v10, v11)

        # Default values
        is_crossed = 1
        cross = CVertex()

        # Find cross point
        if eq0.a == eq1.a:
            # Both lines are parallel
            is_crossed = 0
        elif (eq0.is_vertical == 0 and eq1.is_vertical == 0):
            # Both lines are not vertical
            cross.x = (eq1.b - eq0.b) / (eq0.a - eq1.a)
            cross.y = eq0.a * cross.x + eq0.b
        elif (eq0.is_vertical == 1 and eq1.is_vertical == 0):
            # First line is vertical
            cross.x = v00.x
            cross.y = eq1.a * cross.x + eq1.b
        elif (eq0.is_vertical == 0 and eq1.is_vertical == 1):
            # Second line is vertical
            cross.x = v10.x
            cross.y = eq0.a * cross.x + eq0.b
        else:
            # Both lines are vertical
            is_crossed = 0

        # Check whether cross point lies within bounding box of both lines
        if is_crossed:
            box0 = CBoundingBox([v00, v01])
            box1 = CBoundingBox([v10, v11])

            if box0.Test(cross) == 0 or box1.Test(cross) == 0:
                is_crossed = 0

        return CVariableVertex(is_crossed, cross)

    #---------------------------------------------------------------------------
    def AddNewVertex(self, l, v_new):
        if len(l.data.new_vertices):
            # New vertex is already present
            v = l.data.new_vertices[0]
        else:
            # Create new vertex
            v = self.AddVertex(CVertex(v_new.x, v_new.y))
            l.data.new_vertices.append(v)

        return v

    #---------------------------------------------------------------------------
    def BuildCircleCrossData(self, center = CVertex(), radius = 0):
        # Reset geometry
        self.ResetData()

        # Flag that indicates whether circle was inside triangle
        was_inside = 0

        # Iterate all triangles
        for t in self.triangles:
            # Do this only if we have circle
            if radius != 0:
                # Circle can be inside the triangle only once
                t.data.is_inside = not was_inside

                # Assume that circle absorbes the triangle
                t.data.is_outside = 1

                # Assume that initially center is located inside the triangle
                center_inside_triangle = 1

            # Iterate all lines
            for l_desc in t.line_desc:
                l = l_desc.l
                l_dir = l_desc.dir
                l_vect = l.GetVector(l_dir)

                # Ignore zero-length vectors
                if l_vect.len == 0:
                    continue

                # Zero-radius means that there are no cross-point
                if radius == 0:
                    if l.data.dir == CLine.DIR_NONE:
                        l.data.dir = l_dir
                    else:
                        l.data.dir = CLine.DIR_BOTH
                    continue

                # Process line only once
                if l.data.dir == CLine.DIR_NONE:
                    # This line has not been processed yet
                    l.data.dir = l_dir

                    # Get line attributes
                    v = l.GetVertices(l_dir)

                    # Get vectors from circle-center to line vertices
                    a = CVector(center, v[0])
                    b = CVector(center, v[1])

                    # Get cross-center
                    c = l_vect
                    e = (SQR(a.len) - SQR(b.len) + SQR(c.len)) / (2 * c.len)
                    l.data.cross = CVertex(
                        v[0].x + e * l_vect.unit.x,
                        v[0].y + e * l_vect.unit.y)

                    # Save distance from circle-center to first-vertex
                    if l_dir == CLine.DIR_FORW:
                        l.data.first = a
                    else:
                        l.data.first = b

                    # Find crossing points and save them
                    l.data.perpendicular = CVector(center, l.data.cross)
                    if l.data.perpendicular.len < radius:
                        # Get offset of cross-points
                        f = math.sqrt(SQR(radius) - SQR(l.data.perpendicular.len))

                        # There're 2 cross points which lie on
                        # opposite sides from cross-center
                        sign = [-1, 1]
                        for i in sign:
                            # Position of cross-point
                            cross = CVertex(
                                l.data.cross.x + i * f * l_vect.unit.x,
                                l.data.cross.y + i * f * l_vect.unit.y)

                            # Check whether cross-point lies within the line
                            # boundaries
                            if l.bounding_box.Test(cross):
                                if len(l.data.circle_cross) == 0:
                                    # Add first cross-point
                                    l.data.AddCross(cross, 1)
                                else:
                                    # Mind the gap :)
                                    l.data.AddCross(cross, l_dir)

                                    # Calculate vertex that lies between two
                                    # cross-points i.e. the middle-vertex
                                    l.data.middle = CVertex(
                                        (l.data.circle_cross[0].x + l.data.circle_cross[1].x) / 2,
                                        (l.data.circle_cross[0].y + l.data.circle_cross[1].y) / 2)

                else:
                    # Line has already been proceed in another triangle
                    l.data.dir = CLine.DIR_BOTH

                # If quater of perpendicular is equal to quater of line-normal
                # then circle-center is inside the triangle
                if t.data.is_inside:
                    l_norm = l.GetNormal(l_dir)
                    if not l.data.perpendicular.TestQuater(l_norm):
                        t.data.is_inside = 0
                        center_inside_triangle = 0

                # If radius is greater than vector from circle-center to all
                # vertices, then circle absorbes the triangle
                if t.data.is_outside:
                    if l.data.first.len > radius:
                        t.data.is_outside = 0

            # Zero-radius means that there are no cross points
            if radius == 0:
                continue

            # Circle center is inside the mesh
            if center_inside_triangle:
                self.is_selected = 1

            # Build array with all cross-points
            cross_cnt = []
            total_cross_cnt = 0
            for desc in t.line_desc:
                cnt = len(desc.l.data.circle_cross)
                cross_cnt.append(cnt)
                total_cross_cnt = total_cross_cnt + cnt

            # Handle cross-type
            type = CTriangle.CROSS_TYPE_NONE
            if total_cross_cnt == 0:
                if t.data.is_outside:
                    type = CTriangle.CROSS_TYPE_ABSORB
                elif t.data.is_inside:
                    type = CTriangle.CROSS_TYPE_HOLE
                    was_inside = 1

            elif (TEST_ARRAYS(cross_cnt, [0, 1, 1])):
                type = CTriangle.CROSS_TYPE_NORMAL

            elif (TEST_ARRAYS(cross_cnt, [2, 0, 0])):
                type = CTriangle.CROSS_TYPE1

            elif (TEST_ARRAYS(cross_cnt, [2, 1, 1])):
                type = CTriangle.CROSS_TYPE2

            elif (TEST_ARRAYS(cross_cnt, [0, 2, 2])):
                type = CTriangle.CROSS_TYPE3

            elif (TEST_ARRAYS(cross_cnt, [2, 2, 2])):
                type = CTriangle.CROSS_TYPE4
            else:
                # This is a rare situation when circle goes through one or many 
                # vertices of triangle. Simply assume that there are no
                # cross-points, otherwise we would have to create tons of tiny
                # triangles that would lead to performance drop. 
                self.ResetData()
                break

            # Save cross type
            t.data.cross_type = type

    #---------------------------------------------------------------------------
    def NormalizeTrianglesType12(self, t):
        # Get index of base-line which has 2 cross points
        idx = self.GetCrossedLineIdx(t, 2)
        ASSERT(idx != -1, "No base-line")

        # Get line descriptors
        desc = self.GetLineDesc(t, idx)

        # Get vertices of base-line
        v = desc.base.l.GetVertices(desc.base.dir)

        # Get vertex that is opposite to base-line
        v_opp = t.GetOppositeVertex(idx)

        # Get new vertex
        v_new = self.AddNewVertex(desc.base.l, desc.base.l.data.middle)

        # Create normalized triangles
        self.AddModificationData(v[1], v_opp, v_new)
        self.AddModificationData(v_new, v_opp, v[0])

        return 1

    #---------------------------------------------------------------------------
    def NormalizeTrianglesType34(self, t):
        # Get base-line
        type = t.data.cross_type
        if (type == CTriangle.CROSS_TYPE3):
            # Base-line should not be crossed by circle
            idx = self.GetCrossedLineIdx(t, 0)
            ASSERT(idx != -1, "No base-line")
        else:
            # Assume that first line is base-line
            idx = 0

        # Get line descriptors
        desc = self.GetLineDesc(t, idx)

        # Get vertices of base-line
        v = desc.base.l.GetVertices(desc.base.dir)

        # Get vertex that is opposite to base-line
        v_opp = t.GetOppositeVertex(idx)

        # Get vertices where circle intersects triangle
        v_next_cross = desc.next.l.data.GetCross(desc.next.dir)
        v_prev_cross = desc.prev.l.data.GetCross(desc.prev.dir)

        # Get middle vertices
        v_prev = self.AddNewVertex(desc.prev.l, desc.prev.l.data.middle)
        v_next = self.AddNewVertex(desc.next.l, desc.next.l.data.middle)

        # Get crosspoint between 2 lines
        rc = self.GetCrossVertex(
            v_prev_cross[0], v_next_cross[0],
            v_prev_cross[1], v_next_cross[1])
        if not rc.present:
            ASSERT(0, "No cross point :: type = %d" % type, 0)
            return 0

        # Add center-vertex to mesh
        v_cent = self.AddVertex(rc.v)

        # Create triangles that are common in both TYPE3 & TYPE4
        self.AddModificationData(v_cent, v_opp, v_prev)
        self.AddModificationData(v_cent, v_prev, v[0])
        self.AddModificationData(v_cent, v[1], v_next)
        self.AddModificationData(v_cent, v_next, v_opp)

        # Create normalized triangles
        if type == CTriangle.CROSS_TYPE3:
            self.AddModificationData(v_cent, v[0], v[1])
        else:
            v_base = self.AddNewVertex(desc.base.l, desc.base.l.data.middle)
            self.AddModificationData(v_cent, v[0], v_base)
            self.AddModificationData(v_cent, v_base, v[1])

        return 1

    #---------------------------------------------------------------------------
    def NormalizeTrianglesTypeHole(self, t, center):
        # Add center vertex
        v_cent = self.AddVertex(CVertex(center.x, center.y))

        # Divide current triangle into 3 smaller ones with one common vertex
        # in the middle
        for idx in range(3):
            # Get base-line descriptor
            desc = t.GetBaseLineDesc(idx)

            # Get vertices of base-line
            v = desc.l.GetVertices(desc.dir)

            # Create normalized triangle
            self.AddModificationData(v_cent, v[0], v[1])

        return 1

    #---------------------------------------------------------------------------
    def NormalizeTriangles(self, center, radius):
        # Pre-process geometry
        self.BuildCircleCrossData(center, radius)
        self.ResetModificationData()

        # Iterate triangles
        for t in self.triangles:
            type = t.data.cross_type
            if (type == CTriangle.CROSS_TYPE_NONE or
                type == CTriangle.CROSS_TYPE_NORMAL):
                # Triangle is either not crossed at all or
                # it is already normalized - nothing to do
                rc = 0

            elif (type == CTriangle.CROSS_TYPE1 or
                  type == CTriangle.CROSS_TYPE2):
                rc = self.NormalizeTrianglesType12(t)

            elif (type == CTriangle.CROSS_TYPE3 or
                  type == CTriangle.CROSS_TYPE4):
                rc = self.NormalizeTrianglesType34(t)

            elif type == CTriangle.CROSS_TYPE_HOLE:
                rc = self.NormalizeTrianglesTypeHole(t, center)

            elif type == CTriangle.CROSS_TYPE_ABSORB:
                # Delete old triangle
                rc = 1

            else:
                ASSERT(0, "Invalid cross type :: %d" % type)

            # Kill current triangle
            if rc:
                self.RemoveModificationData(t)

        return self.ApplyModificationData()

    #---------------------------------------------------------------------------
    def CutCircle(self, new_meshes, old_meshes, center, radius):
        # Pre-process geometry
        modified = self.NormalizeTriangles(center, radius)
        self.BuildCircleCrossData(center, radius)
        self.ResetModificationData()

        # Do the monkey business
        for t in self.triangles:
            # Validate cross type
            type = t.data.cross_type
            if type != CTriangle.CROSS_TYPE_NORMAL:
                ASSERT(type == CTriangle.CROSS_TYPE_NONE,
                    "Unexpected cross type %d" % type, 0)
                continue

            # Put current triangle to delete-list
            self.RemoveModificationData(t)

            # Base-line should not be crossed by circle
            idx = self.GetCrossedLineIdx(t, 0)
            ASSERT(idx != -1, "Base-line not found")

            # Get line descriptors
            desc = self.GetLineDesc(t, idx)

            # Get vertices of base-line
            v = desc.base.l.GetVertices(desc.base.dir)

            # Get new vertices
            v_prev = self.AddNewVertex(desc.prev.l, desc.prev.l.data.circle_cross[0])
            v_next = self.AddNewVertex(desc.next.l, desc.next.l.data.circle_cross[0])

            # Build vector: common-vertex -> circle-center
            common = self.GetCommonVertex(desc.prev.l, desc.next.l)
            ASSERT(common.present, "No common vertex")
            vect_common = CVector(common.v, center)

            # Figure out which part to cut out: inner or outer
            if vect_common.len < radius:
                # Common vertex is outside the circle - cut inner part
                self.AddModificationData(v[0], v[1], v_prev)
                self.AddModificationData(v[1], v_next, v_prev)
            else:
                # Common vertex is inside the circle - cut outer part
                self.AddModificationData(v_prev, v_next, common.v)

        # If mesh was modified then we need to finalize it
        modified = modified | self.ApplyModificationData()
        if modified:
            self.Finalize(new_meshes, old_meshes)
            return 1
        else:
            return 0

    #---------------------------------------------------------------------------
    def BuildBorderCandidates(self):
        candidates = []
        it = self.lines.GetIterator()
        while it.Next():
            l = it.GetVal()
            l_dir = l.data.dir
            if l_dir == CLine.DIR_FORW or l_dir == CLine.DIR_REV:
                candidates.append(l)

#        LOG("Border candidates :: %d/%d" % (len(candidates), len(self.lines)))
        return candidates

    #---------------------------------------------------------------------------
    def ParseBorderCandidates(self, candidate):
        # Reset borders
        self.borders = []
        cur_border = CBorder()
        found_first = 0; idx = 0
        while len(candidate):
            # Line attributes
            l = candidate[idx]
            l_dir = l.data.dir
            v = l.GetVertices(l_dir)

            if not found_first:
                # Found first border line
                found_first = 1
                first = v[0]
                v_next = v[1]
                cur_border.AddLine(candidate.pop(idx))
                idx = 0

            elif v[0] == v_next:
                # Found next border line
                v_next = v[1]
                cur_border.AddLine(candidate.pop(idx))
                idx = 0

                if v_next == first:
                    # Found last border line
                    self.borders.append(cur_border)
                    cur_border = CBorder()
                    found_first = 0
            else:
                idx += 1

            if (idx > 0 and idx >= len(candidate)):
                ASSERT(0, "Candidate list overflow", 0)
                break

        LOG("Borders :: %d" % (len(self.borders)))

    #---------------------------------------------------------------------------
    def FinalizeBorders(self):
        # Handle special cases when there's none/one border
        cnt = len(self.borders)
        if cnt == 0:
            return 0

        elif cnt == 1:
            # If mesh contains one border then it is always OUTER
            self.borders[0].type = CBorder.TYPE_OUTER
            return 1

        # Calculate how many OUTER borders exist
        outer_cnt = 0
        for b in self.borders:
            if b.GetType() == CBorder.TYPE_OUTER:
                outer_cnt += 1

        return outer_cnt

    #---------------------------------------------------------------------------
    def DivideMesh(self, new_meshes):
        # Create list of all INNER borders
        inner_borders = []
        for b in self.borders:
            if b.type == CBorder.TYPE_INNER:
                inner_borders.append(b)

        # Create mesh for each OUTER border
        is_first = 1
        for b in self.borders:
            # Ignore INNER border
            if b.type == CBorder.TYPE_INNER:
                continue

            # Ignore first OUTER border - it should stay in the same mesh
            if is_first:
                is_first = 0

                # First OUTER border becomes main border
                self.main_border.append(b)
                continue

            # Create new mesh
            m = CMesh()
            new_meshes.append(m)

            # Push first triangle of the first line into the stack
            t = b.lines[0].triangles[0]
            stack = [t]

            # Walk all triangles inside outer-border and move them to new mesh
            while(len(stack)):
                # Remove triangle from stack
                t = stack.pop()

                # Add current triangle to new mesh
                m.triangles.append(t)
                t.data.in_new_mesh = 1

                # Get list of neighbor triangles
                neighbors = [t.line_desc[0].l.GetAdjacentTriangle(t),
                             t.line_desc[1].l.GetAdjacentTriangle(t),
                             t.line_desc[2].l.GetAdjacentTriangle(t)]

                # Push neighbor triangles to stack
                for n in neighbors:
                    # Check whether neighbor triangle exists
                    is_present = n[0]
                    if not is_present:
                        continue

                    # Ignore if neighbor-triangle is already in new mesh
                    t = n[1]
                    if (t.data.in_new_mesh or t.data.in_move_stack):
                        continue

                    # Push triangle to stack
                    stack.append(t)
                    t.data.in_move_stack = 1

            # Move triangles/lines/vertices from old mesh to new mesh
            for t in m.triangles:
                # Remove triangle from old mesh
                self.triangles.remove(t)

                # Iterate lines
                for desc in t.line_desc:
                    # Ignore if line is already moved
                    l = desc.l
                    if l.data.in_new_mesh:
                        continue

                    # Add matching inner borders to new mesh
                    for ib in inner_borders:
                        # Check whether line belongs to inner border
                        if l == ib.lines[0]:
                            m.borders.append(ib)
                            inner_borders.remove(ib)
                            break

                    # Add line to new mesh
                    l.data.in_new_mesh = 1
#                    m.lines.append(l)
                    m.lines.AppendVal(l)

                    # Remove line from old mesh
#                    self.lines.remove(l)
                    self.lines.RemoveVal(l)

                    # Iterate vertices
                    for v in l.vertices[CLine.DIR_FORW]:
                        if v.data.in_new_mesh:
                            continue

                        # Add vertex to new mesh
                        v.data.in_new_mesh = 1
#                        m.vertices.append(v)
                        m.vertices.AppendVal(v)

                        # Remove vertex from old mesh
#                        self.vertices.remove(v)
                        self.vertices.RemoveVal(v)

            # Add border to new mesh
            m.borders.append(b)

        # Remove borders which no longer belong to current mesh
        for m in new_meshes:
            for b in m.borders:
                self.borders.remove(b)

    #---------------------------------------------------------------------------
    def BuildBorder(self, new_meshes, old_meshes):
        self.main_border = []

        # Pre-process mesh geometry
        self.BuildCircleCrossData()

        # Build border candidates and parse them
        candidates = self.BuildBorderCandidates()
        self.ParseBorderCandidates(candidates)

        # Finalize border
        outer_cnt = self.FinalizeBorders()

        if outer_cnt == 1:
            # First and only border becomes main
            self.main_border.append(self.borders[0])
        elif outer_cnt > 1:
            # Multiple borders might indicate that mesh is divided in parts, if
            # so then we need to create separate mesh object for each part
            self.DivideMesh(new_meshes)
        else:
            # No borders indicate that current mesh must be deleted
            old_meshes.append(self)

    #---------------------------------------------------------------------------
    def DrawBorders(self, is_selected, n_len = 5, n_col = CCanvas.COLOR_GREEN, n_width = 1):
        for b in self.borders:
            b.Draw(is_selected, n_len, n_col, n_width)

    #---------------------------------------------------------------------------
    def DrawWireframe(self, center, radius):
        # Get current crossing data
        self.is_selected = 0
        self.BuildCircleCrossData(center, radius)

        # Draw lines
        it = self.lines.GetIterator()
        while it.Next():
            l = it.GetVal()
#        for l in self.lines:
            # Line attributes
            l_dir = l.data.dir
            if l_dir == CLine.DIR_NONE:
                continue

            # Draw crossing
            for cross in l.data.circle_cross:
                glob.canvas.DrawCircle(cross.x, cross.y, 2)

            # Color
            if l.data.IsCrossed():
                color = CCanvas.COLOR_LIGHT_RED
            else:
                color = CCanvas.COLOR_LIGHT_GRAY

            # Draw line
            v = l.vertices[CLine.DIR_FORW]
            glob.canvas.DrawLine(v[0].x, v[0].y, v[1].x, v[1].y, color, 1)

    #---------------------------------------------------------------------------
    def DrawBsp(self, lvl):
        def DrawBspNode(n):
            if n.depth == lvl:
                color = CCanvas.COLOR_GREEN
                x = n.rect.x
                y = n.rect.y
                w = n.rect.width
                h = n.rect.height

                glob.canvas.DrawLine(x, y, x + w, y, color, 1)
                glob.canvas.DrawLine(x + w, y, x + w, y + h, color, 1)
                glob.canvas.DrawLine(x + w, y + h, x, y + h, color, 1)
                glob.canvas.DrawLine(x, y + h, x, y, color, 1)
            elif n.depth > lvl:
                return 0
            return 1

        self.bsp.Walk(DrawBspNode)

    #---------------------------------------------------------------------------
    def DrawSolid(self):
#        if self.is_selected == 0:
#            return

        for t in self.triangles:
#            if not t.data.in_new_mesh:
#                continue
            glob.canvas.DrawPolygon([
                CCanvasPoint(t.vertices[0].x, t.vertices[0].y),
                CCanvasPoint(t.vertices[1].x, t.vertices[1].y),
                CCanvasPoint(t.vertices[2].x, t.vertices[2].y)],
                CCanvas.COLOR_GREEN)

    #---------------------------------------------------------------------------
    def Draw(self, center, radius):
#        self.DrawSolid()
        self.DrawWireframe(center, radius)
#        self.DrawBorders(self.is_selected)
        self.DrawBorders(0)
        self.bounding_box.Draw()

#        self.DrawBsp(5)
