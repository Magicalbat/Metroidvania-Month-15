import pygame
from pygame.math import Vector2

from enum import Enum

from src.entities.enemy import *

class EnemyManager:
    enemyTypes = {
        "GroundEnemies": GroundEnemy,
        "JumpingEnemies": JumpingEnemy,
        "FlyingEnemies": FlyingEnemy
    }
    def __init__(self, extraData):
        self.enemySpawns = {}

        for enemyType in ["GroundEnemies", "JumpingEnemies", "FlyingEnemies"]:
            if enemyType in extraData:
                self.enemySpawns[enemyType] = extraData[enemyType]

    def setup(self):
        self.reset = False
        self.enemies = []
        for enemyType, positions in self.enemySpawns.items():
            for pos in positions:
                self.enemies.append(self.enemyTypes[enemyType](pos, 12, 16))

    def draw(self, win, scroll):
        for enemy in self.enemies:
            #if screenRect.colliderect(enemy.rect):
            enemy.draw(win, scroll)

    def update(self, delta, tilemap, player, screenRect):
        for enemy in self.enemies:
            enemy.onScreen = enemy.rect.colliderect(screenRect)
            enemy.update(delta, player, tilemap)

        for i in range(len(self.enemies))[::-1]:
            if enemy.onScreen:#screenRect.colliderect(self.enemies[i].rect):
                if player.waterParticles.collideRect(self.enemies[i].rect):
                    if player.acid:
                        if not self.enemies[i].damage(1):
                            self.enemies.pop(i)
                    else:
                        self.enemies[i].stun(1)

        for enemy in self.enemies:
            if enemy.stunTimer <= 0 and enemy.collide(player.rect):#rect(player.rect):
                self.reset = True

    def getStunnedRects(self):
        return [enemy.rect for enemy in self.enemies if enemy.stunTimer > 0]