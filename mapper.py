import math
import time
import evdev.uinput
from geometryHelper import TouchInstance,TouchRelative,Geometry
import mapperWidgets
from touchinstance import TouchInstance
import evdev
from evdev import ecodes as ec

from touchmapper_config import CONFIG
from mapperOutput import Mouse



# ui_mouse = evdev.UInput(capabs,name='mapper-mouse')
class Mapper:
    geometryTouch:Geometry
    geometryOutput:Geometry=Geometry(0,16384,0,16384)
    widgetManager:mapperWidgets.WidgetManager|None=None
    touches:dict[int, TouchRelative]={}
    
    def __init__(self):
        self.mouse = Mouse()
        self.touches:dict[int, TouchRelative]={}
        
    def updateTouches(self,touches:dict[int, TouchInstance]):
        for slot,touch in touches.items():
            self.touches[slot]=TouchRelative.fromAbsolute(touch,self.geometryTouch).flip(CONFIG.flip_x,CONFIG.flip_y,CONFIG.swap_xy)
        self.processTouchesFrame()
        print(self.touches)
        
    def processTouchesFrame(self):
        sendTouches:dict[int,TouchRelative]={}
        for slot,touchRel in self.touches.items():
            if not self.processWidgets(touchRel):
                sendTouches[slot]=(touchRel)
        self.processGesture(sendTouches)
        
    def processWidgets(self,touch:TouchRelative):
        if self.widgetManager and isinstance(self.widgetManager,mapperWidgets.WidgetManager):
            widgets:list[mapperWidgets.Widget]=self.widgetManager.getWidgets()
            for widget in widgets:
                if widget.isInWidget(touch):
                    return True
    
    def processGesture(self,touches:dict[int,TouchRelative]):
        activeTouches:dict[int,TouchRelative]={}
        for slot,touch in touches.items():
            if touch.pressed:
                activeTouches[slot]=touch
                
        if activeTouches.__len__()==1:
            for slot,touch in activeTouches.items():
                # print(touch2)
                self.mouse.moveFractional(touch)
                if touch.pressed:
                    self.mouse.setPressed(1)
                self.mouse.syn()
        else:
            self.mouse.setPressed(0)
            self.mouse.syn()
        if activeTouches.__len__()>=2:
            sums=[0.0,0.0,0]
            for slot,touch in activeTouches.items():
                sums[0]=sums[0]+touch.x
                sums[1]=sums[1]+touch.y
                sums[2]=sums[2]+1
            avgX=sums[0]/sums[2]
            avgY=sums[1]/sums[2]
            print(avgX,avgY)