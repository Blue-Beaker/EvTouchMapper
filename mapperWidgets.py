from typing import override
import geometryHelper

class Widget:
    def __init__(self,x:float,y:float,width:float,height:float,isRound:bool=False) -> None:
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.isRound=isRound
        print(self)
    def __repr__(self) -> str:
        return f"{self.__class__.__name__} at ({self.x},{self.y}) {self.width}x{self.height} {'Round' if self.isRound else 'Box'}"
    def isInWidget(self,relTouch:geometryHelper.TouchRelative) -> bool:
        if self.isRound:
            return (pow(relTouch.x-self.x,2)/pow(self.width/2,2)+
            pow(relTouch.y-self.y,2)/pow(self.height/2,2))<1
        else:
            return ((abs(relTouch.x-self.x)<self.width/2) and 
            (abs(relTouch.y-self.y)<self.height/2))
    def shouldCapture(self,relTouch:geometryHelper.TouchRelative) -> bool:
        return False
    def onTouch(self,relTouch:geometryHelper.TouchRelative):
        pass
    def onRelease(self,relTouch:geometryHelper.TouchRelative):
        pass
    
class Button(Widget):
    @override
    def shouldCapture(self, relTouch: geometryHelper.TouchRelative):
        return self.isInWidget(relTouch)
    def onTouch(self, relTouch: geometryHelper.TouchRelative):
        print("Pressing",relTouch,self)
    def onRelease(self, relTouch: geometryHelper.TouchRelative):
        print("Released",relTouch,self)
    
class WidgetManager:
    __widgets:list[Widget]
    def __init__(self) -> None:
        self.__widgets:list[Widget]=[]
    def addWidget(self,widget:Widget):
        self.__widgets.append(widget)
    def addWidgets(self,widgets:list[Widget]):
        for widget in widgets:
            self.addWidget(widget)
    def getWidgets(self):
        return self.__widgets