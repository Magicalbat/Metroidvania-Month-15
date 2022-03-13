import pygame
from pygame.math import Vector2

import copy

from src.screens.screenmanager import ScreenManager, GameScreen
    
from src.entities.player import Player
from src.entities.enemy import GroundEnemy
from src.entities.enemymanager import EnemyManager

from src.utils.tilemap import Tilemap
from src.utils.camera import Camera
from src.utils.particles import Particles
from src.utils.specialtiles import SpecialTileManager
from src.utils.common import *

class Level(GameScreen):
    def __init__(self, filepath="res/levels/level0.json", player=None):
        tileImgs = loadSpriteSheet("res/imgs/labtiles.png", (16,16), (5,5), (1,1), 25, (0,0,0))
        self.tilemap = Tilemap(16, tileImgs)
        extraData = self.tilemap.loadLevel(filepath)

        self.enemyManager = EnemyManager(extraData)

        self.processExtraData(extraData)

        if player is not None:
            self.player = player
            self.player.pos = self.playerSpawn
            self.player.updateRectPos()

    def setup(self, screenManager):
        super().setup(screenManager)

        if hasattr(self, "player"):
            self.player.vel = Vector2(0, 0)
            self.player.pos = copy.deepcopy(self.playerSpawn)
            self.player.updateRectPos()
            #self.player = Player(self.playerSpawn, 12, 16, images=self.player.imgs, text=self.player.text)
        else:
            self.player = Player(self.playerSpawn, 12, 16)
            self.player.displayText("Left and right to move")
            self.player.displayText("C to jump")

        self.enemyManager.setup()
        self.specialTileManager.setup()

        self.awaitingSpawn = False
        self.awaitingSpawnTimer = 0
        #self.enemies = [GroundEnemy(pos, 12, 16) for pos in self.enemyPositions]

        self.screenRect = pygame.Rect(0,0,0,0)

    def draw(self, win : pygame.Surface):
        self.camera.update(self.player, win.get_size())
        if self.camera.changedTarget:
            self.awaitingSpawn = True
            self.awaitingSpawnTimer = 0.1

        if self.awaitingSpawn and self.awaitingSpawnTimer <= 0 and self.player.collisionDir & 0b0010 > 0:
            self.playerSpawn = copy.deepcopy(self.player.pos)
            self.awaitingSpawn = False

        self.screenRect = pygame.Rect(self.camera.scroll-Vector2(25,25), (win.get_width()+25, win.get_width()+25))
        
        self.tilemap.draw(win, self.camera.scroll)
        #self.tilemap.drawCollision(win, self.camera.scroll)
        self.specialTileManager.draw(win, self.camera.scroll)

        self.enemyManager.draw(win, self.camera.scroll)
        self.player.draw(win, self.camera.scroll)

        #pygame.draw.rect(win, (255,0,0), (self.playerSpawn-self.camera.scroll, (16,16)))

        col = (0,255,0) if self.player.acid else (0,0,255)
        pygame.draw.rect(win, col, (2,2,10,10))

    def update(self, delta):
        self.player.update(delta, self.tilemap, self.enemyManager, self.enemyManager.getStunnedRects()+self.specialTileManager.getColRects())

        self.enemyManager.update(delta, self.tilemap, self.player, self.screenRect, self.playerSpawn)

        self.specialTileManager.update(delta, self.player)

        if self.enemyManager.reset or self.specialTileManager.reset:
            self.screenManager.reloadCurrentScreen()

        if self.awaitingSpawnTimer > 0:
            self.awaitingSpawnTimer -= delta

    def keydown(self, event):
        self.player.keydown(event)
        if event.key == pygame.K_a:
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

        self.specialTileManager = SpecialTileManager(extraData)