import pynput
import geometryHelper
from touchinstance import TouchInstance

geometryTouch:geometryHelper.Geometry
geometryScreen:geometryHelper.Geometry
mouse=pynput.mouse.Controller()

def processTouches(captured:dict[int, TouchInstance]):
    touchList:dict[int, TouchInstance]={}
    for slot,touch in captured.items():
        touchList[str(slot)]=str(geometryHelper.TouchRelative.fromAbsolute(touch,geometryTouch).toAbsolute(geometryScreen))
    print(touchList)
    if captured.__len__()==1:
        for slot,touch in captured.items():
            mouseX=mouse.position[0]
            mouseY=mouse.position[1]
            mouse.move(touch.x-mouseX,touch.y-mouseY)
            if touch.pressed:
                mouse.press(pynput.mouse.Button.left)
            else:
                mouse.release(pynput.mouse.Button.left)