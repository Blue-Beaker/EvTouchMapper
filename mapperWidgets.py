import geometryHelper

class Widget:
    def __init__(self,x,y,width,height) -> None:
        pass
    def isInWidget(self,relTouch:geometryHelper.TouchRelative):
        return False
    
class WidgetManager:
    
    def __init__(self) -> None:
        self.widgets:list[Widget]=[]
    def addWidget(self,widget:Widget):
        self.widgets.append(widget)
    def addWidgets(self,widgets:list[Widget]):
        for widget in widgets:
            self.addWidget(widget)
    def getWidgets(self):
        return self.widgets