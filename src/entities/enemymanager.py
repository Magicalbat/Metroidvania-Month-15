import pygame
from pygame.math import Vector2

from enum import Enum

from src.entities.enemy import *

class EnemyManager:
    enemyTypes = {
        "GroundEnemies": GroundEnemy
    }
    def __init__(self, extraData):
        self.enemySpawns = {}

        for enemyType in ["GroundEnemies"]:
            if enemyType in extraData:
                self.enemySpawns[enemyType] = extraData[enemyType]

    def setup(self):
        self.reset = False
        self.enemies = []
        for enemyType, positions in self.enemySpawns.items():
            for pos in positions:
                self.enemies.append(self.enemyTypes[enemyType](pos, 12, 16))

    def draw(self, win, scroll, screenRect):
        for enemy in self.enemies:
            if screenRect.colliderect(enemy.rect):
                enemy.draw(win, scroll)

    def update(self, delta, tilemap, player, screenRect):
        for enemy in self.enemies:
            enemy.update(delta, player, tilemap)

        for i in range(len(self.enemies))[::-1]:
            if screenRect.colliderect(self.enemies[i].rect):
                if player.waterParticles.collideRect(self.enemies[i].rect):
                    if player.acid:
                        self.enemies.pop(i)
                    else:
                        self.enemies[i].stun(1)

        for enemy in self.enemies:
            if enemy.stunTimer <= 0 and enemy.rect.colliderect(player.rect):
                self.reset = True

    def getStunnedRects(self):
        return [enemy.rect for enemy in self.enemies if enemy.stunTimer > 0]