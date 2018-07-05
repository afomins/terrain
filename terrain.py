#!/usr/bin/env python

################################################################################
import time
from common import *
from PyQt4 import QtGui
from canvas import CCanvas
from gui import CControls
from engine import CEngine
import linked_list
import mem_page

################################################################################
if __name__ == '__main__':
    import sys

    # Unit tests
    linked_list.Test()
    mem_page.Test()
#    sys.exit(1)

    # App 
    app = QtGui.QApplication(sys.argv)

    # Engine
    glob.engine = CEngine()

    # Canvas
    glob.canvas = CCanvas(500, 300, glob.engine)

    # Ui
    glob.controls = CControls()
    glob.controls.CreateUI()
    glob.controls.CreateRootWidget(glob.canvas)
    glob.controls.CreateWindow("terrain", 500, 300)

    # Exit
    sys.exit(app.exec_())

