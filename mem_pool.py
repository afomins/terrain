################################################################################
from common import *
from mem_page import *
from linked_list import *

################################################################################
class CMemPool:
    #---------------------------------------------------------------------------
    OPEN_THRESHOLD = 0.85

    #---------------------------------------------------------------------------
    def __init__(self, name, constructor, size):
        # Save properties
        self.constructor = constructor
        self.size = size
        self.close_thresh = int(self.size * OPEN_THRESHOLD)

        self.pages = []
        self.open_pages = CLinkedList()
        self.closed_pages = CLinkedList()

        # Create first page
        self.AddPage()

    #---------------------------------------------------------------------------
    def AddPage(self):
        p = CMemPage(self.name, self.constructor, self.size)
        self.pages.append(p)
        self.open_pages.AppendVal(p)

    #---------------------------------------------------------------------------
    def Alloc(self):
        # Get list node
        n = self.open_pages.GetFirstNode()
        p = n.GetVal()
        ASSERT(p.IsFull() == 0, "Page is full")

        # Allocate object from page
        obj = p.Alloc()

        if p.IsFull():
            # Page is full - close it
            self.closed_pages.AppendVal(p)
            self.open_pages.Remove(n)

            if self.open_pages.IsEmpty():
                # No more open pages - create new one
                self.AddPage()

        return obj

    #---------------------------------------------------------------------------
    def Free(self, obj):
        # Get page from object
        p = obj.__mem_page__

        # Page should not be empty
        ASSERT(p.IsEmpty() != 0, "Page is empty")

        # Free object
        p.Free(obj)

        if p.GetOccupiedCnt() == self.open_thresh:
            # Open page when it open threshold
            self.closed_pages.Remove(n)
            self.open_pages.AppendVal(p)
