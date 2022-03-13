import pygame
from pygame.math import Vector2

from src.utils.common import loadSpriteSheet
from src.entities.enemy import *
from src.entities.boss import Boss

class EnemyManager:
    enemyTypes = {
        "GroundEnemies": GroundEnemy,
        "JumpingEnemies": JumpingEnemy,
        "FlyingEnemies": FlyingEnemy,
        "SlowEnemies": SlowEnemy
    }
    enemyImgs = {
        "GroundEnemies": (9, 12), 
        "JumpingEnemies": (6, 9),
        "FlyingEnemies": (3, 6),
        "SlowEnemies": (0, 3)
    }
    def __init__(self, extraData):
        self.enemySpawns = {}

        for enemyType in ["GroundEnemies", "JumpingEnemies", "FlyingEnemies", "SlowEnemies"]:
            if enemyType in extraData:
                self.enemySpawns[enemyType] = extraData[enemyType]
        
        if "Boss" in extraData:
            self.enemySpawns["Boss"] = extraData["Boss"][0]
        if "BossDamagePoints" in extraData:
            self.bossDamagePoints = extraData["BossDamagePoints"]
        
        self.imgs = loadSpriteSheet("res/imgs/enemies.png", (16,16), (3,4), (1,1), 12, (0,0,0))

    def setup(self):
        self.reset = False
        
        self.boss = None
        self.enemies = []
        for enemyType, positions in self.enemySpawns.items():
            if enemyType != "Boss":
                for pos in positions:
                    self.enemies.append(self.enemyTypes[enemyType](pos, 12, 16, \
                        images=self.imgs[self.enemyImgs[enemyType][0]:self.enemyImgs[enemyType][1]]))
            else:
                self.boss = Boss(positions, 12, 16, images=self.imgs[0:3])

    def draw(self, win, scroll):
        if self.boss is not None:
            self.boss.draw(win, scroll)

        for enemy in self.enemies:
            #if screenRect.colliderect(enemy.rect):
            enemy.draw(win, scroll)

    def update(self, delta, tilemap, player, screenRect):
        if self.boss is not None:
            self.boss.update(delta, tilemap)

            if not player.invincible:
                if player.rect.colliderect(self.boss.rect):
                    self.reset = True

            if player.acid:
                if player.waterParticles.collideRect(self.boss.rect):
                    if not self.boss.damage(1):
                        self.boss = None
                        self.bossDamagePoints = []

        for enemy in self.enemies:
            enemy.onScreen = enemy.rect.colliderect(screenRect)
            enemy.update(delta, player, tilemap)

        for i in range(len(self.enemies))[::-1]:
            if self.enemies[i].onScreen:#screenRect.colliderect(self.enemies[i].rect):
                if player.waterParticles.collideRect(self.enemies[i].rect):
                    if player.acid:
                        if not self.enemies[i].damage(1):
                            self.enemies.pop(i)
                    else:
                        self.enemies[i].stun(1)

        if not player.invincible:
            for enemy in self.enemies:
                if enemy.stunTimer <= 0 and enemy.collide(player.rect):#rect(player.rect):
                    self.reset = True

    def getStunnedRects(self):
        return [enemy.rect for enemy in self.enemies if enemy.stunTimer > 0]