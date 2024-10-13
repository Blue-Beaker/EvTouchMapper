
from typing import override

class TouchInstance:
    id:int
    x:int
    y:int
    pressed:bool
    def __init__(self,x:int=-1,y:int=-1,id:int=-1,pressed:bool=True):
        self.id=id
        self.x=x
        self.y=y
        self.pressed=pressed
    @override
    def __str__(self):
        if self.pressed:
            return f"Pressed {self.id}@({self.x},{self.y})"
        else:
            return f"Release {self.id}"
            return f"Release {self.id}@({self.x},{self.y})"