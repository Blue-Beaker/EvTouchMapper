import sys,os,pywayland,ctypes
from typing import override

from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLayout,QWidgetItem,QStyle
)
from PyQt5 import QtCore
from PyQt5.QtCore import QSize,pyqtSignal,QThread
from PyQt5.QtGui import QRegion,QResizeEvent
import mapperWidgets
import test_widgets
import evtouch_grab

COLOR_ACTIVE="80B0B0B0"
COLOR_INACTIVE="808080ff"

class MapperWidget(QWidget):
    def __init__(self,widget:mapperWidgets.Widget,*args):
        super().__init__(*args)
        self.widget=widget
        self.setText(widget.name)
    def resizePos(self):
        window=self.window()
        if window:
            size=window.size()
            x=round(self.widget.x*size.width())
            y=round(self.widget.y*size.height())
            w=round(self.widget.width*size.width())
            h=round(self.widget.height*size.height())
            self.setGeometry(x,y,w,h)
            print(x,y,w,h)
            
class MapperButton(QPushButton):
    def __init__(self,widget:mapperWidgets.Button,*args):
        super().__init__(*args)
        self.widget=widget
        self.setText(widget.name)
    def resizePos(self):
        window=self.window()
        if window:
            size=window.size()
            w=round(self.widget.width*size.width())
            h=round(self.widget.height*size.height())
            x=round(self.widget.x*size.width()-w/2)
            y=round(self.widget.y*size.height()-h/2)
            self.setGeometry(x,y,w,h)
            print(x,y,w,h)
    def update(self,state:bool):
        # print(state)
        self.setStyleSheet(f'background: #{COLOR_ACTIVE if state else COLOR_INACTIVE};')
        # self.setFlat(state)
class OverlayWidgetManager():
    def __init__(self,parent:QWidget|None=None,widgetManager:mapperWidgets.WidgetManager|None=None,*args):
        super().__init__(*args)
        self.widgetManager=widgetManager
        self.parent=parent
        self.__items:list[MapperWidget]=[]
        
    def reloadWidgets(self):
        if not self.widgetManager:
            return
        for widget in self.__items:
            widget.setParent(None)
            
        for widget in self.widgetManager.getWidgets():
            # print(widget)
            wd:MapperWidget
            if isinstance(widget,mapperWidgets.Button):
                wd=MapperButton(widget)
                self.__items.append(wd)
            else:
                wd=MapperWidget(widget)
                self.__items.append(wd)
            
            if wd.update:
                # signal=QtCore.pyqtBoundSignal()
                # def update_with_signal(*args):
                #     signal.emit(*args)
                # widget.onUpdate=update_with_signal
                # signal.connect(wd.update)
                pass
                # widget.onUpdate=wd.update
                
            wd.setStyleSheet('background: #808080ff;')
            wd.setParent(self.parent)
            
    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        for widget in self.__items:
            widget.resizePos()
            
class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(QtCore.Qt.WindowType.WindowDoesNotAcceptFocus)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowTransparentForInput)
        # Doesnt work under wayland
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        
        self.setWindowFlag(QtCore.Qt.WindowType.BypassWindowManagerHint)
        self.setWindowFlag(QtCore.Qt.WindowType.X11BypassWindowManagerHint)
        
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_X11DoNotAcceptFocus)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_X11OpenGLOverlay)
        self.setWindowState(QtCore.Qt.WindowState.WindowFullScreen)
        
        self.setMask(QRegion(0,0,1,1,QRegion.RegionType.Rectangle))
        
        self.setWindowTitle("EvTouchMapper Overlay")
        self.setGeometry(0,0,1600,900)
        
        self.managerWidget = OverlayWidgetManager(self,None)
    @override
    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        self.managerWidget.resizeEvent(a0)
        
def initApp(widgetManager:mapperWidgets.WidgetManager):
    global app,window
    app = QApplication(sys.argv)
    app.instance()
    window = OverlayWindow()
    window.managerWidget.widgetManager=widgetManager
    window.managerWidget.reloadWidgets()
    window.show()
    app.exec()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.instance()
    window = OverlayWindow()
    window.managerWidget.widgetManager=test_widgets.TestWidgets()
    window.managerWidget.reloadWidgets()
    window.show()
    app.exec()