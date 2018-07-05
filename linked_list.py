################################################################################
from common import *

################################################################################
class CLinkedListNode:
    #---------------------------------------------------------------------------
    def __init__(self, val = None, next = None, prev = None):
        self.val = val
        self.next = next
        self.prev = prev

    #---------------------------------------------------------------------------
    def IsLast(self):
        if self.next == None:
            return 1
        else:
            return 0

    #---------------------------------------------------------------------------
    def IsFirst(self):
        if self.prev == None:
            return 1
        else:
            return 0

    #---------------------------------------------------------------------------
    def GetNext(self):
        return self.next

    #---------------------------------------------------------------------------
    def GetPrev(self):
        return self.prev

    #---------------------------------------------------------------------------
    def GetVal(self):
        return self.val

################################################################################
class CLinkedListIterator:
    #---------------------------------------------------------------------------
    def __init__(self, n):
        self.idx = 0
        self.base = n
        self.n = None

    #---------------------------------------------------------------------------
    def Next(self):
        if self.base == None:
            # No base node
            return 0

        if self.n == None:
            # Select first node
            self.idx = 0
            self.n = self.base
            return 1

        if self.n.IsLast():
            # Last node on the list
            return 0

        # Select next node
        self.idx += 1
        self.n = self.n.GetNext()
        return 1

    #---------------------------------------------------------------------------
    def Prev(self):
        if self.base == None:
            # No base node
            return 0

        if self.n == None:
            # Select first node
            self.idx = 0
            self.n = self.base
            return 1

        if self.n.IsFirst():
            # First node on the list
            return 0

        # Select prev node
        self.idx -= 1
        self.n = self.n.GetPrev()
        return 1

    #---------------------------------------------------------------------------
    def GetIdx(self):
        return self.idx

    #---------------------------------------------------------------------------
    def GetVal(self):
        ASSERT(self.n != None, "Invalid node")
        return self.n.val

################################################################################
class CLinkedList:
    #---------------------------------------------------------------------------
    def __init__(self):
        self.first = None
        self.last = None
        self.size = 0

    #---------------------------------------------------------------------------
    def GetFirstNode(self):
        return self.first

    #---------------------------------------------------------------------------
    def GetSize(self):
        return self.size

    #---------------------------------------------------------------------------
    def GetNodeByIdx(self, idx):
        ASSERT(idx >= 0 and idx < self.size, "Invalid index")

        i = 0
        n = self.first
        while i != idx:
            n = n.next
            i += 1

        return n

    #---------------------------------------------------------------------------
    def GetNodeByVal(self, val):
        n = self.first
        while n.val != val:
            n = n.next

        return n

    #---------------------------------------------------------------------------
    def GetValByIdx(self, idx):
        return self.GetNodeByIdx(idx).val

    #---------------------------------------------------------------------------
    def AppendVal(self, val):
        n = CLinkedListNode(val)
        self.Append(n)
        return n

    #---------------------------------------------------------------------------
    def Append(self, n):
        n.next = None
        n.prev = self.last

        if self.size == 0:
            # List is empty

            # Validate first/last pointers
            ASSERT(self.first == None, "Invalid first pointer")
            ASSERT(self.last == None, "Invalid last pointer")

            # Append first node to list
            self.first = n
            self.last = n
        else:
            # List is not empty

            # Validate first/last pointers
            ASSERT(self.first != None, "Invalid first pointer")
            ASSERT(self.last != None, "Invalid last pointer")

            # Append node to the end of the list
            self.last.next = n
            self.last = n

        # Increment node counter
        self.size += 1
        ASSERT(self.size > 0, "Invalid node counter")

    #---------------------------------------------------------------------------
    def RemoveVal(self, val):
        n = self.GetNodeByVal(val)
        ASSERT(n != None, "Value not found")
        self.Remove(n)

    #---------------------------------------------------------------------------
    def Remove(self, n):
        if self.size == 1:
            # Remove last element from list

            # Node should be first/last in the list
            ASSERT(self.first == self.last == n, "Invalid node pointer")

            # Remove first/last pointers
            self.first = None
            self.last = None
        else:
            # Remove node from the middle of the list

            # List should not be empty
            ASSERT(self.size != 0, "List is empty")

            if self.first == n:
                # Remove first node from the list

                # Second node becomes first
                self.first = n.next
                n.next.prev = None

            elif self.last == n:
                # Remove node from the end of the list

                # Pre-last node becomes last
                self.last = n.prev
                n.prev.next = None

            else:
                # Remove node somewhere from the middle of the list
                n.prev.next = n.next
                n.next.prev = n.prev

        # Clear next/prev node pointers
        n.next = None
        n.prev = None

        # Decrement node counter
        self.size -= 1
        ASSERT(self.size >= 0, "Invalid node counter")

    #---------------------------------------------------------------------------
    def Clear(self):
        if self.size == 0:
            # List should be empty

            # Validate first/last pointers
            ASSERT(self.first == None, "Invalid first pointer")
            ASSERT(self.last == None, "Invalid last pointer")
        else:
            # List should not be empty

            # Validate first/last pointers
            ASSERT(self.first != None, "Invalid first pointer")
            ASSERT(self.last != None, "Invalid last pointer")

            # Iterate list and remove links from each node
            n = self.first
            while n != None:
                next = n.next
                n.next = None
                n.prev = None
                n = next
                self.size -= 1

            # Clear first/last pointer
            self.first = None
            self.last = None

            # Size of list shoul be 0
            ASSERT(self.size == 0, "Invalid list size")

    #---------------------------------------------------------------------------
    def Iterate(self, f):
        i = 0
        n = self.first
        while n != None:
            if f(i, n) == 0:
                break
            n = n.next
            i += 1

    #---------------------------------------------------------------------------
    def GetIterator(self):
        return CLinkedListIterator(self.first)

################################################################################
def Test():
    l = CLinkedList()

    n0 = l.AppendVal("eat")
    n1 = l.AppendVal("my")
    n2 = l.AppendVal("shorts")

    ASSERT(l.size == 3, "Invalid size")

    n = l.first
    while n != None:
        print n.val
        n = n.next

    def DumpList(i, n):
        print "%i - %s" % (i, n.val),
        if n.IsFirst():
            print "<First>",
        if n.IsLast():
            print "<Last>",
        print ""

    l.Iterate(DumpList)

    l.Remove(n1)
    l.Iterate(DumpList)
    ASSERT(l.size == 2, "Invalid size")

    l.Clear()
    l.Iterate(DumpList)
    ASSERT(l.size == 0, "Invalid size")
