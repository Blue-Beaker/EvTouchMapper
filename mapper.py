import math
import time
import evdev.uinput
import geometryHelper
from touchinstance import TouchInstance
import evdev
from evdev import ecodes as ec

geometryTouch:geometryHelper.Geometry
geometryOutput:geometryHelper.Geometry=geometryHelper.Geometry(0,16384,0,16384)

capabs=cap = {
    ec.EV_KEY : [ec.BTN_LEFT, ec.BTN_RIGHT, ec.BTN_MIDDLE, ec.BTN_FORWARD, ec.BTN_BACK],
    ec.EV_ABS : [
        (ec.ABS_X, evdev.AbsInfo(value=0, min=0, max=16384,
                          fuzz=0, flat=0, resolution=0)),
        (ec.ABS_Y, evdev.AbsInfo(0, 0, 16384, 0, 0, 0))]
}

ui_mouse = evdev.UInput(cap,name='mapper-mouse')

def processTouches(captured:dict[int, TouchInstance]):
    print(captured)
    # touchList:dict[int, TouchInstance]={}
    # for slot,touch in captured.items():
    #     touchList[str(slot)]=str()
    # print(touchList)
    if captured.__len__()==1:
        for slot,touch in captured.items():
            touch2=geometryHelper.TouchRelative.fromAbsolute(touch,geometryTouch).toAbsolute(geometryOutput)
            print(touch2)
            ui_mouse.write(ec.EV_ABS, ec.ABS_X, touch2.x)
            ui_mouse.write(ec.EV_ABS, ec.ABS_Y, touch2.y)
            if touch2.pressed:
                ui_mouse.write(ec.EV_KEY,ec.BTN_LEFT,1)
            ui_mouse.syn()
    else:
        ui_mouse.write(ec.EV_KEY,ec.BTN_LEFT,0)
        ui_mouse.syn()