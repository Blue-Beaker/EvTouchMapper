from configparser import ConfigParser
import os,sys

CONFIG_PATH=os.path.join(os.path.dirname(sys.argv[0]),"touchmapper.cfg")
SECTION='Touchscreen'

PARSER:ConfigParser=ConfigParser(default_section="Touchscreen",defaults={"flip_x":False,"flip_y":False,"swap_xy":False})

def update_config():
    PARSER.read(CONFIG_PATH)
    with open(CONFIG_PATH,"w") as f:
        PARSER.write(f)

@property
def flip_x():
    return PARSER['SECTION']['flip_x']
@property
def flip_x(value:bool):
    PARSER['SECTION']['flip_x']=value

@property
def flip_y():
    return PARSER['SECTION']['flip_y']
@property
def flip_y(value:bool):
    PARSER['SECTION']['flip_y']=value

@property
def swap_xy():
    return PARSER['SECTION']['swap_xy']
@property
def swap_xy(value:bool):
    PARSER['SECTION']['swap_xy']=value
