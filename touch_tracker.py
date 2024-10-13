from typing import override
import evdev,os,asyncio,colorama
from evdev import ecodes
from evdev import UInput, InputDevice,categorize
from evdev.events import InputEvent
import touchmapper_config
from touchinstance import TouchInstance
ACTION_PRESS=1
ACTION_RELEASE=0
    
class TouchTracker:

    # print_info:bool

    # lastSlot:int
    # trackID:int
    # capturedSlots:set[int]
    # touchInstances:dict[int,TouchInstance]
    # unsentActions:list[tuple[int,int]]
    # unsentEvents:list[tuple[int,InputEvent]]
    def __init__(self):

        self.print_info=False

        self.lastSlot:int=-1
        self.trackID:int=-1
        self.capturedSlots:set[int]=set()
        self.touchInstances:dict[int,TouchInstance]={}
        self.unsentActions:list[tuple[int,int]]=[]
        self.unsentEvents:list[tuple[int,InputEvent]]=[]
        self.capturedTouches:dict[int,TouchInstance]={}
    def saveTouches(self,event:InputEvent):
        if event.type==3:
            if event.code==ecodes.ABS_MT_SLOT:
                if event.value!=-1:
                    if event.value not in self.touchInstances:
                        self.touchInstances[event.value]=TouchInstance(id=-1)
                    self.lastSlot=event.value

            elif event.code==ecodes.ABS_MT_TRACKING_ID:
                if event.value==-1:
                    self.stopPressSlot(self.lastSlot)
                else:
                    self.startPressSlot(self.lastSlot,event.value)
                    self.trackID=event.value

            elif (event.code==ecodes.ABS_X) or (event.code==ecodes.ABS_MT_POSITION_X):
                if self.lastSlot!=-1:
                    self.touchInstances[self.lastSlot].x=event.value

            elif (event.code==ecodes.ABS_Y) or (event.code==ecodes.ABS_MT_POSITION_Y):
                if self.lastSlot!=-1:
                    self.touchInstances[self.lastSlot].y=event.value

        if event.type==1 and event.code==ecodes.BTN_TOUCH:
            if event.value==1:
                if self.lastSlot==-1:
                    self.lastSlot=0
                self.startPressSlot(self.lastSlot)
            if event.value==0:
                self.stopPressSlot(self.lastSlot)
        if event.type==0:
            for action,slot in self.unsentActions:
                if action==ACTION_PRESS:
                    self.checkStartCapture(slot)
            self.unsentActions.clear()
            self.unsentEvents.append((-1,event))
        else:
            self.unsentEvents.append((self.lastSlot,event))

    def handleEvent(self,event:InputEvent):
        self.saveTouches(event)
        if event.type==0:
            passthroughEvents=self.sendEvents()
            self.unsentEvents.clear()
            return passthroughEvents
        return None
    
    def startPressSlot(self,slot:int,id:int=None):
        if id==None:
            id=self.trackID
        if slot not in self.touchInstances:
            self.touchInstances[slot]=TouchInstance(id=id)
        self.touchInstances[slot].pressed=True
        self.touchInstances[slot].id=id

        self.unsentActions.append((ACTION_PRESS,slot))
    def stopPressSlot(self,slot:int):
        if slot in self.touchInstances:
            self.touchInstances[slot].pressed=False
        if slot in self.capturedSlots:
            self.capturedSlots.remove(slot)
        self.unsentActions.append((ACTION_RELEASE,slot))

    def checkStartCapture(self,slot:int):
        if self.shouldStartCapture(self.touchInstances[slot]):
            self.capturedSlots.add(slot)
    def shouldStartCapture(self,touch:TouchInstance):
        if touch.x>0:
            return True
        return False
    def isSlotCaptured(self,slot:int):
        return slot in self.capturedSlots
    
    def sendEvents(self):
        passThroughEvents:list[InputEvent]=[]
        for i,event in self.unsentEvents:
            self.printEvents(i,event)
            if self.isSlotCaptured(i):
                self.handleTouch(self.touchInstances[i],i)
            else:
                passThroughEvents.append(event)
        return passThroughEvents
    # def getLastTouch(self):
    #     if self.lastSlot in self.touchInstances:
    #         return self.touchInstances[self.lastSlot]
        
    def handleTouch(self,touch:TouchInstance,slot:int):
        self.capturedTouches[slot]=touch
        if self.print_info:
            print("Captured:",str(touch))

    def getCapturedTouches(self):
        captured=self.capturedTouches.copy()
        self.capturedTouches.clear()
        return captured

    def putValue(self,slot:int,id:int=None,x:int=None,y:int=None,pressed:int=None):
        if not slot in self.touchInstances:
            self.touchInstances[slot]=TouchInstance(id=id)
    
    def printEvents(self,slot:int,event:InputEvent):
            # printEvent=event.code not in [ecodes.ABS_MT_POSITION_X,ecodes.ABS_MT_POSITION_Y,ecodes.ABS_X,ecodes.ABS_Y]
        printEvent=self.print_info
        if printEvent:
            ev=categorize(event)

            touchList=[]
            for id,instance in self.touchInstances.items():
                touchList.append(instance.__str__())
            
            print(f'\033[{37-slot}m',end="")
            if self.isSlotCaptured(slot):
                print(colorama.Back.RED,end="")
            else:
                print(colorama.Back.BLACK,end="")
            print(ev,f"Type={event.type}",f"Code={event.code}",f"Value={event.value}")
            print(",".join(touchList),"captured="+str(self.capturedSlots))
