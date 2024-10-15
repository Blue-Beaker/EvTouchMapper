import evdev
from evdev import ecodes as ec
import geometryHelper

MOUSE_CAPABS = {
    ec.EV_KEY : [ec.BTN_LEFT, ec.BTN_RIGHT, ec.BTN_MIDDLE, ec.BTN_FORWARD, ec.BTN_BACK],
    ec.EV_ABS : [
        (ec.ABS_X, evdev.AbsInfo(value=0, min=0, max=16384,
                          fuzz=0, flat=0, resolution=0)),
        (ec.ABS_Y, evdev.AbsInfo(0, 0, 16384, 0, 0, 0))],
    ec.EV_REL:[ec.REL_X,ec.REL_Y,ec.REL_HWHEEL,ec.REL_WHEEL,ec.REL_WHEEL_HI_RES,ec.REL_HWHEEL_HI_RES]
}

class Mouse:
    geometry=geometryHelper.Geometry(0,16384,0,16384)
    def __init__(self,device_name:str='mapper-mouse') -> None:
        self.uinput=evdev.UInput(MOUSE_CAPABS,name=device_name)
        
    def moveRaw(self,x:int,y:int):
        self.uinput.write(ec.EV_ABS, ec.ABS_X, x)
        self.uinput.write(ec.EV_ABS, ec.ABS_Y, y)
        
    def moveFractional(self,rel:geometryHelper.TouchRelative):
        pos=rel.toAbsolute(self.geometry)
        self.moveRaw(pos.x,pos.y)
    def setPressed(self,pressed:int=1,key:int=ec.BTN_LEFT):
        self.uinput.write(ec.EV_KEY,key,pressed)
    def syn(self):
        self.uinput.syn()
        
class Keyboard():
    def __init__(self,device_name:str='mapper-keyboard') -> None:
        self.uinput=evdev.UInput(name=device_name)
        
    def setPressed(self,key:int,pressed:int=1):
        self.uinput.write(ec.EV_KEY,key,pressed)
    
    def setPressedByName(self,key:str,pressed:int=1):
        name='KEY_'+key.upper()
        if name in ec.keys:
            self.setPressed(pressed,ec.keys[name])
        else:
            print(f'Key {name} not found')
    
    def syn(self):
        self.uinput.syn()
        
class OutputHub():
    def __init__(self) -> None:
        self.mouse=Mouse()
        self.keyboard=Keyboard()
        
OUTPUT_HUB=OutputHub()