import math
from typing import override
import pynput
from touchinstance import TouchInstance

class Geometry():
    def __init__(self,minX,maxX,minY,maxY) -> None:
        self.minX=minX
        self.maxX=maxX
        self.minY=minY
        self.maxY=maxY

class TouchRelative:

    def __init__(self,x:float,y:float,id:float=None,pressed:bool=True):
        self.x=x
        self.y=y
        self.id=id
        self.pressed=pressed

    @staticmethod
    def fromAbsolute(touch:TouchInstance,geometry:Geometry):
        newX=(touch.x-geometry.minX)/(geometry.maxX-geometry.minX)
        newY=(touch.y-geometry.minY)/(geometry.maxY-geometry.minY)
        newTouch=TouchRelative(x=newX,y=newY,id=touch.id,pressed=touch.pressed)
        return newTouch
    
    def toAbsolute(self,geometry:Geometry):
        newX=round(self.x*(geometry.maxX-geometry.minX)+geometry.minX)
        newY=round(self.y*(geometry.maxY-geometry.minY)+geometry.minY)
        newTouch=TouchInstance(x=newX,y=newY,id=self.id,pressed=self.pressed)
        return newTouch
    
    def flip(self,flipX:bool=False,flipY:bool=False,swapXY:bool=False):
        if flipX:
            self.x=1-self.x
        if flipY:
            self.x=1-self.y
        if swapXY:
            c=self.x
            self.x=self.y
            self.y=c
        return self
    
    @override
    def __str__(self):
        if self.pressed:
            return f"Pressed {self.id}@({self.x},{self.y})"
        else:
            return f"Release {self.id}"
            return f"Release {self.id}@({self.x},{self.y})"