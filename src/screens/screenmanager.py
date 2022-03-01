class GameScreen:
    def __init__(self):    pass
    def setup(self, screenManager):
        self.screenManager = screenManager 
    def draw(self, win):    pass
    def update(self, delta):    pass
    def keydown(self, event):    pass

class ScreenManager:
    def __init__(self, startScreen):
        self.curScreen = startScreen
        self.curScreen.setup(self)
        
    def draw(self, win):
        self.curScreen.draw(win)
    def update(self, delta):
        self.curScreen.update(delta)
    def keydown(self, event):
        self.curScreen.keydown(event)