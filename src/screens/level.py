import pygame
from pygame.math import Vector2

import copy

from src.screens.screenmanager import ScreenManager, GameScreen
from src.entities.player import Player
from src.tilemap import Tilemap
from src.common import *

class Level(GameScreen):
    def __init__(self):
        tileImgs = loadSpriteSheet("res/temptiles.png", (16,16), (3,1), (1,1), 3, (0,0,0))
        self.tilemap = Tilemap(16, tileImgs)
        extraData = self.tilemap.loadLevel("res/levels/cameralevel.json")

        self.playerSpawn = Vector2(0,0)
        if "PlayerSpawn" in extraData:
            self.playerSpawn = Vector2(extraData["PlayerSpawn"][0][0], extraData["PlayerSpawn"][0][1] - 20)
        self.cameraTriggerRects = []
        self.cameraTriggerVectors = []
        if "CameraTriggers" in extraData:
            for i in range(int(len(extraData["CameraTriggers"])/2)):
                p1 = Vector2(extraData["CameraTriggers"][i*2])
                p2 = Vector2(extraData["CameraTriggers"][i*2+1])
                #r = pygame.Rect(p1, p2-p1)
                self.cameraTriggerRects.append(pygame.Rect(p1, p2-p1))
                self.cameraTriggerVectors.append((p1, p2))

    def setup(self, screenManager):
        super().setup(screenManager)

        self.player = Player(self.playerSpawn, 12, 20)
        self.scroll = Vector2(0, 0)
        self.cameraBounds = [Vector2(0, 0), Vector2(0, 0)]
        self.targetIndex = 0

    def draw(self, win : pygame.Surface):
        self.updateCamera(win.get_size())
        
        self.tilemap.draw(win, self.scroll)
        self.player.draw(win, self.scroll)

    def update(self, delta):
        self.player.update(delta, self.tilemap)

    def updateCamera(self, winDim):
        self.scroll += ((self.player.pos - Vector2(winDim)*0.5) - self.scroll) / 10

        col = self.player.rect.collidelist(self.cameraTriggerRects)
        if col > -1:    self.targetIndex = col#self.cameraBounds = self.cameraTriggers[col]
        self.cameraBounds[0] = self.cameraBounds[0].lerp(self.cameraTriggerVectors[self.targetIndex][0], 0.075)
        self.cameraBounds[1] = self.cameraBounds[1].lerp(self.cameraTriggerVectors[self.targetIndex][1], 0.075)
        
        self.scroll.x = min(self.cameraBounds[1].x-winDim[0], self.scroll.x)
        self.scroll.x = max(self.cameraBounds[0].x, self.scroll.x)
        self.scroll.y = min(self.cameraBounds[1].y-winDim[1], self.scroll.y)
        self.scroll.y = max(self.cameraBounds[0].y, self.scroll.y)
        
    def keydown(self, event):
        self.player.keydown(event)

    def keyup(self, event):
        self.player.keyup(event)