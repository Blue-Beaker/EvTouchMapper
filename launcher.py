
import time
from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLayout,QWidgetItem,QStyle,QComboBox
)
from PyQt5 import QtCore
from PyQt5.QtCore import QSize,pyqtSignal,QThread
from PyQt5.QtGui import QRegion,QResizeEvent
import displayOverlay
import mapperOutput
import mapperWidgets
import test_widgets,sys
import evtouch_grab,os

IS_X11=False

if "XDG_SESSION_TYPE" in os.environ and os.environ["XDG_SESSION_TYPE"]=="x11":
   IS_X11=True
   
SCREEN_WIDTH=0
SCREEN_HEIGHT=0

class BackendThread(QThread):
    def __init__(self,backend:evtouch_grab.Backend):
        super().__init__()
        self.backend=backend
    def run(self):
        self.backend.loop()
    def quit(self):
        super().quit()
        self.backend.stop()
        
class OverlayThread(QThread):
    def __init__(self):
        super().__init__()
    def run(self):
        displayOverlay.initApp(evtouch_grab.widgetManager)

class LauncherWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("EvTouchMapper")
        
        self.setGeometry(0,0,200,200)
        
        layout=QVBoxLayout()
        self.button1=QPushButton("Start")
        self.button1.pressed.connect(self.launch)
        self.button2=QPushButton("Stop")
        self.button2.pressed.connect(self.stop)
        self.deviceDropDown=QComboBox()
        layout.addWidget(self.deviceDropDown)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        self.setLayout(layout)
        self.backendManager=evtouch_grab.Backend()
        self.refreshDevices()
    def refreshDevices(self):
        devices=self.backendManager.getDevices()
        self.deviceDropDown.clear()
        for device in devices:
            self.deviceDropDown.addItem(device.name+"@"+device.path,device)
            
    def launch(self):
        time.sleep(0.5)
        self.launchBackend()
        # self.launchOverlay()
    def stop(self):
        time.sleep(0.5)
        if self.backendThread:
            self.backendThread.quit()
        if self.overlay:
            self.overlay.quit()
    
    def launchBackend(self):
        mapperOutput.IS_X11=IS_X11
        if IS_X11:
            screen=self.screen()
            dpiX=self.physicalDpiX()
            dpiY=self.physicalDpiY()
            if screen:
                screenSize=screen.geometry()
                width=screenSize.width()
                height=screenSize.height()
                mapperOutput.OUTPUT_HUB.mouse.geometry.maxX=round(width*dpiX/120)
                mapperOutput.OUTPUT_HUB.mouse.geometry.maxY=round(height*dpiY/120)
                
        self.backendManager.startDevice(self.deviceDropDown.currentData())
        
        self.backendThread=BackendThread(self.backendManager)
        self.backendThread.start()
    def launchOverlay(self):
        self.overlay=OverlayThread()
        self.overlay.start()
        
def initApp():
    global app,window
    app = QApplication(sys.argv)
    app.instance()
    window = LauncherWindow()
    window.show()
    app.exec()
    
if __name__=="__main__":
    initApp()