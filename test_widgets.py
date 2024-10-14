from mapperWidgets import *
class TestWidgets(WidgetManager):
    def __init__(self) -> None:
        super().__init__()
        self.addWidget(Button(0.1,0.9,0.1,0.1,False))
        self.addWidget(Button(0.2,0.9,0.1,0.1,True))