#! /bin/python3
import pywayland
import pywayland.client
from pywayland.protocol.wayland import wl_seat
import pywayland.protocol_core
import pywayland.server
display=pywayland.client.display.Display()
display.connect()
interface=pywayland.protocol_core.Interface()
seat=wl_seat.WlSeat()
queue=pywayland.client.eventqueue.EventQueue(display)

def listen(event):
    print(event)

listener=pywayland.server.Listener(listen)
