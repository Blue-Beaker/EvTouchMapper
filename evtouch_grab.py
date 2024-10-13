from typing import override
import evdev,os,asyncio,colorama,configparser
from evdev import ecodes
from evdev import UInput, InputDevice,categorize
from evdev.events import InputEvent
from touch_tracker import TouchTracker
# sudo usermod -a -G input $USER before using this

if __name__ == "__main__":
    
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

    virtual_input = UInput.from_device(device, name='passthrough')

    device.grab()

    tracker=TouchTracker()

    for event in device.read_loop():
        event:InputEvent
        events=tracker.handleEvent(event)
        if events:
            for event in events:
                virtual_input.write_event(event)