################################################################################
import math
from common import *

from geom_common import *

################################################################################
class CBspNode:
    #---------------------------------------------------------------------------
    DIV_HORIZONTAL = 0
    DIV_VERTICAL = 1

    #---------------------------------------------------------------------------
    CHILD_COUNT = 2

    #---------------------------------------------------------------------------
    def __init__(self, depth, rect):
        self.rect = rect
        self.children = []
        self.depth = depth

    #---------------------------------------------------------------------------
    def Build(self, max_depth):
        # Test whether we have reached bottom of the tree
        if self.depth == max_depth:
            return

        # Widest size of the rect gets divided
        div = CBspNode.DIV_HORIZONTAL
        if self.rect.width > self.rect.height:
            div = CBspNode.DIV_VERTICAL

        # Get size of each child
        if div == CBspNode.DIV_HORIZONTAL:
            child_size = self.rect.height / CBspNode.CHILD_COUNT
        else:
            child_size = self.rect.width / CBspNode.CHILD_COUNT

        # Create children
        for i in range(CBspNode.CHILD_COUNT):
            if div == CBspNode.DIV_VERTICAL:
                child_rect = CRect(
                    self.rect.x + i * child_size, 
                    self.rect.y, 
                    child_size, 
                    self.rect.height)
            else:
                child_rect = CRect(
                    self.rect.x, 
                    self.rect.y + i * child_size, 
                    self.rect.width,
                    child_size)

            child = CBspNode(self.depth + 1, child_rect)
            child.Build(max_depth)
            self.children.append(child)

    #---------------------------------------------------------------------------
    def Walk(self, f):
        if f(self):
            for child in self.children:
                child.Walk(f)

################################################################################
class CBspTree:

    #---------------------------------------------------------------------------
    def __init__(self, mesh, depth):
        self.mesh = mesh
        self.depth = depth

        # Build tree
        self.root = CBspNode(0, self.mesh.bounding_box.GetRect())
        self.root.Build(depth)

    #---------------------------------------------------------------------------
    def Walk(self, f):
        self.root.Walk(f)

    #---------------------------------------------------------------------------
    def Test(self, rect, dest):
        def CompareLines(l0, l1):
            len0 = l0[1] - l0[0]
            len1 = l1[1] - l1[0]
            if len0 > len1:
                l_small = len1
                l_big = len0
            elif len1 > len0:
                l_small = len0
                l_big = len1
            else:
                if len0[0] == len1[0] and len0[1] == len1[1]:
                    return 1
                else:
                    l_small = len1
                    l_big = len0

            if ((l_small[0] >= l_big[0] and l_small[0] < l_big[1]) or 
                (l_small[1] >= l_big[0] and l_small[1] < l_big[1])):
                return 1
            else:
                return 0
