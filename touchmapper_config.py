from configparser import ConfigParser
import os,sys


CONFIG_PATH=os.path.join(os.path.dirname(sys.argv[0]),"touchmapper.cfg")
SECTION='Touchscreen'
class __CFG:
    def __init__(self) -> None:
        self.parser=ConfigParser(default_section=SECTION,defaults={"flip_x":0,"flip_y":0,"swap_xy":0})
    @property
    def flip_x(self):
        return int(self.parser[SECTION]['flip_x'])
    @flip_x.setter
    def setFlip_x(self,value:int):
        self.parser[SECTION]['flip_x']=str(value)

    @property
    def flip_y(self):
        return int(self.parser[SECTION]['flip_y'])
    @flip_y.setter
    def setFlip_y(self,value:int):
        self.parser[SECTION]['flip_y']=str(value)

    @property
    def swap_xy(self):
        return int(self.parser[SECTION]['swap_xy'])
    @swap_xy.setter
    def setSwap_xy(self,value:int):
        self.parser[SECTION]['swap_xy']=str(value)
        
    def update_config(self):
        self.parser.read(CONFIG_PATH)
        with open(CONFIG_PATH,"w") as f:
            self.parser.write(f)

CONFIG:__CFG=__CFG()