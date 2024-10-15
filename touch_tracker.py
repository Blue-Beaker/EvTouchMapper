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
    
    def __init__(self):

        self.print_info=False

        self.lastSlot:int=0
        self.trackID:int=-1
        self.capturedIds:set[int]=set()
        """Touches to be sent to mapper."""
        self.slotsToIds:dict[int,int]={}
        """ Slots to id mappings: {slot, id}"""
        self.idsToStopCapture:set[int]=set()
        """ Touches to stop capture because they released. Should be cleared after sending to mapper"""
        
        self.touches:dict[int,TouchInstance]={}
        """Dict: slot -> touch"""
        
        self.bufferedActions:list[tuple[int,int,int]]=[]
        """ Buffered actions, use to check if touch is captured (action, slot, id)"""
        
        self.unsentEvents:list[tuple[int,InputEvent]]=[]
        """Buffered events to be sent to passthrough uinput device."""
        
        self.capturedTouches:dict[int,TouchInstance]={}
        
        self.updatedTouches:set[int]=set()
        """Touch slots that updated after last SYN event."""
        
    def saveTouches(self,event:InputEvent):
        if event.type==3:
            if event.code==ecodes.ABS_MT_SLOT:
                slot:int=event.value
                if slot!=-1:
                    if slot not in self.touches:
                        self.touches[slot]=TouchInstance(id=-1)
                    self.lastSlot=slot
                    self.updatedTouches.add(slot)

            elif event.code==ecodes.ABS_MT_TRACKING_ID:
                trackID:int=event.value
                if trackID==-1:
                    self.releaseSlot(self.lastSlot)
                    self.idsToStopCapture.add(self.trackID)
                else:
                    self.startPressSlot(self.lastSlot,trackID)
                    self.trackID=trackID
                    self.slotsToIds[self.lastSlot]=trackID

            elif (event.code==ecodes.ABS_X) or (event.code==ecodes.ABS_MT_POSITION_X):
                self.touches[self.lastSlot].x=event.value

            elif (event.code==ecodes.ABS_Y) or (event.code==ecodes.ABS_MT_POSITION_Y):
                self.touches[self.lastSlot].y=event.value

        if event.type==1 and event.code==ecodes.BTN_TOUCH:
            if event.value==1:
                self.startPressSlot(self.lastSlot)
            if event.value==0:
                self.releaseSlot(self.lastSlot)
                
        if event.type==0:
            self.unsentEvents.append((-1,event))
        else:
            self.unsentEvents.append((self.lastSlot,event))

    def handleEvent(self,event:InputEvent):
        """Handles input event from evdev device"""
        self.saveTouches(event)
        if event.type==0:
            for action,slot,id in self.bufferedActions:
                if action==ACTION_PRESS:
                    self.checkStartCapture(slot)
            passthroughEvents=self.sendEvents()
            self.unsentEvents.clear()
            return passthroughEvents
        return None
    
    def startPressSlot(self,slot:int,trackId:int|None=None):
        if trackId==None:
            trackId=self.trackID
        if slot not in self.touches:
            self.touches[slot]=TouchInstance(id=trackId)
        self.touches[slot].pressed=True
        self.touches[slot].id=trackId

        self.bufferedActions.append((ACTION_PRESS,slot,trackId))
        
    def getIdFromSlot(self,slot:int):
        if slot in self.slotsToIds:
            return self.slotsToIds[slot]
        else:
            return -1
        
    def startCapturingSlot(self,slot:int):
        id=self.getIdFromSlot(slot)
        if id>0:
            self.capturedIds.add(id)
    def startCapturingId(self,id:int):
        if id>0:
            self.capturedIds.add(id)
            
    def stopCapturingSlot(self,slot:int):
        touchId=self.getIdFromSlot(slot)
        if touchId>0:
            self.idsToStopCapture.add(touchId)
            
    def removeCapturingId(self,trackId:int):
        if trackId in self.capturedIds:
            self.capturedIds.remove(trackId)
        
    def releaseSlot(self,slot:int):
        if slot in self.touches:
            self.touches[slot].pressed=False
        trackId=self.getIdFromSlot(slot)
        if trackId in self.capturedIds:
            self.stopCapturingSlot(trackId)
            
        self.bufferedActions.append((ACTION_RELEASE,slot,trackId))

    def checkStartCapture(self,slot:int):
        tid=self.getIdFromSlot(slot)
        if self.shouldStartCapture(self.touches[slot]):
            self.startCapturingSlot(slot)
            
    def shouldStartCapture(self,touch:TouchInstance):
        if touch.x>=0:
            return True
        return False
    
    def isIdCaptured(self,slot:int):
        return slot in self.capturedIds
    
    def sendEvents(self):
        """Get event for passthrough device"""
        passThroughEvents:list[InputEvent]=[]
        for slot,event in self.unsentEvents:
            tid=self.getIdFromSlot(slot)
            self.printEvents(slot,event)
            if self.isIdCaptured(tid):
                self.addCapturedTouchToBuffer(self.touches[slot],tid)
            else:
                passThroughEvents.append(event)
        return passThroughEvents
    
    # def getLastTouch(self):
    #     if self.lastSlot in self.touchInstances:
    #         return self.touchInstances[self.lastSlot]
        
    def addCapturedTouchToBuffer(self,touch:TouchInstance,tid:int):
        self.capturedTouches[tid]=touch
        if self.print_info:
            print("Captured:",str(touch))

    def sendToMapper(self):
        """Get captured touches to send to mapper. Also flushes"""
        captured:dict[int, TouchInstance]={}
        
        for slot in self.updatedTouches:
            tid=self.getIdFromSlot(slot)
            if tid in self.capturedTouches:
                touch=self.capturedTouches[tid]
                if touch.x>0 and touch.y>0:
                    captured[tid]=touch
                
            
        for action,slot,id in self.bufferedActions:
            if action==ACTION_RELEASE:
                self.removeCapturingId(id)
                self.slotsToIds[slot]=-1
                if slot in self.touches:
                    self.touches.pop(slot)
                
        # self.slotsToIds[self.lastSlot]=-1
        self.idsToStopCapture.clear()
        self.capturedTouches.clear()
        self.bufferedActions.clear()
        return captured
    
    def printEvents(self,slot:int,event:InputEvent):
            # printEvent=event.code not in [ecodes.ABS_MT_POSITION_X,ecodes.ABS_MT_POSITION_Y,ecodes.ABS_X,ecodes.ABS_Y]
        printEvent=self.print_info
        if printEvent:
            ev=categorize(event)

            touchList=[]
            for id,instance in self.touches.items():
                touchList.append(instance.__str__())
            
            print(f'\033[{37-slot}m',end="")
            if self.isIdCaptured(slot):
                print(colorama.Back.RED,end="")
            else:
                print(colorama.Back.BLACK,end="")
            print(ev,f"Type={event.type}",f"Code={event.code}",f"Value={event.value}")
            print(f"{",".join(touchList)}, captured={self.capturedIds}, ids={self.slotsToIds}")
