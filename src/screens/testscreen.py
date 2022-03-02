import pygame
from pygame.math import Vector2

from src.screens.screenmanager import ScreenManager, GameScreen
from src.entities.player import Player
from src.tilemap import Tilemap
from src.common import *

class TestScreen(GameScreen):
    def __init__(self):
        tileImgs = loadSpriteSheet("res/temptiles.png", (16,16), (3,1), (1,1), 3, (0,0,0))
        self.tilemap = Tilemap(16, tileImgs)
        extraData = self.tilemap.loadLevel("res/levels/testlevel.json")

        self.playerSpawn = Vector2(0,0)
        if "PlayerSpawn" in extraData:
            self.playerSpawn = Vector2(extraData["PlayerSpawn"][0][0], extraData["PlayerSpawn"][0][1] - 20)

    def setup(self, screenManager):
        super().setup(screenManager)

        self.player = Player(self.playerSpawn, 12, 20)

    def draw(self, win):
        self.tilemap.draw(win, Vector2(0, 0))
        self.player.draw(win, Vector2(0, 0))

    def update(self, delta):
        self.player.update(delta, self.tilemap)

    def keydown(self, event):
        self.player.keydown(event)