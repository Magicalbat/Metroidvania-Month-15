import pygame
from pygame.math import Vector2

from src.screens.screenmanager import ScreenManager, GameScreen
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.utils.tilemap import Tilemap
from src.utils.camera import Camera
from src.utils.particles import Particles
from src.utils.common import *

class Level(GameScreen):
    def __init__(self, filepath="res/levels/level0.json"):
        tileImgs = loadSpriteSheet("res/temptiles.png", (16,16), (3,1), (1,1), 3, (0,0,0))
        self.tilemap = Tilemap(16, tileImgs)
        extraData = self.tilemap.loadLevel(filepath)

        self.playerSpawn = Vector2(0,0)
        if "PlayerSpawn" in extraData:
            self.playerSpawn = Vector2(extraData["PlayerSpawn"][0][0], extraData["PlayerSpawn"][0][1] - 20)
        cameraTriggerRects = []
        cameraTriggerVectors = []
        if "CameraTriggers" in extraData:
            for i in range(int(len(extraData["CameraTriggers"])/2)):
                p1 = Vector2(extraData["CameraTriggers"][i*2])
                p2 = Vector2(extraData["CameraTriggers"][i*2+1])
                #r = pygame.Rect(p1, p2-p1)
                cameraTriggerRects.append(pygame.Rect(p1, p2-p1))
                cameraTriggerVectors.append((p1, p2))
        self.camera = Camera(cameraTriggerRects, cameraTriggerVectors)
        
        self.levelChangeRects = {}
        i = 0
        while True:
            if f"{i} Level" in extraData:
                if len(extraData[f"{i} Level"]):
                    self.levelChangeRects[i] = pygame.Rect((extraData[f"{i} Level"][0], (16, 16)))
            else:   break
            i += 1

    def setup(self, screenManager):
        super().setup(screenManager)

        self.player = Player(self.playerSpawn, 12, 20)
        self.enemy = Enemy(50,50,12,16)

    def draw(self, win : pygame.Surface):
        self.camera.update(self.player, win.get_size())
        
        self.tilemap.draw(win, self.camera.scroll)
        self.player.draw(win, self.camera.scroll)
        self.enemy.draw(win, self.camera.scroll)

    def update(self, delta):
        self.player.update(delta, self.tilemap)
        self.enemy.update(delta, self.tilemap)

        if self.enemy.rect.colliderect(self.player.rect):
            self.screenManager.reloadCurrentScreen()

        for i, rect in self.levelChangeRects.items():
            if rect.colliderect(self.player.rect):
                self.screenManager.changeScreen(Level(f"res/levels/level{i}.json"))

    def keydown(self, event):
        self.player.keydown(event)

    def keyup(self, event):
        self.player.keyup(event)