################################################################################
from common import *

################################################################################
class CMemPage:
    #---------------------------------------------------------------------------
    def __init__(self, name, constructor, size):
        # Default properties
        self.free_cnt = size
        self.name = name

        # Previous node initially does not exist
        n_prev = None

        # Pre-create nodes
        self.nodes = []
        for i in range(size):
            # Create node
            n = constructor()
            n.__mem_node_next__ = None
            n.__mem_node_idx__ = i
            n.__mem_node_is_free__ = 1
            n.__mem_page__ = self

            if i == 0:
                # Save pointer to first free node
                self.free = n
            else:
                # Link previous node with current one
                n_prev.__mem_node_next__ = n

            # Save node
            self.nodes.append(n)

            # Current node becomes previous
            n_prev = n

    #---------------------------------------------------------------------------
    def IsFull(self):
        if self.free_cnt == 0:
            return 1
        else:
            return 0

    #---------------------------------------------------------------------------
    def IsEmpty(self):
        if self.free_cnt == len(self.nodes):
            return 1
        else:
            return 0

    #---------------------------------------------------------------------------
    def GetMaxSize(self):
        return len(self.nodes)

    #---------------------------------------------------------------------------
    def GetFreeCnt(self):
        return self.free_cnt

    #---------------------------------------------------------------------------
    def GetOccupiedCnt(self):
        return self.GetMaxSize() - self.GetFreeCnt()

    #---------------------------------------------------------------------------
    def Alloc(self):
        # Make sure that page is not full
        ASSERT(self.IsFull() == 0, "No free space")

        # Pointer to free node should be valid
        ASSERT(self.free != None, "Invalid free pointer")

        # Get first free node off the page
        n = self.free
        self.free_cnt -= 1

        # Validate number of free nodes
        ASSERT(self.free_cnt >= 0 and self.free_cnt < self.GetMaxSize(), 
            "Invalid free counter")

        # Node should be free
        ASSERT(n.__mem_node_is_free__ == 1, "Node is occupied")
        n.__mem_node_is_free__ = 0

        # Select next free node
        self.free = self.free.__mem_node_next__
        return n

    #---------------------------------------------------------------------------
    def Free(self, n):
        # Make sure that node belongs to current page
        ASSERT(n.__mem_page__ == self, "Invalid mempage pointer")

        # Memory node should be occupied
        ASSERT(n.__mem_node_is_free__ == 0, "Node is free")
        n.__mem_node_is_free__ = 1

        # Node becomes first in free list
        n.__mem_node_next__ = self.free
        self.free = n
        self.free_cnt += 1

        # Validate number of free nodes
        ASSERT(self.free_cnt > 0 and self.free_cnt <= self.GetMaxSize(), 
            "Invalid free counter")

    #---------------------------------------------------------------------------
    def Check(self, log = None):
        fatal_err = 0

        if log != None:
            print "-------------------------------------------------------------"
            print "Checking memory page [name=%s] [size=%i] [free=%i] [occupied=%i]" % (
                self.name, self.GetMaxSize(), self.GetFreeCnt(), self.GetOccupiedCnt())

        # Check occupied nodes
        if log != None:
            print "Iterating occupied nodes:"

        cnt = 0
        for n in self.nodes:
            if n.__mem_node_is_free__ == 0:
                cnt += 1
                if log != None:
                    print "  [idx=%i] [desc=%s]" % (n.__mem_node_idx__, log(n))

        if log != None:
            print "Occupied nodes = %i:%i\n" % (cnt, self.GetOccupiedCnt())

        if cnt != self.GetOccupiedCnt():
            fatal_err = 1
            print "Invalid occupied node count"

        # Check free nodes
        if log != None:
            print "Iterating free nodes:"

        n = self.free
        cnt = 0
        while n != None:
            if log != None:
                print "  [idx=%i] [desc=%s]" % (n.__mem_node_idx__, log(n))

            n = n.__mem_node_next__
            cnt += 1

        if log != None:
            print "Free nodes = %i:%i\n" % (cnt, self.GetFreeCnt())

        if cnt != self.GetFreeCnt():
            fatal_err = 1
            print "Invalid free node count"

        ASSERT(fatal_err == 0, "Memory integrity error")

        if log != None:
            print "Memory is OK"

################################################################################
def Test():
    class CDummy:
        def __init__(self):
            self.a = "empty"
            self.b = -1

    m = CMemPage("Dummy", lambda: CDummy(), 7)
    dumy_log = lambda n: "<a=%s> <b=%i>" % (n.a, n.b)
    m.Check(dumy_log)

    n0 = m.Alloc()
    n1 = m.Alloc()
    n2 = m.Alloc()
    n3 = m.Alloc()
    n4 = m.Alloc()

    n0.a = "eat"
    n1.a = "my"
    n2.a = "shorts"
    n3.a = "mother"
    n4.a = "fucker"

    m.Check(dumy_log)

    m.Free(n2)

    m.Check(dumy_log)

    n5 = m.Alloc()
    n6 = m.Alloc()
    n7 = m.Alloc()

    m.Check(dumy_log)

    m.Free(n0)
    m.Free(n1)
    m.Free(n3)
    m.Free(n4)
    m.Free(n5)
    m.Free(n6)
    m.Free(n7)

    m.Check(dumy_log)
