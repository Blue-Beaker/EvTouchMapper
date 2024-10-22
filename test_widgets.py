from mapperWidgets import *
from evdev import ecodes as ec
class TestWidgets(WidgetManager):
    def __init__(self) -> None:
        super().__init__()
        self.addWidget(Button(0.1,0.8,0.2,0.1,False,"A").setKeyCode(ec.KEY_A))
        self.addWidget(Button(0.3,0.8,0.2,0.1,False,"D").setKeyCode(ec.KEY_D))
        self.addWidget(Button(0.2,0.7,0.2,0.1,False,"W").setKeyCode(ec.KEY_W))
        self.addWidget(Button(0.2,0.9,0.2,0.1,False,"S").setKeyCode(ec.KEY_S))
        self.addWidget(Button(0.9,0.7,0.2,0.1,False,"Enter").setKeyCode(ec.KEY_ENTER))
        self.addWidget(Button(0.9,0.9,0.2,0.1,False,"SPACE").setKeyCode(ec.KEY_SPACE))
        self.addWidget(Button(0.9,0.8,0.2,0.1,False,"RSHIFT").setKeyCode(ec.KEY_RIGHTSHIFT))
        self.addWidget(Button(0.1,0.1,0.1,0.1,False,"ESC").setKeyCode(ec.KEY_ESC))