import math
import time
import evdev.uinput
from geometryHelper import TouchInstance,TouchRelative,Geometry
import mapperWidgets
from touchinstance import TouchInstance
import evdev
from evdev import ecodes as ec

from touchmapper_config import CONFIG
from mapperOutput import Mouse,Keyboard,OUTPUT_HUB



class Gesture:
    def __init__(self) -> None:
        self.clear()
    def clear(self):
        self.startTime=time.time_ns()
        self.initX:float|None=None
        self.initY:float|None=None
        self.lastX:float|None=None
        self.lastY:float|None=None
        self.clicks:int=0
    # Do gestures, after the touch isn't captured by any widget
    def processGesture(self,touches:dict[int,TouchRelative],mouse:Mouse):
        
        # print(touches)
        activeTouches:dict[int,TouchRelative]={}
        for slot,touch in touches.items():
            if touch.pressed:
                activeTouches[slot]=touch
        # time2=time.time_ns()
        # if time2-self.startTime<100000:
        #     self.clicks=max(self.clicks,activeTouches.__len__())
        #     return
        # if activeTouches.__len__()<1:
        #     self.doSingleTouchGesture(activeTouches,mouse)
        #     mouse.syn()
        #     time.sleep(0.01)
        #     mouse.setPressed(0)
        #     mouse.syn()
        #     self.clicks=0
        #     return
        if activeTouches.__len__()==1:
            self.doSingleTouchGesture(activeTouches,mouse)
        else:
            mouse.setPressed(0)
            mouse.syn()
        if activeTouches.__len__()>=2:
            pos2=self.calculateAvgPos(activeTouches)
    def calculateAvgPos(self,activeTouches:dict[int,TouchRelative]):
        sums=[0.0,0.0]
        count=0
        for slot,touch in activeTouches.items():
            sums[0]=sums[0]+touch.x
            sums[1]=sums[1]+touch.y
        count=activeTouches.__len__()
        avgX=sums[0]/count
        avgY=sums[1]/count
        self.lastX
        return (avgX,avgY)
    def doSingleTouchGesture(self,activeTouches:dict[int,TouchRelative],mouse:Mouse):
        for slot,touch in activeTouches.items():
            mouse.moveFractional(touch)
            if touch.pressed:
                mouse.setPressed(1)
            mouse.syn()

class Mapper:
    geometryTouch:Geometry
    geometryOutput:Geometry=Geometry(0,16384,0,16384)
    widgetManager:mapperWidgets.WidgetManager|None=None
    gesture:Gesture|None=None
    def __init__(self):
        self.mouse = OUTPUT_HUB.mouse
        self.keyboard=OUTPUT_HUB.keyboard
        self.touches:dict[int, TouchRelative]={}
        self.touchesSwitched:set[int]=set()
        self.touchesCapturedByWidget:dict[int,mapperWidgets.Widget]={}
        self.debugInfo=False
        
    # Update self touches from new event
    def updateTouches(self,touches:dict[int, TouchInstance]):
        for slot,touch in touches.items():
            if slot not in self.touches or self.touches[slot].pressed != touch.pressed:
                self.touchesSwitched.add(slot)
            self.touches[slot]=TouchRelative.fromAbsolute(touch,self.geometryTouch).flip(CONFIG.flip_x,CONFIG.flip_y,CONFIG.swap_xy)
        self.processTouchesFrame()
        if self.debugInfo:
            print(f"Mapper: {self.touches}, ToWidgets: {self.touchesCapturedByWidget}")
    
    # Process to send touches to a widget or the gestures
    def processTouchesFrame(self):
        sendTouches:dict[int,TouchRelative]={}
        touchesReleased:list[int]=[]
        
        for slot,relTouch in self.touches.items():
            # Attempt to bind newly pressed touches to a widget
            if relTouch.pressed and (slot in self.touchesSwitched):
                self.processWidgets(relTouch,slot)
            # Unbind released touches from a widget
            if ((not relTouch.pressed) 
                and (slot in self.touchesSwitched) 
                and (slot in self.touchesCapturedByWidget)):
                self.touchesCapturedByWidget[slot].onRelease(relTouch)
                
            elif slot in self.touchesCapturedByWidget:
                self.touchesCapturedByWidget[slot].onTouch(relTouch)
            # Do gestures if not bind to a widget
            if slot not in self.touchesCapturedByWidget:
                sendTouches[slot]=(relTouch)
            if not relTouch.pressed:
                touchesReleased.append(slot)
        for slot in touchesReleased:
            if slot in self.touchesCapturedByWidget:
                self.touchesCapturedByWidget.pop(slot)
            self.touches.pop(slot)
        if sendTouches.__len__()>0:
            self.processGesture(sendTouches)
        self.touchesSwitched.clear()
        
        self.keyboard.syn()
        
    # Check whether the touch is captured by a widget and store that widget    
    def processWidgets(self,touch:TouchRelative,slot:int):
        if self.widgetManager and isinstance(self.widgetManager,mapperWidgets.WidgetManager):
            widgets:list[mapperWidgets.Widget]=self.widgetManager.getWidgets()
            for widget in widgets:
                if widget.shouldCapture(touch):
                    self.touchesCapturedByWidget[slot]=widget
                    
    def processGesture(self,touches:dict[int,TouchRelative]):
        if not self.gesture:
            self.gesture=Gesture()
        self.gesture.processGesture(touches,self.mouse)
            