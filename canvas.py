################################################################################
from common import *
from PyQt4 import QtCore, QtGui

################################################################################
class CCanvasPoint(QtCore.QPointF):
    pass

################################################################################
class CCanvas(QtGui.QGraphicsView):
    #---------------------------------------------------------------------------
    def __init__(self, width, height, event_handler):
        super(CCanvas, self).__init__()

        # Event handler
        self.event_handler = event_handler

        # Create scene
        self.scene = QtGui.QGraphicsScene(self)
        self.scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        self.scene.setSceneRect(0, 0, width, height)

        # Init scene
        self.setScene(self.scene)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QtGui.QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        self.scale(1.0, 1.0)

    #---------------------------------------------------------------------------
    def drawBackground(self, painter, rect):
        sceneRect = self.sceneRect()

        gradient = QtGui.QLinearGradient(
            sceneRect.topLeft(), sceneRect.bottomRight())
        gradient.setColorAt(0, QtCore.Qt.white)
        gradient.setColorAt(1, QtCore.Qt.lightGray)

        painter.fillRect(rect.intersect(sceneRect), QtGui.QBrush(gradient))
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(sceneRect)

    #---------------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        if self.event_handler.OnMouseMoveEvent(event.x(), event.y()):
            self.Refresh()

    #---------------------------------------------------------------------------
    def wheelEvent(self, event):
        if self.event_handler.OnMouseWheelEvent(event.delta() / 32):
            self.Refresh()

    #---------------------------------------------------------------------------
    def mousePressEvent(self, event):
        if self.event_handler.OnMousePressEvent():
            self.Refresh()

    #---------------------------------------------------------------------------
    def paintEvent(self, event):
        self.Clear()
        self.event_handler.OnRedrawEvent()
        super(CCanvas, self).paintEvent(event)

    #---------------------------------------------------------------------------
    def Clear(self):
        self.scene.clear()

    #---------------------------------------------------------------------------
    def Refresh(self):
        self.scene.update()

    #---------------------------------------------------------------------------
    def DrawLine(self, x0, y0, x1, y1, color = QtCore.Qt.black, width = 1):
        item = QtGui.QGraphicsLineItem(x0, y0, x1, y1)
        item.setPen(QtGui.QPen(QtGui.QColor(color), width))
        self.scene.addItem(item)

    #---------------------------------------------------------------------------
    def DrawCircle(self, x, y, radius, color = QtCore.Qt.black, width = 1):
        item = QtGui.QGraphicsEllipseItem(x - radius, y - radius,
            radius * 2, radius * 2)
        item.setPen(QtGui.QPen(QtGui.QColor(color), width))
        self.scene.addItem(item)

    #---------------------------------------------------------------------------
    def DrawPolygon(self, vertices, color = QtCore.Qt.black):
        item = QtGui.QGraphicsPolygonItem(QtGui.QPolygonF(vertices))
        item.setPen(QtGui.QPen(QtGui.QColor(color)))
        item.setBrush(QtGui.QBrush(QtGui.QColor(color), QtCore.Qt.SolidPattern))
        self.scene.addItem(item)

    #---------------------------------------------------------------------------
    COLOR_GRAY = QtCore.Qt.gray
    COLOR_LIGHT_GRAY = QtGui.QColor(210, 210, 210)
    COLOR_RED = QtCore.Qt.red
    COLOR_YELLOW = QtCore.Qt.yellow
    COLOR_BLACK = QtCore.Qt.black
    COLOR_GREEN = QtCore.Qt.green
    COLOR_BLACK = QtCore.Qt.black
    COLOR_BLUE = QtCore.Qt.blue
    COLOR_LIGHT_RED = QtGui.QColor(255, 100, 100)
