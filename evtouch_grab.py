#! /bin/python3
import threading
import evdev
from evdev import ecodes
from evdev import UInput, InputDevice
from evdev.events import InputEvent
import pynput
import mapperWidgets
import test_widgets
from touch_tracker import TouchTracker
from touchmapper_config import CONFIG
import geometryHelper
from mapper import Mapper
import displayOverlay
# sudo usermod -a -G input $USER before using this
def runBackend():
    CONFIG.update_config()
    devices = [InputDevice(path) for path in evdev.list_devices()]
    tp_devices:list[InputDevice]=[]
    for device in devices:
        capabilities=device.capabilities()
        props=device.input_props()
        # Exclude devices without direct input
        if ecodes.INPUT_PROP_DIRECT in props:
            # Exclude non-touch devices and pens
            if ecodes.BTN_TOUCH in capabilities[ecodes.EV_KEY] and ecodes.BTN_TOOL_PEN not in capabilities[ecodes.EV_KEY]:
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
    device.grab()
    # print(device.capabilities(verbose=True))
    x=device.absinfo(0)
    y=device.absinfo(1)

    Mapper.geometryTouch=geometryHelper.Geometry(x.min,x.max,y.min,y.max)

    touch_passthrough = UInput.from_device(device, name=device.name+'passthrough')
    touch_passthrough.syn()
    
    mapper=Mapper()
    
    widgetManager=test_widgets.TestWidgets()
    mapper.widgetManager=widgetManager
    
    tracker=TouchTracker()
    try:
        overlayThread=threading.Thread(target=displayOverlay.initApp,args=[widgetManager])
        overlayThread.start()
        # tracker.print_info=True
        for event in device.read_loop():
            event:InputEvent
            events=tracker.handleEvent(event)
            if events:
                for event in events:
                    # pass
                    touch_passthrough.write_event(event)
                captured=tracker.sendToMapper()
                mapper.updateTouches(captured)
    except KeyboardInterrupt:
        displayOverlay.app.quit()
        
if __name__ == "__main__":
    runBackend()