################################################################################
from common import *
from PyQt4 import QtCore, QtGui

################################################################################
class CCtlIndexer:
    def __init__(self, name):
        # Default button policy
        self.button_policy = QtGui.QSizePolicy()
        self.button_policy.setHorizontalPolicy(QtGui.QSizePolicy.Minimum)
        self.button_policy.setVerticalPolicy(QtGui.QSizePolicy.Minimum)

        # Edit-box
        self.edit = QtGui.QLineEdit()

        # Decrease button
        self.decr = QtGui.QPushButton("-")
        self.decr.setSizePolicy(self.button_policy)
        self.decr.setMinimumSize(1, 1)

        # Increase button
        self.incr = QtGui.QPushButton("+")
        self.incr.setSizePolicy(self.button_policy)
        self.incr.setMinimumSize(1, 1)

        # Layout
        self.layout = QtGui.QHBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.decr)
        self.layout.addWidget(self.incr)

        # Widget
        self.widget = QtGui.QWidget()
        self.widget.setLayout(self.layout)

################################################################################
class CControls:
    #---------------------------------------------------------------------------
    def CreateUI(self):
        # Custom indexers
        self.control = [
            CCtlIndexer("mesh"),
            CCtlIndexer("trig"),
            CCtlIndexer("line"),
            CCtlIndexer("vert")]

        # Create control widget
        self.control_layout = QtGui.QVBoxLayout()

        # Add custom indexers to layout 
#        for c in self.control: 
#            self.control_layout.addWidget(c.widget)

        # Apply layout
        self.control_layout.setAlignment(QtCore.Qt.AlignTop)
        self.control_widget = QtGui.QWidget()
        self.control_widget.setLayout(self.control_layout)

    #---------------------------------------------------------------------------
    def CreateRootWidget(self, widget):
        self.root_layout = QtGui.QHBoxLayout()
        self.root_layout.addWidget(widget)
        self.root_layout.addWidget(self.control_widget)
        self.root_widget = QtGui.QWidget() 
        self.root_widget.setLayout(self.root_layout)

    #---------------------------------------------------------------------------
    def CreateWindow(self, title, width, height):
        self.wnd = QtGui.QMainWindow()
        self.wnd.setWindowTitle(title)
        self.wnd.setCentralWidget(self.root_widget)
        self.wnd.setMinimumSize(width, height)
        self.wnd.show()

    #---------------------------------------------------------------------------
    CTL_MESH = 0
    CTL_TRIG = 1
    CTL_LINE = 2
    CTL_VERT = 3
