import pygame
from pygame.math import Vector2

from src.screens.screenmanager import ScreenManager, GameScreen

from src.entities.player import Player
from src.entities.enemy import GroundEnemy
from src.entities.enemymanager import EnemyManager
from src.entities.firemanager import FireManager

from src.utils.tilemap import Tilemap
from src.utils.camera import Camera
from src.utils.particles import Particles
from src.utils.common import *

class Level(GameScreen):
    def __init__(self, filepath="res/levels/level0.json"):
        tileImgs = loadSpriteSheet("res/temptiles.png", (16,16), (3,1), (1,1), 3, (0,0,0))
        self.tilemap = Tilemap(16, tileImgs)
        extraData = self.tilemap.loadLevel(filepath)

        self.enemyManager = EnemyManager(extraData)

        self.processExtraData(extraData)

    def setup(self, screenManager):
        super().setup(screenManager)

        self.player = Player(self.playerSpawn, 12, 20)
        self.enemyManager.setup()
        #self.enemies = [GroundEnemy(pos, 12, 16) for pos in self.enemyPositions]

        self.screenRect = pygame.Rect(0,0,0,0)

    def draw(self, win : pygame.Surface):
        self.camera.update(self.player, win.get_size())

        self.screenRect = pygame.Rect(self.camera.scroll, win.get_size())
        
        self.tilemap.draw(win, self.camera.scroll)
        
        self.fireManager.draw(win, self.camera.scroll)

        self.player.draw(win, self.camera.scroll)

        self.enemyManager.draw(win, self.camera.scroll, self.screenRect)


    def update(self, delta):
        self.player.update(delta, self.tilemap, self.enemyManager, self.enemyManager.getStunnedRects())

        self.enemyManager.update(delta, self.tilemap, self.player, self.screenRect)

        self.fireManager.update(delta, self.player)

        if self.enemyManager.reset or self.fireManager.reset:
            self.fireManager.reset = False
            self.screenManager.reloadCurrentScreen()

        for i, rect in self.levelChangeRects.items():
            if rect.colliderect(self.player.rect):
                self.screenManager.changeScreen(Level(f"res/levels/level{i}.json"))

    def keydown(self, event):
        self.player.keydown(event)
        if event.key == pygame.K_t:
            self.player.toggleAcid()

    def keyup(self, event):
        self.player.keyup(event)

    def processExtraData(self, extraData):
        self.playerSpawn = Vector2(0,0)
        if "PlayerSpawn" in extraData:
            self.playerSpawn = Vector2(extraData["PlayerSpawn"][0][0], extraData["PlayerSpawn"][0][1] - 16)
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

        self.fireManager = FireManager(extraData["Fire"])

        self.levelChangeRects = {}
        i = 0
        while True:
            if f"{i} Level" in extraData:
                if len(extraData[f"{i} Level"]):
                    self.levelChangeRects[i] = pygame.Rect((extraData[f"{i} Level"][0], (16, 16)))
            else:   break
            i += 1
