# EvTouchMapper

A touchscreen remapper for linux, based on evdev, written with python.  
Run `launcher.py` to launch.  
Select your touchscreen device from dropdown, and press `Start` to start remapping.  

Works both under Wayland or X11 for now.  

For now, it:
- Remaps single-touch into left mouse button.  
- Adds onscreen buttons, that can emulate keys and only reacts to touch.  
  (When using Wayland, the overlay isn't kept on top automatically, you need to set it manually with your compositor/window manager)

Sorry for the bad code. Just treat it as a demonstration of mapping touch controls with evdev.  

Requires `python-evdev`, `pyqt5` and `pynput` modules.
    `sudo apt install python3-evdev`
    `sudo apt install python3-pyqt5`
    `sudo apt install python3-pynput`

You need to be in `input` group to use this:
    `sudo usermod -a -G input $USER`

## Tested Environments
- KDE Plasma 5.27.11:  
  Wayland - The overlay window needs to be pinned on top manually.  
  X11 - Totally fine. Used pynput as workaround for absolute mouse position.  

- Gnome 46:  
  Wayland - The overlay window has black background, making it impossible to see apps under it. The cutout isn't applied either, so mouse can't click through it.  
  X11 - Totally not work, can't grab input. Maybe the touchscreen is grabbed by another program?  