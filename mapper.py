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



class Gesture:
    
    def __init__(self) -> None:
        pass
    # Do gestures, after the touch isn't captured by any widget
    def processGesture(self,touches:dict[int,TouchRelative],mouse:Mouse):
        activeTouches:dict[int,TouchRelative]={}
        for slot,touch in touches.items():
            if touch.pressed:
                activeTouches[slot]=touch
                
        if activeTouches.__len__()==1:
            for slot,touch in activeTouches.items():
                # print(touch2)
                mouse.moveFractional(touch)
                if touch.pressed:
                    mouse.setPressed(1)
                mouse.syn()
        else:
            mouse.setPressed(0)
            mouse.syn()
        if activeTouches.__len__()>=2:
            sums=[0.0,0.0,0]
            for slot,touch in activeTouches.items():
                sums[0]=sums[0]+touch.x
                sums[1]=sums[1]+touch.y
                sums[2]=sums[2]+1
            avgX=sums[0]/sums[2]
            avgY=sums[1]/sums[2]
            print(avgX,avgY)

class Mapper:
    geometryTouch:Geometry
    geometryOutput:Geometry=Geometry(0,16384,0,16384)
    widgetManager:mapperWidgets.WidgetManager|None=None
    gesture:Gesture|None=None
    def __init__(self):
        self.mouse = Mouse()
        self.touches:dict[int, TouchRelative]={}
        self.touchesSwitched:set[int]=set()
        self.touchesCapturedByWidget:dict[int,mapperWidgets.Widget]={}
        
    # Update self touches from new event
    def updateTouches(self,touches:dict[int, TouchInstance]):
        for slot,touch in touches.items():
            if slot in self.touches:
                if self.touches[slot].pressed != touch.pressed:
                    self.touchesSwitched.add(slot)
            self.touches[slot]=TouchRelative.fromAbsolute(touch,self.geometryTouch).flip(CONFIG.flip_x,CONFIG.flip_y,CONFIG.swap_xy)
        self.processTouchesFrame()
        # print(self.touches)
    
    # Process to send touches to a widget or the gestures
    def processTouchesFrame(self):
        sendTouches:dict[int,TouchRelative]={}
        for slot,relTouch in self.touches.items():
            # Attempt to bind newly pressed touches to a widget
            if relTouch.pressed and (slot in self.touchesSwitched):
                self.processWidgets(relTouch,slot)
            # Unbind released touches from a widget
            if ((not relTouch.pressed) 
                and (slot in self.touchesSwitched) 
                and (slot in self.touchesCapturedByWidget)):
                self.touchesCapturedByWidget[slot].onRelease(relTouch)
                self.touchesCapturedByWidget.pop(slot)
            if slot in self.touchesCapturedByWidget:
                self.touchesCapturedByWidget[slot].onTouch(relTouch)
            # Do gestures if not bind to a widget
            if slot not in self.touchesCapturedByWidget:
                sendTouches[slot]=(relTouch)
        self.processGesture(sendTouches)
        self.touchesSwitched.clear()
        
    # Check whether the touch is captured by a widget and store that widget    
    def processWidgets(self,touch:TouchRelative,slot:int):
        if self.widgetManager and isinstance(self.widgetManager,mapperWidgets.WidgetManager):
            widgets:list[mapperWidgets.Widget]=self.widgetManager.getWidgets()
            for widget in widgets:
                if widget.shouldCapture(touch):
                    self.touchesCapturedByWidget[slot]=widget
                    
    def processGesture(self,touches:dict[int,TouchRelative]):
        if len(touches)>0:
            if not self.gesture:
                self.gesture=Gesture()
            self.gesture.processGesture(touches,self.mouse)
        else:
            self.gesture=None
            