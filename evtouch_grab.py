import evdev
from evdev import ecodes
from evdev import UInput, InputDevice
from evdev.events import InputEvent
import pynput
from touch_tracker import TouchTracker
from touchmapper_config import CONFIG
import geometryHelper
from mapper import Mapper
# sudo usermod -a -G input $USER before using this

if __name__ == "__main__":
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
    # print(device.capabilities(verbose=True))
    x=device.absinfo(0)
    y=device.absinfo(1)

    Mapper.geometryTouch=geometryHelper.Geometry(x.min,x.max,y.min,y.max)

    touch_passthrough = UInput.from_device(device, name=device.name+'passthrough')

    device.grab()
    
    mapper=Mapper()
    
    tracker=TouchTracker()
    # tracker.print_info=True
    for event in device.read_loop():
        event:InputEvent
        events=tracker.handleEvent(event)
        if events:
            for event in events:
                touch_passthrough.write_event(event)
            captured=tracker.getCapturedTouches()
            mapper.updateTouches(captured)