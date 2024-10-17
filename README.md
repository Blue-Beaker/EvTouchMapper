# EvTouchMapper

A touchscreen remapper for linux, based on evdev, written with python. 
Run evtouch_grab.py in a terminal to start. 

Works both under Wayland or X11 for now. 

For now, it:
- Remaps single-touch into left mouse button.  
- Adds onscreen buttons, that can emulate keys and only reacts to touch.  
  (When using Wayland, the overlay isn't kept on top automatically, you need to set it manually with your compositor/window manager)

Sorry for the bad code. Just treat it as a demonstration of mapping touch controls with evdev.  

Requires `python-evdev` and `pyqt5` modules.
    `sudo apt install python3-evdev`
    `sudo apt install python3-pyqt5`

You need to be in `input` group to use this:
    `sudo usermod -a -G input $USER`