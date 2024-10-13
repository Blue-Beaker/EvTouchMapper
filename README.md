# EvTouchMapper

A touchscreen remapper for linux, based on evdev, written with python. 
Run evtouch_grab.py in a terminal to start. 

Works both under Wayland or X11 for now. 
For now, it only remaps single-touch into left mouse button, but the possibilities can be extended further. 

Requires `python-evdev` module.
    `sudo apt install python3-evdev`

You need to be in `input` group to use this:
    `sudo usermod -a -G input $USER`