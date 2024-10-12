from typing import override
import evdev,os,asyncio,colorama
from evdev import ecodes
from evdev import UInput, InputDevice,categorize
from evdev.events import InputEvent
# sudo usermod -a -G input $USER before using this


EV_ABS=ecodes.ecodes['EV_ABS']
EV_KEY=ecodes.ecodes['EV_KEY']
BTN_TOUCH=ecodes.ecodes['BTN_TOUCH']
INPUT_PROP_DIRECT=ecodes.ecodes['INPUT_PROP_DIRECT']

ACTION_PRESS=1
ACTION_RELEASE=0

class TouchInstance:
    id:int=-1
    x:int=-1
    y:int=-1
    pressed:bool=True
    def __init__(self,id):
        self.id=id
    @override
    def __str__(self):
        if self.pressed:
            return f"Touch {self.id} at ({self.x},{self.y})"
        else:
            return ""
    
class TouchTracker:
    lastSlot:int=-1
    trackID:int=-1
    capturedIDs:set[int]=set()
    touchInstances:dict[int,TouchInstance]={}
    unsendActions:list[tuple[str,int]]=[]
    def saveTouches(self,event:InputEvent):
        if event.type==3:
            if event.code==ecodes.ABS_MT_SLOT:
                if event.value!=-1:
                    if event.value not in self.touchInstances:
                        self.touchInstances[event.value]=TouchInstance(-1)
                    self.lastSlot=event.value

            elif event.code==ecodes.ABS_MT_TRACKING_ID:
                if event.value==-1:
                    self.stopPressSlot(self.lastSlot)
                else:
                    self.startPressSlot(self.lastSlot)
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
            for action,slot in self.unsendActions:
                if action==ACTION_PRESS:
                    self.checkStartCapture(slot)
            self.unsendActions.clear()

    def handleEvent(self,event:InputEvent):
        ev=categorize(event)
        self.saveTouches(event)
        liststr=""
        for id,instance in self.touchInstances.items():
            liststr=liststr+","+instance.__str__()
        
        capture=False
        if event.type!=0:
            if self.handleLastTouch():
                capture=True
            
        # printEvent=event.code not in [ecodes.ABS_MT_POSITION_X,ecodes.ABS_MT_POSITION_Y,ecodes.ABS_X,ecodes.ABS_Y]
        printEvent=True
        if printEvent:
            print(f'\033[{37-self.lastSlot}m',end="")
            if capture:
                print(colorama.Back.RED,end="")
            else:
                print(colorama.Back.BLACK,end="")
            print(ev,f"Type={event.type}",f"Code={event.code}",f"Value={event.value}")
            print(liststr,"captured="+str(self.capturedIDs))
        return capture
    
    def startPressSlot(self,slot:int,id:int=-1):
        if slot not in self.touchInstances:
            self.touchInstances[slot]=TouchInstance(id)
        self.touchInstances[slot].pressed=True
        self.unsendActions.append((ACTION_PRESS,slot))
    def stopPressSlot(self,slot:int):
        if slot in self.touchInstances:
            self.touchInstances[slot].pressed=False
        if slot in self.capturedIDs:
            self.capturedIDs.remove(slot)
        self.unsendActions.append((ACTION_RELEASE,slot))

    def checkStartCapture(self,slot):
        if self.shouldStartCapture(self.touchInstances[slot]):
            self.capturedIDs.add(slot)
    def shouldStartCapture(self,touch:TouchInstance):
        if touch.x>8192:
            return True
        return False
    
    def getLastTouch(self):
        if self.lastSlot in self.touchInstances:
            return self.touchInstances[self.lastSlot]
    def handleLastTouch(self):
        lastTouch=self.getLastTouch()
        if lastTouch:
            return self.handleTouch(lastTouch)
        return False        
    def handleTouch(self,touch:TouchInstance):
        if self.lastSlot in self.capturedIDs:
            return True
        return False
    
    def putValue(self,slot:int,id:int=None,x:int=None,y:int=None,pressed:int=None):
        if not slot in self.touchInstances:
            self.touchInstances[slot]=TouchInstance(id)


if __name__ == "__main__":
    
    devices = [InputDevice(path) for path in evdev.list_devices()]
    tp_devices:list[InputDevice]=[]
    for device in devices:
        capabilities=device.capabilities()
        props=device.input_props()
        # Exclude devices without direct input
        if INPUT_PROP_DIRECT in props:
            # Exclude non-touch devices and pens
            if BTN_TOUCH in capabilities[EV_KEY] and ecodes.BTN_TOOL_PEN not in capabilities[EV_KEY]:
                # print(device.path, device.name, device.phys,device.capabilities(True,absinfo=False),device.input_props(True))
                tp_devices.append(device)

    if tp_devices.__len__()==1:
        device=tp_devices[0]
    if tp_devices.__len__()>1:
        print("Select a device:")
        for i in range(tp_devices.__len__()):
            print(i,tp_devices[i].name)
        num=int(input())
        device=tp_devices(num)
    if not isinstance(device,InputDevice):
        print("No touchscreen device selected, exiting")
        exit()

    print(device.name)

    virtual_input = UInput.from_device(device, name='passthrough')

    device.grab()

    tracker=TouchTracker()

    for event in device.read_loop():
        event:InputEvent
        if not tracker.handleEvent(event):
            virtual_input.write_event(event)
        else:
            print(tracker.getLastTouch())